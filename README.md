# PureGym MCP

PureGym client library and MCP server.

## Setup

Install dependencies:

```bash
uv sync --dev
```

## What it provides

- PureGym client and structured schemas with derived fields like waitlist position
- MCP tools for listing class types, centers, and searching classes
- Optional authenticated mode for listing bookings, booking classes, and cancelling bookings

## Modes

- Anonymous mode
  - enabled when `PUREGYM_USERNAME` and `PUREGYM_PASSWORD` are not set
  - read-only tools only
  - default search window is 14 days ahead
- Authenticated mode
  - enabled automatically when both `PUREGYM_USERNAME` and `PUREGYM_PASSWORD` are set
  - booking management tools are also available
  - default search window is 28 days ahead

## Running locally

```bash
uv run puregym-mcp
```

Pick a transport explicitly when needed:

```bash
uv run puregym-mcp --transport stdio
uv run puregym-mcp --transport streamable-http --host 127.0.0.1 --port 8000
uv run puregym-mcp --transport sse --host 127.0.0.1 --port 8000
```

Useful HTTP options:

```bash
uv run puregym-mcp \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8000 \
  --streamable-http-path /mcp
```

Run in authenticated mode by providing credentials:

```bash
PUREGYM_USERNAME="your-email" \
PUREGYM_PASSWORD="your-password" \
uv run puregym-mcp
```

Authenticated HTTP example for private self-hosting:

```bash
PUREGYM_USERNAME="your-email" \
PUREGYM_PASSWORD="your-password" \
uv run puregym-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

## Test

```bash
uv run pytest
uv run python -m compileall puregym_mcp tests
```

## Debug with MCP Inspector

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

The Inspector UI opens at `http://localhost:6274`. Useful checks are `get_capabilities`, `search_classes`, and, in authenticated mode, `list_my_bookings`, `book_class`, and `cancel_booking`.

Keep the Inspector bound to localhost and leave its auth enabled.

## Example MCP client config

Claude Desktop:

```json
{
  "mcpServers": {
    "puregym": {
      "command": "uv",
      "args": ["run", "puregym-mcp"],
      "cwd": "/path/to/this/repo"
    }
  }
}
```

Authenticated Claude Desktop example:

```json
{
  "mcpServers": {
    "puregym": {
      "command": "uv",
      "args": ["run", "puregym-mcp"],
      "cwd": "/path/to/this/repo",
      "env": {
        "PUREGYM_USERNAME": "your-email",
        "PUREGYM_PASSWORD": "your-password"
      }
    }
  }
}
```

OpenCode example:

```json
{
  "mcpServers": {
    "puregym": {
      "command": "uv",
      "args": ["run", "puregym-mcp"],
      "cwd": "/path/to/this/repo"
    }
  }
}
```

## Hosting over HTTP

For remote MCP clients that connect by URL, run the server with an HTTP transport:

```bash
uv run puregym-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

By default the streamable HTTP endpoint is exposed at `http://127.0.0.1:8000/mcp`.

SSE is also supported if a client specifically requires it:

```bash
uv run puregym-mcp --transport sse --host 127.0.0.1 --port 8000
```

When deploying publicly:

- prefer `streamable-http` unless your client only supports SSE
- put the service behind HTTPS and a reverse proxy
- keep authenticated mode private, since it exposes booking mutations for your account
- use anonymous mode for public read-only hosting

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

## Exposed tools

- Always available:
  - `get_capabilities`
  - `list_class_types`
  - `list_centers`
  - `search_classes`
- Authenticated only:
  - `list_my_bookings`
  - `book_class`
  - `cancel_booking`
