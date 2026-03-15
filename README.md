# Chrono Series MCP Server & Web UI

[![Docker CI/CD](https://github.com/UberMetroid/chrono-mcp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/UberMetroid/chrono-mcp/actions/workflows/docker-publish.yml)

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server and Flask-based Web UI for analyzing the *Chrono* series ROMs (*Chrono Trigger*, *Chrono Cross*, and *Radical Dreamers*).

## 🚀 Features

- **Web UI (Port 5000)**: Browse, search, and export extracted game data.
- **MCP Server (Port 8080)**: 62 specialized tools for AI/LLM integration (Claude, Cursor, etc.).
- **Live Emulator Hook**: Real-time memory analysis via BizHawk (TCP Port 8081).
- **Comprehensive Database**: Over 21,000 items extracted across all major versions and fan hacks.
- **Automated Deployment**: Pre-built Docker images hosted on GitHub Container Registry (GHCR).

## 📊 Available Games & Data

| Game | Total Items | Categories | Highlights |
|------|-------------|------------|------------|
| **Chrono Trigger** | 9,975 | 31 | SNES, DS, PS1, MSU1, Fan Hacks |
| **Chrono Cross** | 7,623 | 21 | Disc 1 & 2, TIM Images, Credits |
| **Radical Dreamers** | 4,099 | 11 | Translation patches, Dialog |

**Total: 21,697 items across 63 categories**

## 🛠️ Quick Start

### Using Docker (Recommended)

The easiest way to get started is by pulling the pre-built image from GHCR:

```bash
# Pull the latest image
docker pull ghcr.io/ubermetroid/chrono-mcp:latest

# Run the full stack (Web UI + MCP + Emulator Hook)
docker run -d \
  -p 5000:5000 \
  -p 8080:8080 \
  -p 8081:8081 \
  --name chrono-mcp \
  ghcr.io/ubermetroid/chrono-mcp:latest
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/UberMetroid/chrono-mcp.git
cd chrono-mcp

# Build and run with Docker Compose
docker-compose up -d
```

## 🤖 MCP Tools

The server provides **62 tools** for deep ROM analysis, including:

- **Game Info**: `list_games`, `get_game_info`, `get_database_summary`
- **Text Analysis**: `search_dialog_text`, `find_text`, `decode_game_text`
- **Technical Tools**: `decompress_rom_data` (LZSS), `disassemble_bytes`, `generate_ips_patch`
- **Media**: `list_game_art`, `get_game_art_metadata`, `get_audio_data_info`
- **Live Data**: `get_live_emulator_state` (requires BizHawk hook)

## 🌐 Web UI & API

Once running, access the services at:
- **Web UI**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/api/health`
- **MCP Status**: `http://localhost:8080/mcp` (requires MCP client)

## 🎮 Emulator Integration

1. Download the `chrono_mcp_hook.lua` script from the Web UI (**API & Tools** section).
2. Open **BizHawk** and load a Chrono series ROM.
3. Open the **Lua Console** and run the downloaded script.
4. The MCP server will now have access to live RAM state via the `get_live_emulator_state` tool.

## 📖 Documentation

- [Self-Hosting Guide](docs/SELF_HOSTING.md)
- [Knowledge Base](docs/KNOWLEDGE.md)

## ⚖️ License

This project is for educational and research purposes only. ROM files are not included.
