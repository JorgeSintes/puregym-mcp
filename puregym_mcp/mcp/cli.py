import argparse
from collections.abc import Sequence
from typing import cast

from puregym_mcp.mcp.server import LogLevel, Transport, run_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="puregym-mcp",
        description="Run the PureGym MCP server over stdio or HTTP transports.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default="stdio",
        help="MCP transport to run.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP bind host for SSE or streamable HTTP transports.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP bind port for SSE or streamable HTTP transports.",
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="INFO",
        help="Server log level.",
    )
    parser.add_argument(
        "--mount-path",
        default="/",
        help="Root mount path for the HTTP app, mainly useful for SSE deployments.",
    )
    parser.add_argument(
        "--sse-path",
        default="/sse",
        help="SSE handshake path when using the SSE transport.",
    )
    parser.add_argument(
        "--message-path",
        default="/messages/",
        help="SSE message POST path when using the SSE transport.",
    )
    parser.add_argument(
        "--streamable-http-path",
        default="/mcp",
        help="Path to expose when using the streamable HTTP transport.",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    run_server(
        transport=cast(Transport, args.transport),
        host=args.host,
        port=args.port,
        log_level=cast(LogLevel, args.log_level),
        mount_path=args.mount_path,
        sse_path=args.sse_path,
        message_path=args.message_path,
        streamable_http_path=args.streamable_http_path,
    )
