# import asyncio
# import streamlit as st
# from dotenv import load_dotenv
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph.prebuilt import create_react_agent
# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain_groq import ChatGroq

# load_dotenv()

# # Sidebar UI Setup
# st.sidebar.title("🧠 Agent Configuration")
# model_name = "qwen-2.5-32b"
# st.sidebar.subheader("🤖 Model Used")
# st.sidebar.code(model_name)

# # Server configuration
# server_list = {
#     "latest_tech_news": {
#         "command": "python",
#         "args": ["/workspaces/codespaces-blank/mcp_client_server/mcp_projects/mcp-server/weather.py"],
#         "transport": "stdio",
#     },
#     "math": {
#         "command": "python",
#         "args": ["/workspaces/codespaces-blank/langgraph_mcp/match.py"],
#         "transport": "stdio",
#     },
#        "github": {
#       "command": "npx",
#       "args": [
#         "-y",
#         "mcprouter"
#       ],
#       "env": {
#         "SERVER_KEY": "9934ewm96ogv2f"
#       }
#     },
#      "playwright": {
#       "command": "npx",
#       "args": ["-y", "@automatalabs/mcp-server-playwright"]
#     }
# }
# st.sidebar.subheader("🧩 Servers Used")
# for name in server_list:
#     st.sidebar.write(f"🔧 {name}")

# # Define model
# model = ChatGroq(
#     model=model_name,
#     groq_api_key="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"
# )

# # Chat input section
# st.title("💬 LangGraph Agent Chatbot")
# query = st.chat_input("Ask me something...")

# # Initialize session state for tools and response
# if "tools" not in st.session_state:
#     st.session_state.tools = []

# if query:
#     async def run_agent(query):
#         with st.spinner("🤖 Thinking..."):
#             async with MultiServerMCPClient(server_list) as client:
#                 tools = client.get_tools()
#                 st.session_state.tools = tools  # Save tools to show in sidebar
#                 agent = create_react_agent(model, tools)
#                 system_message = SystemMessage(content=(
#                     "You have access to multiple tools that can help answer queries. "
#                     "Use them dynamically and efficiently based on the user's request."
#                 ))
#                 response = await agent.ainvoke({"messages": [system_message, HumanMessage(content=query)]})
#                 return response["messages"][-1].content

#     response = asyncio.run(run_agent(query))

#     # Show response in chat
#     with st.chat_message("user"):
#         st.write(query)
#     with st.chat_message("assistant"):
#         st.write(response)

# # Show tools in sidebar (after the agent runs at least once)
# if st.session_state.tools:
#     st.sidebar.subheader("🛠️ Tools Available")
#     for tool in st.session_state.tools:
#         st.sidebar.write(f"🔍 {tool.name}")

# import asyncio
# import streamlit as st
# from dotenv import load_dotenv
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph.prebuilt import create_react_agent
# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain_groq import ChatGroq
# from langchain.schema.messages import ToolMessage
# load_dotenv()

# # Page configuration
# st.set_page_config(page_title="LangGraph Agent Chat", page_icon="🧠", layout="wide")

# # Sidebar: Agent & Model Info
# with st.sidebar:
#     st.title("🧠 Agent Configuration")
    
#     model_name = "qwen-2.5-32b"
#     st.subheader("🤖 Model Used")
#     st.code(model_name, language="text")

#     # Server configuration
#     server_list = {
#         "latest_tech_news": {
#             "command": "python",
#             "args": ["/workspaces/codespaces-blank/mcp_client_server/mcp_projects/mcp-server/weather.py"],
#             "transport": "stdio",
#         },
#         "math": {
#             "command": "python",
#             "args": ["/workspaces/codespaces-blank/langgraph_mcp/match.py"],
#             "transport": "stdio",
#         },
#         "github": {
#             "command": "npx",
#             "args": ["-y", "mcprouter"],
#             "env": {
#                 "SERVER_KEY": "9934ewm96ogv2f"
#             }
#         }
#     }

#     st.subheader("🧩 Servers Used")
#     for name in server_list:
#         st.markdown(f"🔧 **{name}**")
# tool_names = []

# # Initialize model
# model = ChatGroq(
#     model=model_name,
#     groq_api_key="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"
# )

# # Title
# st.title("💬 LangGraph AI Agent")

# # Session state for tools and history
# if "tools" not in st.session_state:
#     st.session_state.tools = []
# if "last_tool_used" not in st.session_state:
#     st.session_state.last_tool_used = None

# # Chat input
# query = st.chat_input("Ask me anything smart...")

# # Handle query
# if query:
#     async def run_agent(query):
#         with st.spinner("🤖 Thinking..."):
#             async with MultiServerMCPClient(server_list) as client:
#                 tools = client.get_tools()
#                 st.session_state.tools = tools

