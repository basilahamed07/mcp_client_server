# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import asyncio

async def main():
    # Initialize the Groq model
    model = ChatGroq(
        model="qwen-2.5-32b",
        groq_api_key="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"
    )

    # Set up server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["/workspaces/codespaces-blank/mcp_client_server/mcp_projects/mcp-server/weather.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke(
                {"messages": "give the latest tech news!"}
            )
            print(agent_response)

if __name__ == "__main__":
    asyncio.run(main())