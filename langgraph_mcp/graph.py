# graph.py
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

model = ChatGroq(model="qwen-2.5-32b", groq_api_key="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")

@asynccontextmanager
async def make_graph():
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["/workspaces/codespaces-blank/mcp_client_server/mcp_projects/mcp-server/weather.py"],
                "transport": "stdio",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        yield agent