#                 agent = create_react_agent(model, tools)
#                 system_message = SystemMessage(content=(
#                     "You have access to multiple tools. Use them wisely to solve user problems."
#                 ))
#                 response = await agent.ainvoke({
#                     "messages": [system_message, HumanMessage(content=query)]
#                 })
#                 print("Response:", response)
#                 tool_calls = None
#                 global tool_names
#                 tool_names = [
#                         msg.name for msg in response['messages']
#                         if isinstance(msg, ToolMessage)
#                     ]
#                 print("Tool Names:", tool_names)

#                 if hasattr(response, "tool_calls"):
#                     tool_calls = response.tool_calls
#                 elif hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
#                     tool_calls = response.additional_kwargs["tool_calls"]
#                 print("Tool Calls:", tool_calls)
#                 if tool_calls:
#                     for call in tool_calls:
#                         tool_name = call.get("name") or call.get("function", {}).get("name")
#                         print("Tool Name:", tool_name)

#                 # Find which tool was called (if any)
#                 tool_used = response.get("invocation", {}).get("tool", None)
#                 st.session_state.last_tool_used = tool_used

#                 return response["messages"][-1].content

#     response = asyncio.run(run_agent(query))

#     # Display chat
#     with st.chat_message("user"):
#         st.write(query)

#     with st.chat_message("assistant"):
#     # Show tool_name(s) used, if any
#         if 'tool_names' in locals() and tool_names:
#             st.info(f"🧰 Tools Used: **{', '.join(tool_names)}**")

#     st.write(response)

#     if st.session_state.last_tool_used:
#         st.success(f"🛠️ Tool Invoked: **{st.session_state.last_tool_used}**")


# # Show available tools in sidebar
# if st.session_state.tools:
#     st.sidebar.subheader("🛠️ Tools Available")
#     for tool in st.session_state.tools:
#         st.sidebar.markdown(f"🔍 **{tool.name}**")




import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain.schema.messages import ToolMessage

# Load environment
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="LangGraph Agent Chat", page_icon="🧠", layout="wide")

# Sidebar: Agent Configuration
# Sidebar: Agent Configuration
with st.sidebar:
    st.title("🧠 Agent Configuration")

    model_name = "qwen-2.5-32b"
    st.subheader("🤖 Model Used")
    st.code(model_name, language="text")

    # Server list
    server_list = {
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
        "github": {
            "command": "npx",
            "args": ["-y", "mcprouter"],
            "env": {
                "SERVER_KEY": "9934ewm96ogv2f"
            }
        }
    }

    # Dropdown for servers
    with st.expander("🧩 Servers Used", expanded=False):
        for name in server_list:
            st.markdown(f"🔧 **{name}**")

    # Dropdown for tools (dynamically shows only if available)
    # if st.session_state.tools:
    #     with st.expander("🛠️ Tools Available", expanded=False):
    #         for tool in st.session_state.tools:
    #             st.markdown(f"🔍 **{tool.name}**")
    # --- Tools in Sidebar ---


# Initialize model
model = ChatGroq(
    model=model_name,
    groq_api_key="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"
)

# Title
st.title("💬 LangGraph AI Agent")

# --- Session State ---
if "tools" not in st.session_state:
    st.session_state.tools = []
if "last_tool_used" not in st.session_state:
    st.session_state.last_tool_used = None
if "tool_names" not in st.session_state:
    st.session_state.tool_names = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat Input
query = st.chat_input("Ask me anything smart...")

# Async agent handler
if query:
    async def run_agent(query):
        with st.spinner("🤖 Thinking..."):
            async with MultiServerMCPClient(server_list) as client:
                tools = client.get_tools()
                st.session_state.tools = tools

                agent = create_react_agent(model, tools)
                messages = [SystemMessage(content="You have access to multiple tools. Use them wisely to solve user problems.")]
                # Add previous chat history for continuity
                for role, content in st.session_state.chat_history:
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    else:
                        messages.append(AIMessage(content=content))

                # Append the latest user input
                messages.append(HumanMessage(content=query))

                response = await agent.ainvoke({"messages": messages})

                tool_names = [
                    msg.name for msg in response['messages']
                    if isinstance(msg, ToolMessage)
                ]
                st.session_state.tool_names = tool_names

                if hasattr(response, "tool_calls"):
                    tool_calls = response.tool_calls
                elif hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
                    tool_calls = response.additional_kwargs["tool_calls"]

                tool_used = response.get("invocation", {}).get("tool", None)
                st.session_state.last_tool_used = tool_used

                # Add to conversation memory
                st.session_state.chat_history.append(("user", query))
                st.session_state.chat_history.append(("assistant", response["messages"][-1].content))

                return response["messages"][-1].content

    response = asyncio.run(run_agent(query))

# --- Display Chat --

if st.session_state.chat_history:
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    if st.session_state.tool_names:
        st.info(f"🧰 Tools Used: **{', '.join(st.session_state.tool_names)}**")

    if st.session_state.last_tool_used:
        st.success(f"🛠️ Tool Invoked: **{st.session_state.last_tool_used}**")


