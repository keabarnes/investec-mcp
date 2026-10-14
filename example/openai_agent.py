# agents/scrape_agent.py
import asyncio
import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerHTTP
from dotenv import load_dotenv
import logging
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key")

investec_mcp_server = MCPServerHTTP(
    url="http://localhost:8050/sse",
)


class InvestecAgentDependencies(BaseModel):
    user_question: str = Field(..., description="Question from the user.")


model = OpenAIModel("gpt-4.1")

investecAgent: Agent = Agent(
    model=model,
    deps_type=InvestecAgentDependencies,
    output_type=str,
    mcp_servers=[investec_mcp_server],
)


@investecAgent.system_prompt
def system_prompt(ctx: RunContext[InvestecAgentDependencies]):
    return f"""
    You are a helpful assistant specializing in answering questions about Investec bank services, accounts, and related topics.
    You have access to tools provided by the Investec bank MCP server. Use these tools whenever necessary to retrieve accurate and up-to-date information (e.g., account balances, transaction history, beneficiary details).
    Carefully analyze the user's question and provide a clear, concise, and accurate answer based on the information available to you, utilizing the MCP tools as needed.
    User's question: {ctx.deps.user_question}
    """


async def main():
    console = Console()
    async with investecAgent.run_mcp_servers():
        while True:
            user_question = console.input("[bold cyan]Please enter your question (or type 'exit' to quit):[/bold cyan] ")
            if user_question.lower() in ["exit", "quit"]:
                break

            deps = InvestecAgentDependencies(user_question=user_question)
            console.print("[yellow]Thinking...[/yellow]")
            try:
                result = await investecAgent.run(deps=deps)
                console.print("\n[bold green]Answer:[/bold green]")
                console.print(Markdown(result.output))
            except Exception as e:
                console.print(f"[bold red]An error occurred:[/bold red] {e}")
            console.print("\n" + "-"*20 + "\n") # Separator for clarity


if __name__ == "__main__":
    asyncio.run(main())
