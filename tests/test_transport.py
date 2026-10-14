"""The HTTP transports accept requests addressed to localhost or to ALLOWED_HOSTS only."""
import pathlib
import sys

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}},
}


@pytest.fixture
def main_module(monkeypatch):
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    for name in ("INVESTEC_CLIENT_ID", "INVESTEC_CLIENT_SECRET", "INVESTEC_API_KEY"):
        monkeypatch.setenv(name, "dummy")  # the server's lifespan builds the client
    import main

    return main


def status_for(main_module, host_header):
    app = main_module.mcp.streamable_http_app(host="127.0.0.1", transport_security=main_module.transport_security())
    with TestClient(app, base_url=f"http://{host_header}") as client:
        response = client.post("/mcp", json=INITIALIZE, headers={"Accept": "application/json, text/event-stream"})
    return response.status_code


def test_only_localhost_by_default(main_module, monkeypatch):
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    assert status_for(main_module, "localhost:8050") == 200
    assert status_for(main_module, "pi.example.ts.net") == 421


def test_allowed_hosts_are_accepted(main_module, monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "pi.example.ts.net, other.example")
    assert status_for(main_module, "pi.example.ts.net") == 200
    assert status_for(main_module, "localhost:8050") == 200
    assert status_for(main_module, "evil.example") == 421
