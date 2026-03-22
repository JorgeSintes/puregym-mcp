import os
from typing import Literal

from mcp.server.fastmcp import FastMCP

from puregym_mcp.mcp.tools import register_tools
from puregym_mcp.puregym.client import PureGymClient
from puregym_mcp.puregym.service import PureGymService

Transport = Literal["stdio", "sse", "streamable-http"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def build_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    log_level: LogLevel = "INFO",
    mount_path: str = "/",
    sse_path: str = "/sse",
    message_path: str = "/messages/",
    streamable_http_path: str = "/mcp",
) -> FastMCP:
    client = PureGymClient(
        username=os.getenv("PUREGYM_USERNAME"),
        password=os.getenv("PUREGYM_PASSWORD"),
    )
    service = PureGymService(client)
    mcp = FastMCP(
        "PureGym MCP",
        host=host,
        port=port,
        log_level=log_level,
        mount_path=mount_path,
        sse_path=sse_path,
        message_path=message_path,
        streamable_http_path=streamable_http_path,
    )
    register_tools(mcp, service)
    return mcp


def run_server(
    *,
    transport: Transport = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
    log_level: LogLevel = "INFO",
    mount_path: str = "/",
    sse_path: str = "/sse",
    message_path: str = "/messages/",
    streamable_http_path: str = "/mcp",
) -> None:
    server = build_server(
        host=host,
        port=port,
        log_level=log_level,
        mount_path=mount_path,
        sse_path=sse_path,
        message_path=message_path,
        streamable_http_path=streamable_http_path,
    )
    server.run(transport=transport, mount_path=mount_path)
