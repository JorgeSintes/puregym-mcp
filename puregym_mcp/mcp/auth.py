from mcp.server.auth.provider import AccessToken


class StaticTokenVerifier:
    def __init__(self, token: str | None) -> None:
        self.token = token

    async def verify_token(self, token: str) -> AccessToken | None:
        if self.token is None or token != self.token:
            return None
        return AccessToken(
            token=token,
            client_id="self",
            scopes=["puregym"],
        )
