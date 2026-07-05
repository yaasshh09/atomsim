import atomsim.cli as cli


def test_parser_defaults():
    args = cli.build_parser().parse_args(["serve"])
    assert args.command == "serve"
    assert args.port == 8000
    assert args.no_browser is False


def test_serve_invokes_uvicorn_on_loopback(monkeypatch):
    captured = {}

    def fake_run(app, host, port):
        captured["host"] = host
        captured["port"] = port

    opened = []
    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setattr(cli, "_open_browser_soon", lambda url: opened.append(url))

    cli.main(["serve", "--port", "8123"])
    assert captured == {"host": "127.0.0.1", "port": 8123}
    assert opened == ["http://127.0.0.1:8123"]


def test_no_browser_flag(monkeypatch):
    monkeypatch.setattr(cli.uvicorn, "run", lambda app, host, port: None)
    opened = []
    monkeypatch.setattr(cli, "_open_browser_soon", lambda url: opened.append(url))
    cli.main(["serve", "--no-browser"])
    assert opened == []
