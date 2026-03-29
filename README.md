# PureGym MCP

`puregym-mcp` is a Python package and Model Context Protocol server for browsing PureGym centers in Denmark,
discovering classes, checking your bookings, and managing bookings from MCP-compatible clients.

This is an independent third-party project and is not affiliated with, endorsed by, or sponsored by PureGym.
PureGym is a registered trademark of Pure Gym Limited.

- Docs: [puregym-mcp.jorgesintes.dev](https://puregym-mcp.jorgesintes.dev)
- Public read-only endpoint: `https://puregym-mcp.jorgesintes.dev/mcp`
- PyPI: [puregym-mcp](https://pypi.org/project/puregym-mcp/)

## Capabilities

The server exposes a small set of tools for public class discovery and optional authenticated booking actions.

### Class discovery

Available without PureGym credentials:

- `get_capabilities`
- `list_class_types`
- `list_centers`
- `search_classes`

### Booking management

Available when `PUREGYM_USERNAME` and `PUREGYM_PASSWORD` are configured:

- `list_my_bookings`
- `book_class`
- `cancel_booking`
- `get_center_live_status` - Real-time occupancy and capacity data
- `get_center_open_hours` - Opening and staffed hours for a center

## Modes

- `Anonymous mode` exposes read-only tools and uses a 14-day search window.
- `Authenticated mode` unlocks booking tools and expands the default search window to 28 days.

## Authentication for HTTP Transports

When running over `streamable-http` or `sse` transports, the server requires Bearer token authentication in
addition to PureGym credentials. This prevents unauthorized access to your booking capabilities when exposing
the MCP server remotely.

**Required environment variables for HTTP transports:**

- `PUREGYM_USERNAME` - Your PureGym account email
- `PUREGYM_PASSWORD` - Your PureGym account password
- `MCP_AUTH_TOKEN` - A secret Bearer token you choose (e.g., a random string)

**Note:** `stdio` transport requires no authentication and runs unauthenticated by default.

Connect from MCP clients (e.g., Mistral) using Simple Auth / HTTP Bearer Token with your `MCP_AUTH_TOKEN`.

## Quickstart

For most users, the easiest setup is local `stdio` usage from an MCP-compatible client:

```json
{
  "mcp": {
    "puregym": {
      "enabled": true,
      "type": "local",
      "command": ["uvx", "puregym-mcp"],
      "environment": {
        "PUREGYM_USERNAME": "your-username",
        "PUREGYM_PASSWORD": "your-password"
      }
    }
  }
}
```

The environment block is optional and only needed for authenticated features.

## Remote Deployment

The server supports both `streamable-http` and `sse` for remote MCP clients.

### Bearer Token Authentication

HTTP transports (`streamable-http`, `sse`) require Bearer token authentication to protect your booking
capabilities:

```bash
export PUREGYM_USERNAME="your-email@example.com"
export PUREGYM_PASSWORD="your-password"
export MCP_AUTH_TOKEN="your-secret-bearer-token"

puregym-mcp --transport streamable-http --host 0.0.0.0 --port 8000 --streamable-http-path /mcp
```

Connect from MCP clients using **Simple Auth** or **HTTP Bearer Token** authentication with your
`MCP_AUTH_TOKEN`.

### Docker Compose Example

```yaml
services:
  puregym-mcp:
    image: puregym-mcp
    environment:
      - PUREGYM_USERNAME=${PUREGYM_USERNAME}
      - PUREGYM_PASSWORD=${PUREGYM_PASSWORD}
      - MCP_AUTH_TOKEN=${MCP_AUTH_TOKEN}
    ports:
      - "8000:8000"
    command:
      - --transport
      - streamable-http
      - --host
      - 0.0.0.0
      - --port
      - "8000"
      - --streamable-http-path
      - /mcp
```

Store sensitive values in a `.env` file (never commit this file):

```env
PUREGYM_USERNAME=your-email@example.com
PUREGYM_PASSWORD=your-password
MCP_AUTH_TOKEN=your-secret-bearer-token-min-16-chars-recommended
```

### Public Read-Only Hosting

- Hosted endpoint: `https://puregym-mcp.jorgesintes.dev/mcp`
- Runs in anonymous mode (no booking capabilities)
- Use this for public class discovery only

## Python Library

The package also exposes a reusable client and service layer:

```python
from puregym_mcp import PureGymClient, PureGymService

# Anonymous client
client = PureGymClient()

# Authenticated client with custom timeout
client = PureGymClient(
    username="your-username",
    password="your-password",
    timeout=30.0  # seconds
)

service = PureGymService(client)

# Book and cancel return typed results
result = await service.book_class(booking_id, activity_id, payment_type)
print(result.participation_id)  # snake_case field

cancel_result = await service.cancel_booking(participation_id)
print(cancel_result.status)
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

Run a private authenticated server (HTTP transport with Bearer token auth):

```bash
docker run --rm -p 8000:8000 \
  -e PUREGYM_USERNAME=your-email \
  -e PUREGYM_PASSWORD=your-password \
  -e MCP_AUTH_TOKEN=your-secret-token \
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
uvx --from dist/puregym_mcp-0.3.0-py3-none-any.whl puregym-mcp --transport stdio
```

Run real API integration tests (requires credentials):

```bash
PUREGYM_USERNAME=your-username PUREGYM_PASSWORD=your-password uv run pytest tests/real_api -m real_api
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
