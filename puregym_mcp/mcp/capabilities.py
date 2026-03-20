from dataclasses import dataclass
import os


@dataclass(frozen=True)
class McpCapabilities:
    authenticated: bool
    search_days_allowed: int


def get_capabilities() -> McpCapabilities:
    username = os.getenv("PUREGYM_USERNAME")
    password = os.getenv("PUREGYM_PASSWORD")
    authenticated = bool(username and password)
    return McpCapabilities(authenticated=authenticated, search_days_allowed=28 if authenticated else 14)
