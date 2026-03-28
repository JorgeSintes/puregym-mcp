FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock LICENSE README.md ./
COPY puregym_mcp ./puregym_mcp

RUN uv sync --frozen --no-dev

EXPOSE 8000

ENTRYPOINT ["uv", "run", "puregym-mcp"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
