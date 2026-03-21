# AGENTS

## Repo Overview

- This repo contains the publishable PureGym client library and MCP server package.
- It is designed to work in two modes:
  - Anonymous read-only mode when credentials are absent.
  - Authenticated self-hosted mode when `PUREGYM_USERNAME` and `PUREGYM_PASSWORD` are set.
- The Telegram bot lives in a separate `puregym-bot` repo and depends on this package.

## Main Architecture

- `puregym_mcp/puregym/client.py`
  - Low-level PureGym HTTP client and login/session handling.
  - Supports anonymous mode when credentials are absent and authenticated mode when env credentials are present.
- `puregym_mcp/puregym/service.py`
  - Reusable service layer used by both MCP tools and the bot.
  - Owns default search windows: 14 days anonymous, 28 days authenticated.
- `puregym_mcp/puregym/schemas.py`
  - Structured PureGym models.
  - Includes derived fields like `is_booked`, `is_waitlisted`, `waitlist_position`, and `waitlist_size`.
- `puregym_mcp/puregym/filters.py`
  - Shared class filtering helpers used by consumers like the bot.
- `puregym_mcp/mcp/server.py`
  - MCP server bootstrap.
- `puregym_mcp/mcp/tools.py`
  - MCP tool registration.
  - Always exposes read-only tools; exposes mutation tools only in authenticated mode.
- `puregym_mcp/mcp/capabilities.py`
  - Declares which tool capabilities are available in the current mode.

## Important Domain Rules

- Keep this repo focused on structured PureGym domain logic and MCP exposure.
- Do not add Telegram formatting or bot-specific interaction logic here.
- `puregym-mcp` has two intended modes:
  - Anonymous/read-only mode for hosted or public use.
  - Authenticated mode for self-hosted use via `PUREGYM_USERNAME` and `PUREGYM_PASSWORD` env vars.
- Do not design for hosted authenticated MCP. That is intentionally out of scope.
- MCP tool outputs should stay structured and derived, not chat-formatted.

## Workflow Rules For Future Changes

- Always use `uv` for project commands.
- Prefer:
  - `uv sync --dev`
  - `uv run pytest`
  - `uv run python -m compileall puregym_mcp tests`
  - `uv run puregym-mcp`
  - `uv add ...` / `uv sync` when dependency changes are needed
- Do not use plain `python`, `pip`, or ad-hoc environment commands when `uv` can do the job.

## Testing Expectations

- After implementing any non-trivial change, always run the tests.
- If tests fail, do not stop with the repo in a failing state unless the user explicitly asks for that.
- Keep working until the tests pass again.
- If behavior changes, update or add tests to reflect the intended behavior.
- Tests live in `tests/` for client, service, schema, and MCP coverage.

## Practical Notes

- Keep MCP tool handlers thin and put business logic in `puregym_mcp/puregym/service.py`.
- Preserve the current package boundary so downstream consumers like `puregym-bot` can reuse the client, filters, schemas, and service layer.
- Be careful when changing defaults in the service layer because both direct MCP consumers and the bot may rely on them.

## Good Validation Commands

- `uv sync --dev`
- `uv run pytest`
- `uv run python -m compileall puregym_mcp tests`
- `uv run puregym-mcp`
