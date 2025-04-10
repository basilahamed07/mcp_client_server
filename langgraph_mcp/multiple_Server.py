from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio

from langchain_groq import ChatGroq
model = ChatGroq(
        model="qwen-2.5-32b",
        groq_api_key="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"
    )


async def main():
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
        math_response = await agent.ainvoke({"messages": "give the latest tech news!"})
        print(math_response)
        weather_response = await agent.ainvoke({"messages": "give the stock price of TSLA"})
        print(weather_response)


if __name__ == "__main__":
    asyncio.run(main())