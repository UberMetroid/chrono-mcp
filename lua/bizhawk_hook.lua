-- BizHawk Emulator Hook for Chrono MCP (Raw TCP)
-- Run this script inside BizHawk's Lua Console.

local socket = require("socket")

local host = "127.0.0.1"
local port = 8081
local tcp = socket.tcp()

print("Connecting to Chrono MCP Server on " .. host .. ":" .. port .. "...")
tcp:settimeout(0)

local connected = false
local connect_timer = 0

-- Simple JSON encoder
local function encode_json(t)
    if type(t) == "table" then
        local s = "{"
        local first = true
        for k, v in pairs(t) do
            if not first then s = s .. ", " end
            first = false
            s = s .. '"' .. tostring(k) .. '": ' .. encode_json(v)
        end
        return s .. "}"
    elseif type(t) == "string" then
        return '"' .. t .. '"'
    elseif type(t) == "number" or type(t) == "boolean" then
        return tostring(t)
    else
        return "null"
    end
end

-- Try to connect
function attempt_connection()
    local res, err = tcp:connect(host, port)
    if res or err == "already connected" then
        print("Connected to MCP!")
        connected = true
        
        -- Send Handshake
        local handshake = encode_json({
            type = "handshake",
            emulator = "BizHawk",
            game = gameinfo.getromname() or "Unknown"
        }) .. "\\n"
        
        tcp:send(handshake)
    else
        connected = false
    end
end

attempt_connection()

-- Main loop
while true do
    if not connected then
        connect_timer = connect_timer + 1
        if connect_timer > 300 then -- Try every 5 seconds (assuming 60fps)
            attempt_connection()
            connect_timer = 0
        end
    else
        -- Read Data from server (Command processing)
        local msg, status, partial = tcp:receive("*l")
        
        if status == "closed" then
            print("Disconnected from MCP Server")
            connected = false
            tcp = socket.tcp()
            tcp:settimeout(0)
        else
            -- We could process incoming requests here (e.g. write to RAM)
            if msg and msg ~= "" then
                print("Received command: " .. msg)
            end
            
            -- Push live state every frame (or every N frames)
            -- For example, Chrono Trigger Party HP (assuming SNES)
            -- Memory domain depends on the core (e.g., WRAM)
            local hp_address = "0x7E0000"
            local val = 0
            
            -- Safety try-catch for reading memory
            pcall(function()
                val = memory.readbyte(0x7E0000)
            end)
            
            local state = encode_json({
                type = "ram_update",
                ram = {
                    [hp_address] = val
                }
            }) .. "\\n"
            
            local s, err = tcp:send(state)
            if err == "closed" then
                connected = false
                tcp = socket.tcp()
                tcp:settimeout(0)
            end
        end
    end
    
    emu.frameadvance()
end
