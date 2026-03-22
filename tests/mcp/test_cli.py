from puregym_mcp.mcp import cli


def test_parse_args_defaults_to_stdio():
    args = cli.parse_args([])

    assert args.transport == "stdio"
    assert args.host == "127.0.0.1"
    assert args.port == 8000
    assert args.log_level == "INFO"
    assert args.mount_path == "/"
    assert args.sse_path == "/sse"
    assert args.message_path == "/messages/"
    assert args.streamable_http_path == "/mcp"


def test_parse_args_supports_http_transports():
    args = cli.parse_args(
        [
            "--transport",
            "streamable-http",
            "--host",
            "0.0.0.0",
            "--port",
            "9000",
            "--log-level",
            "DEBUG",
            "--mount-path",
            "/gym",
            "--sse-path",
            "/events",
            "--message-path",
            "/messages",
            "--streamable-http-path",
            "/api/mcp",
        ]
    )

    assert args.transport == "streamable-http"
    assert args.host == "0.0.0.0"
    assert args.port == 9000
    assert args.log_level == "DEBUG"
    assert args.mount_path == "/gym"
    assert args.sse_path == "/events"
    assert args.message_path == "/messages"
    assert args.streamable_http_path == "/api/mcp"


def test_main_runs_selected_transport(monkeypatch):
    captured = {}

    def fake_run_server(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(cli, "run_server", fake_run_server)

    cli.main(["--transport", "sse", "--host", "0.0.0.0", "--port", "8123"])

    assert captured == {
        "transport": "sse",
        "host": "0.0.0.0",
        "port": 8123,
        "log_level": "INFO",
        "mount_path": "/",
        "sse_path": "/sse",
        "message_path": "/messages/",
        "streamable_http_path": "/mcp",
    }
