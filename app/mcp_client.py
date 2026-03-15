import sys
import asyncio
import json

# Need to ensure we can import from mcp/src
import os
sys.path.insert(0, '/app/mcp/src')
sys.path.insert(0, '/app')

from main import mcp

def get_mcp_tools():
    """Get the list of tools directly from the FastMCP object."""
    try:
        async def fetch_tools():
            return await mcp.list_tools()
            
        tools = asyncio.run(fetch_tools())
        
        # Serialize the schemas correctly
        result = []
        for t in tools:
            # Pydantic schemas usually have a .model_dump() or dict() method
            schema_dict = {}
            if hasattr(t, "inputSchema"):
                try:
                    schema_dict = t.inputSchema.model_dump()
                except AttributeError:
                    schema_dict = dict(t.inputSchema)
            
            result.append({
                "name": t.name,
                "description": t.description,
                "schema": schema_dict
            })
            
        return result
    except Exception as e:
        print(f"Error loading tools from MCP: {e}")
        return None

def call_mcp_tool(name: str, args: dict):
    """Call a specific MCP tool with arguments."""
    try:
        async def call_tool():
            # FastMCP call_tool expects arguments as a dictionary
            return await mcp.call_tool(name, args)
            
        result = asyncio.run(call_tool())
        
        # Format the result correctly based on FastMCP structure
        formatted_result = []
        for content in result:
            if hasattr(content, "text"):
                formatted_result.append(content.text)
            else:
                formatted_result.append(str(content))
                
        return {"success": True, "result": "\n".join(formatted_result)}
    except Exception as e:
        print(f"Error calling MCP tool '{name}': {e}")
        return {"success": False, "error": str(e)}

