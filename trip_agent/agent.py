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
from app.utils.prompt import DEFAULT_TRIP_AGENT_PROMPT

request_ids = set()

async def plan_trip_function(
    destination: str,
    start_date: str,
    end_date: str,
    origin: str,
    interests: str,
    budget_level: str,
    num_guests: int,
    class_preference: str,
    hotel_rating_min: int,
    initial_query: str
):
    """Intelligently searching for travel information.
    
    This tool performs multiple intelligent searches guided by an LLM to gather comprehensive
    travel information.
    
    Args:
        destination: The primary travel destination (e.g., "Paris", "Japan", "Yellowstone National Park")
        start_date: Trip start date in YYYY-MM-DD format (e.g., "2025-06-15")
        end_date: Trip end date in YYYY-MM-DD format (e.g., "2025-06-25")
        origin: Departure city or location (e.g., "New York", "London")
        interests: Traveler's interests or preferences, comma-separated (e.g., "hiking, museums, local cuisine, photography")
        budget_level: Budget category (e.g., "budget", "mid-range", "luxury")
        num_guests: Number of travelers (e.g., 2, 4)
        class_preference: Flight class preference (e.g., "economy", "business", "first")
        hotel_rating_min: Minimum hotel rating, 1-5 stars (e.g., 3, 4)
        initial_query: Free-form initial travel request if specific parameters aren't known
                    (e.g., "Planning a beach vacation for a family of 4 in December")
    
    Returns:
        Dict containing:
            - status: "complete" if finished successfully, "incomplete" if max iterations reached
            - search_results: List of all search results gathered
    """
    common_exit_stack = AsyncExitStack()

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8081/sse",
        ),
        async_exit_stack=common_exit_stack
    )
    result = await tools[0].run_async(
        args={
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "origin": origin,
            "interests": interests,
            "budget_level": budget_level,
            "num_guests": num_guests,
            "class_preference": class_preference,
            "hotel_rating_min": hotel_rating_min,
            "initial_query": initial_query,
        },
        tool_context=None,
    )
    await exit_stack.aclose()
    return result.content[0].text

class TripAgent(AgentWithTaskManager):
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
            model='gemini-2.0-flash',
            name='trip_agent',
            description=(
                'This agent handles the trip planning process for the employees'
                ' given the destination, start date, end date, origin, interests, budget level, number of guests, class preference, and hotel rating minimum.'
            ),
            instruction=DEFAULT_TRIP_AGENT_PROMPT,
            tools=[
                plan_trip_function,
            ],
        )
