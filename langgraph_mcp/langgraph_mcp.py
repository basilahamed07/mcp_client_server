import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

query = input("Query:")

# Define llm
model = ChatGroq(
        model="qwen-2.5-32b",
        groq_api_key="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"
    )

# Define MCP servers
async def run_agent():
    print("Starting agent...")
    server_list =  {
            "latest_tech_news": {
                "command": "python",
                "args": ["/workspaces/codespaces-blank/mcp_client_server/mcp_projects/mcp-server/weather.py"],
                "transport": "stdio",
            },       
            "math": {
                "command": "python",
                "args": ["/workspaces/codespaces-blank/langgraph_mcp/match.py"],
                "transport": "stdio",
            },       
       
        }
    async with MultiServerMCPClient(
      server_list
    ) as client:
        print("Connected to MCP servers")
        # Load available tools
        tools = client.get_tools()
        agent = create_react_agent(model, tools)
        print("Agent created")

        # Add system message
        system_message = SystemMessage(content=(
                "You have access to multiple tools that can help answer queries. "
                "Use them dynamically and efficiently based on the user's request. "
        ))
        print("System message added")

        # Process the query
        agent_response = await agent.ainvoke({"messages": [system_message, HumanMessage(content=query)]})


        print(agent_response)
        return agent_response["messages"][-1].content

# Run the agent
if __name__ == "__main__":
    response = asyncio.run(run_agent())
    print("\nFinal Response:", response)