"""
MCP server for integrating Investec Banking API into AI agents.
"""
from mcp.server.mcpserver import MCPServer, Context
from mcp.server.transport_security import TransportSecuritySettings
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import os

from utils import get_investec_api_client
from tools import register_all_tools

load_dotenv()

# Create a dataclass for our application context
@dataclass
class InvestecContext:
    """Context for the Investec API MCP server."""
    investec_client: object  # Will be replaced with actual client type

@asynccontextmanager
async def investec_lifespan(server: MCPServer) -> AsyncIterator[InvestecContext]:
    """
    Manages the Investec API client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        InvestecContext: The context containing the Investec client
    """
    # Create and return the Investec client with the helper function in utils.py
    investec_client = get_investec_api_client()
    
    try:
        yield InvestecContext(investec_client=investec_client)
    finally:
        # No explicit cleanup needed for the client
        pass

# Initialize the MCP server with the Investec client as context
mcp = MCPServer(
    "investec-mcp",
    description="MCP server for Investec Banking API integration",
    lifespan=investec_lifespan,
)


def transport_security() -> TransportSecuritySettings | None:
    """Host names to accept besides localhost, e.g. the name a reverse proxy serves.

    Without ALLOWED_HOSTS the SDK default applies: when bound to loopback, only
    requests addressed to localhost are accepted (DNS rebinding protection).
    """
    extra = [name.strip() for name in os.getenv("ALLOWED_HOSTS", "").split(",") if name.strip()]
    if not extra:
        return None
    hosts = ["127.0.0.1", "localhost", "[::1]", *extra]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts + [f"{host}:*" for host in hosts],
    )

async def main():
    """
    Main entry point for the MCP server.
    
    Registers all tools and starts the server with the configured transport.
    """
    # Register all tools with the server
    await register_all_tools(mcp)
    
    # Run the server with the configured transport
    transport = os.getenv("TRANSPORT", "sse")
    host = os.getenv("HOST") or "127.0.0.1"
    port = int(os.getenv("PORT") or "8050")
    security = transport_security()
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async(host=host, port=port, transport_security=security)
    elif transport == 'streamable-http':
        # Run the MCP server with Streamable HTTP transport, served at /mcp
        await mcp.run_streamable_http_async(host=host, port=port, transport_security=security)
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())