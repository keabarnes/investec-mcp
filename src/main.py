"""
MCP server for integrating Investec Banking API into AI agents.
"""
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import os
import sys

from utils import get_investec_api_client
from tools import register_all_tools
from access import access_level_from_env

load_dotenv()

# Create a dataclass for our application context
@dataclass
class InvestecContext:
    """Context for the Investec API MCP server."""
    investec_client: object  # Will be replaced with actual client type

@asynccontextmanager
async def investec_lifespan(server: FastMCP) -> AsyncIterator[InvestecContext]:
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

# Initialize FastMCP server with the Investec client as context
mcp = FastMCP(
    "investec-mcp",
    description="MCP server for Investec Banking API integration",
    lifespan=investec_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)

async def main():
    """
    Main entry point for the MCP server.
    
    Registers all tools and starts the server with the configured transport.
    """
    # Register the tools allowed at the configured access level
    access_level = access_level_from_env()
    await register_all_tools(mcp, access_level)
    print(f"investec-mcp: access level {access_level.name.lower()}", file=sys.stderr)
    
    # Run the server with the configured transport
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())