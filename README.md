# PureGym MCP

`puregym-mcp` is a Python package that exposes PureGym data as an MCP server and a reusable client library.

It supports two main modes:

- anonymous read-only access for class discovery
- authenticated access for your bookings, booking creation, and cancellation

## Install

Try it once without installing:

```bash
uvx puregym-mcp --transport stdio
```

Install it for regular use:

```bash
uv tool install puregym-mcp
```

Or install it as a normal Python package:

```bash
pip install puregym-mcp
```

## Quickstart

Run locally over stdio:

```bash
puregym-mcp --transport stdio
```

Run in authenticated mode by providing your own PureGym credentials:

```bash
PUREGYM_USERNAME="your-email" \
PUREGYM_PASSWORD="your-password" \
puregym-mcp --transport stdio
```

## MCP Client Config

OpenCode:

```json
{
  "mcpServers": {
    "puregym": {
      "command": "puregym-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

Authenticated OpenCode:

```json
{
  "mcpServers": {
    "puregym": {
      "command": "puregym-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "PUREGYM_USERNAME": "your-email",
        "PUREGYM_PASSWORD": "your-password"
      }
    }
  }
}
```

VS Code user or workspace `mcp.json`:

```json
{
  "servers": {
    "puregym": {
      "type": "stdio",
      "command": "puregym-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

## Modes

- Anonymous mode
  - enabled when `PUREGYM_USERNAME` and `PUREGYM_PASSWORD` are not set
  - exposes read-only tools
  - defaults to a 14-day search window
- Authenticated mode
  - enabled automatically when both PureGym credentials are set
  - also exposes booking management tools
  - defaults to a 28-day search window

## Exposed Tools

- Always available
  - `get_capabilities`
  - `list_class_types`
  - `list_centers`
  - `search_classes`
- Authenticated only
  - `list_my_bookings`
  - `book_class`
  - `cancel_booking`

## HTTP Hosting

For remote MCP clients that connect by URL, run the server with an HTTP transport:

```bash
puregym-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

By default the streamable HTTP endpoint is exposed at `http://127.0.0.1:8000/mcp`.

SSE is also supported when a client requires it:

```bash
puregym-mcp --transport sse --host 127.0.0.1 --port 8000
```

When deploying publicly:

- prefer `streamable-http` unless your client only supports SSE
- put the service behind HTTPS and a reverse proxy
- keep authenticated mode private, since it exposes booking mutations for your account
- use anonymous mode for public read-only hosting

## Python Library

The package also exposes a reusable client and service layer:

```python
from puregym_mcp import PureGymClient, PureGymService

client = PureGymClient()
service = PureGymService(client)
```

## Docker

Build the image:

```bash
docker build -t puregym-mcp .
```

Run a public read-only server:

```bash
docker run --rm -p 8000:8000 puregym-mcp
```

Run a private authenticated server:

```bash
docker run --rm -p 8000:8000 \
  -e PUREGYM_USERNAME=your-email \
  -e PUREGYM_PASSWORD=your-password \
  puregym-mcp
```

Override the default container transport or path when needed:

```bash
docker run --rm -p 8000:8000 puregym-mcp \
  --transport sse \
  --host 0.0.0.0 \
  --port 8000 \
  --sse-path /sse
```

## Development

Clone the repo and install dev dependencies:

```bash
uv sync --dev
```

Run from source:

```bash
uv run puregym-mcp --transport stdio
```

Run checks:

```bash
uv run pytest
uv run python -m compileall puregym_mcp tests
uv build
```

Test the built package locally before publishing:

```bash
uvx --from dist/puregym_mcp-0.1.0-py3-none-any.whl puregym-mcp --transport stdio
```

## MCP Inspector

Launch the Inspector against this repo:

```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory /path/to/puregym-mcp \
  run \
  puregym-mcp --transport stdio
```

Launch it in authenticated mode:

```bash
npx @modelcontextprotocol/inspector \
  -e PUREGYM_USERNAME=your-email \
  -e PUREGYM_PASSWORD=your-password \
  -- \
  uv \
  --directory /path/to/puregym-mcp \
  run \
  puregym-mcp --transport stdio
```

The Inspector UI opens at `http://localhost:6274`.
