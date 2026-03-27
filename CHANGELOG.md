# Changelog

## 0.2.0

- migrate authenticated booking, search, and mutation flows to the discovered `mit.puregym.dk` app API
- keep anonymous mode on the existing public website-backed path
- add center live-status and opening-hours support for authenticated users
- extend MCP tools with `get_center_live_status` and `get_center_open_hours`
- normalize richer authenticated class and booking fields such as capacity and waitlist counts

## 0.1.0

- Initial public release of the PureGym Python client and MCP server
- Local `stdio` MCP support for tools like VS Code and OpenCode
- HTTP transports for self-hosted read-only or authenticated deployments
- Structured PureGym client, schemas, filters, and service layer for downstream reuse
