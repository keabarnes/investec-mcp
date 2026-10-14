# Investec MCP Example Agent

This directory contains an example Python script (`openai_agent.py`) demonstrating how to use an AI agent powered by `pydantic-ai` and OpenAI to interact with the Investec MCP server.

## Functionality

The agent is designed to:
1.  Connect to a running Investec MCP server (expected at `http://localhost:8050/sse` by default).
2.  Take a user's question about Investec via terminal input.
3.  Use the connected MCP server's tools and resources to find an answer.
4.  Print the answer back to the terminal.

## Prerequisites

*   Python 3.12+
*   `uv` (for environment management - install via `pip install uv`)
*   A running instance of the Investec MCP server from the parent directory.
*   An OpenAI API key.

## Setup

1.  **Navigate to this directory:**
    ```bash
    cd example
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    uv sync # Installs dependencies based on pyproject.toml and uv.lock
    # Alternatively, use 'uv pip install .' if you want to resolve and install fresh dependencies
    ```
    *(Note: `uv sync` uses the `uv.lock` file if it exists, ensuring consistent dependencies. `uv pip install .` will resolve dependencies based on `pyproject.toml` and potentially update the lock file.)*

4.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your OpenAI API key:
        ```env
        OPENAI_API_KEY=your_openai_api_key_here
        ```

## Running the Example

1.  **Ensure the main Investec MCP server is running.** (You might need to run `python src/main.py` in the parent directory).
2.  **Run the agent script from within this `example` directory:**
    ```bash
    python openai_agent.py
    ```
3.  The script will prompt you to enter your question. Type your question and press Enter.
4.  The agent will process the question, potentially interacting with the MCP server, and print the answer.

## Project Structure

*   `openai_agent.py`: The main script for the example agent.
*   `pyproject.toml`: Defines the project metadata and dependencies for `uv`.
*   `.env.example`: Example environment file structure.
*   `.env`: Your local environment configuration (ignored by git).
*   `README.md`: This file.