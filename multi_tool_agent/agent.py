import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from app.mcp_server.rag import save, search
from multi_tool_agent.prompt import DEFAULT_AGENT_PROMPT

root_agent = Agent(
    name="bm25s_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent that provides information retrieval services using BM25 search algorithm. "
        "Capable of ingesting, indexing, and searching through document collections."
    ),
    instruction=DEFAULT_AGENT_PROMPT,
    tools=[save, search],
)
