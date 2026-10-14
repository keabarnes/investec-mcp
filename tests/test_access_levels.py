"""The server must never do more than its configured access level allows."""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from access import SCOPES, AccessLevel, access_level_from_env  # noqa: E402
from tools import register_all_tools  # noqa: E402
from utils import InvestecClient, get_investec_api_client  # noqa: E402

MONEY_TOOLS = {
    AccessLevel.READ: set(),
    AccessLevel.TRANSFERS: {"transfer_money", "transfer_multiple"},
    AccessLevel.PAYMENTS: {"transfer_money", "transfer_multiple", "pay_beneficiary", "pay_multiple"},
}


class ToolRecorder:
    """Stands in for the MCP server and records which tools get registered."""

    def __init__(self):
        self.names = set()

    def tool(self, *args, **kwargs):
        def register(fn):
            self.names.add(fn.__name__)
            return fn

        return register


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class FakeAsyncClient:
    """Stands in for httpx.AsyncClient and records requests that would reach the API."""

    requests = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, **kwargs):  # token request
        return FakeResponse({"access_token": "token", "expires_in": 1800})

    async def request(self, method, url, **kwargs):
        FakeAsyncClient.requests.append((method, url))
        return FakeResponse({})


@pytest.fixture
def api_requests(monkeypatch):
    FakeAsyncClient.requests = []
    monkeypatch.setattr("utils.httpx.AsyncClient", FakeAsyncClient)
    return FakeAsyncClient.requests


@pytest.mark.parametrize("level", list(AccessLevel))
async def test_registered_tools_match_level(level):
    recorder = ToolRecorder()
    await register_all_tools(recorder, level)
    assert "get_accounts" in recorder.names
    assert recorder.names & MONEY_TOOLS[AccessLevel.PAYMENTS] == MONEY_TOOLS[level]


@pytest.mark.parametrize("level", list(AccessLevel))
def test_requested_scopes_match_level(level):
    scopes = SCOPES[level].split()
    assert ("transfers" in scopes) == (level >= AccessLevel.TRANSFERS)
    assert ("beneficiarypayments" in scopes) == (level >= AccessLevel.PAYMENTS)


def test_default_level_keeps_existing_behaviour(monkeypatch):
    monkeypatch.delenv("INVESTEC_ACCESS_LEVEL", raising=False)
    assert access_level_from_env() is AccessLevel.PAYMENTS


@pytest.mark.parametrize("value", ["", "base", "everything"])
def test_unknown_level_fails(monkeypatch, value):
    monkeypatch.setenv("INVESTEC_ACCESS_LEVEL", value)
    with pytest.raises(ValueError):
        access_level_from_env()


def test_client_uses_level_from_env(monkeypatch):
    for name in ("INVESTEC_CLIENT_ID", "INVESTEC_CLIENT_SECRET", "INVESTEC_API_KEY"):
        monkeypatch.setenv(name, "dummy")
    monkeypatch.setenv("INVESTEC_ACCESS_LEVEL", "read")
    client = get_investec_api_client()
    assert client.access_level is AccessLevel.READ
    assert client.scope == SCOPES[AccessLevel.READ]


CALLS = {
    "read": lambda client: client.get_accounts(),
    "transfer": lambda client: client.transfer_money("from", "to", 1.0, "ref"),
    "payment": lambda client: client.pay_beneficiary("account", "beneficiary", 1.0, "ref"),
    "other write": lambda client: client._make_request("DELETE", "/accounts/a/something"),
}


@pytest.mark.parametrize(
    "level, call, allowed",
    [
        (AccessLevel.READ, "read", True),
        (AccessLevel.READ, "transfer", False),
        (AccessLevel.TRANSFERS, "transfer", True),
        (AccessLevel.TRANSFERS, "payment", False),
        (AccessLevel.TRANSFERS, "other write", False),
        (AccessLevel.PAYMENTS, "payment", True),
    ],
)
async def test_client_enforces_level(api_requests, level, call, allowed):
    client = InvestecClient("id", "secret", "key", level)
    if allowed:
        await CALLS[call](client)
        assert len(api_requests) == 1
    else:
        with pytest.raises(PermissionError):
            await CALLS[call](client)
        assert api_requests == []
