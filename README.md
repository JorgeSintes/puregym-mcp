# PureGym MCP

PureGym client library and MCP server.

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

From the workspace root:

```bash
uv run --package puregym-mcp puregym-mcp
```

Run in authenticated mode by providing credentials:

```bash
PUREGYM_USERNAME="your-email" \
PUREGYM_PASSWORD="your-password" \
uv run --package puregym-mcp puregym-mcp
```

## Example MCP client config

Claude Desktop:

```json
{
  "mcpServers": {
    "puregym": {
      "command": "uv",
      "args": ["run", "--package", "puregym-mcp", "puregym-mcp"],
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
      "args": ["run", "--package", "puregym-mcp", "puregym-mcp"],
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
      "args": ["run", "--package", "puregym-mcp", "puregym-mcp"],
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
