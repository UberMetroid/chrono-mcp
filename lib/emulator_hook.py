import asyncio
import json
import logging
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EmulatorHookServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        self.host = host
        self.port = port
        self.active_connections = set()
        self.live_state: Dict[str, Any] = {
            "connected": False,
            "emulator": "None",
            "game": "Unknown",
            "ram": {}
        }
        self._loop = None
        self._thread = None
        
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming raw TCP connections from Emulators."""
        addr = writer.get_extra_info('peername')
        self.active_connections.add(writer)
        logger.info(f"Emulator connected from {addr}")
        self.live_state["connected"] = True
        
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                    
                try:
                    message = data.decode('utf-8').strip()
                    if not message:
                        continue
                        
                    msg_data = json.loads(message)
                    
                    # Handle different message types
                    msg_type = msg_data.get("type", "update")
                    
                    if msg_type == "handshake":
                        self.live_state["emulator"] = msg_data.get("emulator", "Unknown")
                        self.live_state["game"] = msg_data.get("game", "Unknown")
                        logger.info(f"Handshake complete: {self.live_state['emulator']} running {self.live_state['game']}")
                        
                    elif msg_type == "ram_update":
                        # Merge the new RAM values into our live state
                        ram_data = msg_data.get("ram", {})
                        for address, value in ram_data.items():
                            self.live_state["ram"][str(address)] = value
                            
                    elif msg_type == "state_dump":
                        # Completely replace the state
                        self.live_state["state"] = msg_data.get("state", {})
                        
                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON from emulator: {data[:50]}...")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Emulator connection error: {e}")
        finally:
            logger.info(f"Emulator connection closed from {addr}")
            self.active_connections.remove(writer)
            writer.close()
            await writer.wait_closed()
            if not self.active_connections:
                self.live_state["connected"] = False
                
    async def request_read(self, address: int, length: int) -> Optional[list]:
        """Send a request to the emulator to read specific memory."""
        if not self.active_connections:
            return None
            
        req = {
            "action": "read",
            "address": address,
            "length": length
        }
        
        writer = next(iter(self.active_connections))
        try:
            req_str = json.dumps(req) + "\\n"
            writer.write(req_str.encode('utf-8'))
            await writer.drain()
            
            # Since we're reading asynchronously in handle_client, 
            # returning a synchronous response here requires a callback or future map.
            # For simplicity in this demo, we assume the client pushes updates continually.
            return [] 
        except Exception as e:
            logger.error(f"Failed to request read from emulator: {e}")
            
        return None
        
    async def request_write(self, address: int, data: list) -> bool:
        """Send a request to the emulator to write specific memory."""
        if not self.active_connections:
            return False
            
        req = {
            "action": "write",
            "address": address,
            "data": data
        }
        
        writer = next(iter(self.active_connections))
        try:
            req_str = json.dumps(req) + "\\n"
            writer.write(req_str.encode('utf-8'))
            await writer.drain()
            return True
        except Exception as e:
            logger.error(f"Failed to write to emulator: {e}")
            return False

    def start_server(self):
        """Start the TCP server in a new event loop/thread."""
        async def run_server():
            server = await asyncio.start_server(self.handle_client, self.host, self.port)
            async with server:
                await server.serve_forever()

        def thread_target():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(run_server())

        self._thread = threading.Thread(target=thread_target, daemon=True)
        self._thread.start()
        logger.info(f"Emulator Hook TCP server started on {self.host}:{self.port}")

# Global instance
hook_server = EmulatorHookServer()

def get_emulator_state() -> Dict[str, Any]:
    """Get the current live state from connected emulators."""
    return hook_server.live_state

def read_emulator_ram(address: int, length: int) -> Optional[list]:
    """Blocking wrapper to read RAM from emulator."""
    if not hook_server._loop or not hook_server.live_state["connected"]:
        return None
    future = asyncio.run_coroutine_threadsafe(hook_server.request_read(address, length), hook_server._loop)
    return future.result()

def write_emulator_ram(address: int, data: list) -> bool:
    """Blocking wrapper to write RAM to emulator."""
    if not hook_server._loop or not hook_server.live_state["connected"]:
        return False
    future = asyncio.run_coroutine_threadsafe(hook_server.request_write(address, data), hook_server._loop)
    return future.result()
