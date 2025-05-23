import datetime
import asyncio
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from multi_tool_agent.prompt import DEFAULT_AGENT_PROMPT
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from contextlib import AsyncExitStack
from app.mcp_svr.mcp_tools import save_data_to_db_from_url, search_from_bm25db_using_user_query, search_from_tavily_using_user_query

async def save_data_to_db_from_url_function(
    url: str,
) -> str:
    """Crawls a URL, processes its content, and saves it to a BM25 search index for later retrieval.
    
    This tool is useful when you need to:
    - Index web content for searchable storage
    - Process and store content from a specific URL
    - Create a searchable database from web content
    
    Args:
        url (str): The URL to crawl and process. Must be a valid web address.
        
    Returns:
        dict: A dictionary containing:
            - status: "success", "finished", or "error"
            - report: A message describing the operation result
    """
    common_exit_stack = AsyncExitStack()

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8080/sse",
        ),
        async_exit_stack=common_exit_stack
    )

    result = await tools[0].run_async(
        args={
            "url": url,
        },
        tool_context=None,
    )
    await exit_stack.aclose()
    return result.content[0].text

async def search_from_bm25db_using_user_query_function(
    query: str,
    top_k: int,
) -> str:
    """Search through previously crawled and indexed web content stored in the local BM25 database.
    
    This tool is useful when you need to:
    - Search through content that was previously crawled and saved using save_data_to_db_from_url
    - Perform semantic search on locally stored web content
    - Get relevant snippets from previously processed URLs
    
    Args:
        query (str): The search query to find relevant content
        top_k (int, optional): Number of top results to return. If not provided, you should decide an appropriate value
                               based on the query complexity and context. For general queries, 3-5 results may be sufficient, 
                               while more complex or broad topics might require 7-10 results.
        
    Returns:
        dict: A dictionary containing:
            - status: "success" or "error"
            - results: List of documents with their relevance scores
            
    Note: If top_k is not specified, intelligently determine an appropriate value based on the query context.
    """
    common_exit_stack = AsyncExitStack()

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8080/sse",
        ),
        async_exit_stack=common_exit_stack
    )

    result = await tools[1].run_async(
        args={
            "query": query,
            "top_k": top_k,
        },
        tool_context=None,
    )
    await exit_stack.aclose()
    return result.content[0].text

async def search_from_tavily_using_user_query_function(
    query: str,
    max_results: int,
    search_depth: str,
    days: int,
) -> str:
    """Search the web in real-time using the Tavily search API for fresh, up-to-date content.
    
    This tool is useful when you need to:
    - Search the web for current, real-time information
    - Find recent articles and content from the past few days
    - Get fresh results that aren't in the local database
    
    Args:
        query (str): The search query to find relevant content
        max_results (int, optional): Maximum number of results to return. If not provided, determine an appropriate value
                                     based on the query. For simple factual queries, 1-3 results may be sufficient. For
                                     complex topics requiring diverse perspectives, consider 5-8 results.
        search_depth (str, optional): ["basic", "advanced"] - Depth of search. If not provided, determine based on query
                                      complexity. Use "basic" for straightforward factual queries and "advanced" for complex,
                                      nuanced, or technical topics requiring deeper analysis.
        days (int, optional): Number of past days to search within. If not provided, determine based on the query context.
                              For recent events or trending topics, 1-3 days may be appropriate. For emerging research or
                              developing stories, 7-14 days. For established topics or background information, 30+ days.
        
    Returns:
        dict: A dictionary containing:
            - status: "success" or "error"
            - results: List of search results from the web
            
    Note: If optional parameters are not specified, intelligently determine appropriate values based on the query context
          and the specific information needs implied by the query.
    """
    common_exit_stack = AsyncExitStack()

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8080/sse",
        ),
        async_exit_stack=common_exit_stack
    )
    result = await tools[2].run_async(
        args={
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "days": days,
        },
        tool_context=None,
    )
    await exit_stack.aclose()
    return result.content[0].text

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    instruction=DEFAULT_AGENT_PROMPT,   
    tools=[
        search_from_tavily_using_user_query_function, 
        search_from_bm25db_using_user_query_function, 
        save_data_to_db_from_url_function
    ],
    # tools=[
    #     search_from_tavily_using_user_query,
    #     search_from_bm25db_using_user_query,
    #     save_data_to_db_from_url
    # ]
)

async def main():
    result = await search_from_tavily_using_user_query_function("What is the capital of France?", 1, "basic", 7)

if __name__ == "__main__":
    asyncio.run(main())