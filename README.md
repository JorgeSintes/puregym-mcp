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

Run in authenticated mode by providing credentials:

```bash
PUREGYM_USERNAME="your-email" \
PUREGYM_PASSWORD="your-password" \
uv run puregym-mcp
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
  puregym-mcp
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
  puregym-mcp
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
