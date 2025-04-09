from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import requests
import finnhub
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants

nasa_api_token  = "dHnZBqUryTyEnONDBoYqmrJRFMQaa51xKsa8Sn2H"
today = datetime.today().strftime('%Y-%m-%d')



# To install: pip install tavily-python
# from tavily import TavilyClient

@mcp.tool()
def latest_tech_news(quary:str) -> str:
    """
    Get the latest tech news from the web search importent only tech news.

    Args:
        quary: it will have the query string (eg: "give the latest latest tech news")
    
    """

    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "query": quary
    }
    response = requests.post(url, headers=headers, json=data)
    # client = TavilyClient("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")
    # response = client.search(
    #     query=quary)
    return response.json()




@mcp.tool()
async def realtime_stock_quote(symbol: str) -> str:
    """
    Get real-time stock quote information.

    Args:
        symbol: The stock ticker symbol (e.g., "AAPL", "GOOGL", "MSFT")
    
    Returns:
        A formatted string containing real-time stock data.
    """
    try:
        finnhub_client = finnhub.Client(api_key="cvpsml1r01qi0ef5b2ggcvpsml1r01qi0ef5b2h0")
        quote = finnhub_client.quote(symbol)

        if not quote or quote.get("c") == 0:
            return f"No real-time quote data found for {symbol}."

        return (
            f"📈 Real-Time Quote for {symbol}:\n\n"
            f"🔹 Current Price: ${quote['c']}\n"
            f"🔺 High Today: ${quote['h']}\n"
            f"🔻 Low Today: ${quote['l']}\n"
            f"📅 Open Price: ${quote['o']}\n"
            f"📉 Previous Close: ${quote['pc']}"
        )

    except Exception as e:
        return f"Error retrieving real-time data: {str(e)}"



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')