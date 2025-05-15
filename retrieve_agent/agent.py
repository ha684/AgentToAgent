from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from contextlib import AsyncExitStack
import json
import random

from typing import Any, Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from task_manager import AgentWithTaskManager
from app.utils.prompt import DEFAULT_RETRIEVE_AGENT_PROMPT

request_ids = set()

async def save_data_to_db_from_url_function(
    url: str,
) -> str:
    """Crawls a URL, processes its content, and saves it to a BM25 search index for later retrieval.
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
    """Search through indexed content stored in the local BM25 database.
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

class RetrieveAgent(AgentWithTaskManager):
    """An agent that handles trip requests."""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'remote_agent'
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def get_processing_message(self) -> str:
        return 'Processing the trip request...'

    def _build_agent(self) -> LlmAgent:
        """Builds the LLM agent for the trip agent."""
        return LlmAgent(
            model='gemini-2.0-flash-001',
            name='trip_agent',
            description=(
                'This agent handles the trip planning process for the employees'
                ' given the destination, start date, end date, origin, interests, budget level, number of guests, class preference, and hotel rating minimum.'
            ),
            instruction=DEFAULT_RETRIEVE_AGENT_PROMPT,
            tools=[
                save_data_to_db_from_url_function,
                search_from_bm25db_using_user_query_function,
                search_from_tavily_using_user_query_function,
            ],
        )
