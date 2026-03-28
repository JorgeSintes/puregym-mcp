# Changelog

## 0.3.0

- **BREAKING**: `book_class` and `cancel_booking` MCP tools now return snake_case field names (`participation_id` instead of `participationId`)
- Add typed response models for book/cancel operations (`BookClassResult`, `CancelBookingResponse`)
- Add API response schemas (`ApiBookClassResponse`, `ApiCancelBookingResponse`) for validation
- Fix schema compatibility: `ApiCenterStats.id` and `ApiCenterSummary.id` are now optional
- Fix schema compatibility: `ApiSearchClass.participation` now accepts both string and object formats
- Add real API integration tests (`tests/real_api`) for live endpoint validation
- Add configurable HTTP timeout to `PureGymClient`

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
