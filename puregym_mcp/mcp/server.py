import os
from typing import Literal

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

from puregym_mcp.mcp.auth import StaticTokenVerifier
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
    transport: Transport = "stdio",
) -> FastMCP:
    client = PureGymClient(
        username=os.getenv("PUREGYM_USERNAME"),
        password=os.getenv("PUREGYM_PASSWORD"),
    )
    service = PureGymService(client)

    # Build token verifier for HTTP transports (Simple Auth with static Bearer token)
    token_verifier = None
    auth = None
    if transport in ("sse", "streamable-http") and client.has_credentials:
        mcp_token = os.getenv("MCP_AUTH_TOKEN")
        if mcp_token is None:
            raise ValueError("MCP_AUTH_TOKEN environment variable is required for authenticated transports")
        token_verifier = StaticTokenVerifier(mcp_token)
        # Minimal AuthSettings required by FastMCP when using token_verifier
        auth = AuthSettings(
            issuer_url=AnyHttpUrl("http://localhost:8000"),
            resource_server_url=AnyHttpUrl("http://localhost:8000"),
        )

    mcp = FastMCP(
        "PureGym MCP",
        host=host,
        port=port,
        log_level=log_level,
        mount_path=mount_path,
        sse_path=sse_path,
        message_path=message_path,
        streamable_http_path=streamable_http_path,
        token_verifier=token_verifier,
        auth=auth,
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
        transport=transport,
    )
    server.run(transport=transport, mount_path=mount_path)
