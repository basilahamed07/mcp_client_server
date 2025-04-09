import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import json
import pprint

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.groq = Groq(api_key="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")
        self.pp = pprint.PrettyPrinter(indent=2)  # For pretty printing

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    def print_messages(self, messages, title="Current Messages"):
        """Pretty print the message history"""
        print(f"\n===== {title} =====")
        self.pp.pprint(messages)
        print("=" * (len(title) + 12))

    def print_response(self, response, title="Groq API Response"):
        """Pretty print the API response"""
        print(f"\n===== {title} =====")
        # Convert to dict for better printing
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            # Fallback for non-pydantic objects
            response_dict = {k: v for k, v in response.__dict__.items() if not k.startswith('_')}
        self.pp.pprint(response_dict)
        print("=" * (len(title) + 12))

    def print_tool_call(self, tool_call, result, title="Tool Call"):
        """Pretty print tool call and result"""
        print(f"\n===== {title} =====")
        print(f"Tool: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
        print(f"Result: {result}")
        print("=" * (len(title) + 12))

    async def process_query(self, query: str) -> str:
        """Process a query using Groq and available tools"""
        # Initialize conversation with user query
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        print("\n🔷 Processing query:", query)

        # Get available tools from the server
        tools_response = await self.session.list_tools()
        print("\n🔷 Available tools:")
        for tool in tools_response.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools_response.tools
        ]

        tool_results = []
        
        # Print current messages before API call
        self.print_messages(messages, "Messages")
        
        print("\n🔷 Sending request to Groq...")
        
        # First call to Groq LLM
        groq_response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
            max_tokens=1000
        )
        
        # Print the full response
        self.print_response(groq_response, "Groq Initial Response")

        # Extract the assistant's message
        assistant_message = groq_response.choices[0].message
        
        print(f"\n🔷 Assistant message content: {assistant_message.content}")
        
        # Add the assistant's response to messages
        assistant_dict = {
            "role": "assistant",
            "content": assistant_message.content or ""
        }
        
        # Process tool calls if present
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            print(f"\n🔷 Tool calls detected: {len(assistant_message.tool_calls)}")
            assistant_dict["tool_calls"] = assistant_message.tool_calls
            messages.append(assistant_dict)
            
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                
                print(f"\n🔷 Processing tool call for: {tool_name}")
                print(f"Arguments: {tool_args}")
                
                try:
                    if isinstance(tool_args, str):
                        tool_args = json.loads(tool_args)
                        print(f"Parsed arguments: {tool_args}")
                except json.JSONDecodeError as e:
                    error_msg = f"Error parsing arguments for {tool_name}: {str(e)}"
                    print(f"❌ {error_msg}")
                    tool_results.append({"error": error_msg})
                    continue
                
                try:
                    print(f"🔷 Executing tool: {tool_name} with args: {tool_args}")
                    result = await self.session.call_tool(tool_name, tool_args)
                    result_content = str(result.content)
                    print(f"✅ Tool result: {result_content}")
                    self.print_tool_call(tool_call, result_content)
                    
                    # Add tool results to messages
                    messages.append({
                        "role": "function",
                        "name": tool_name,
                        "content": result_content
                    })
                    tool_results.append({"tool": tool_name, "result": result_content})
                except Exception as e:
                    error_message = f"Error calling tool {tool_name}: {str(e)}"
                    print(f"❌ {error_message}")
                    tool_results.append({"error": error_message})

            # Second call to Groq with tool results
            print("\n🔷 Sending follow-up request to Groq with tool results...")
            final_groq_response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1000
            )
            
            final_response = final_groq_response.choices[0].message.content
            print("\n🔷 Final refined response:")
            print(final_response)
            return final_response
            
        else:
            print("\n🔷 No tool calls detected")
            return assistant_message.content or "No response generated."

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\n🚀 MCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\n🔹 Query: ").strip()

                if query.lower() in ['quit', 'exit']:
                    break

                response = await self.process_query(query)
                print("\n🔹 Final Response:")
                print(response)

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())