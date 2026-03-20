import os

from mcp.server.fastmcp import FastMCP

from puregym_mcp.mcp.tools import register_tools
from puregym_mcp.puregym.client import PureGymClient
from puregym_mcp.puregym.service import PureGymService


def build_server() -> FastMCP:
    client = PureGymClient(
        username=os.getenv("PUREGYM_USERNAME"),
        password=os.getenv("PUREGYM_PASSWORD"),
    )
    service = PureGymService(client)
    mcp = FastMCP("PureGym MCP")
    register_tools(mcp, service)
    return mcp


def main() -> None:
    build_server().run()
