from app.utils.logger_conf import logger
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from contextlib import AsyncExitStack
import os

import click

from trip_agent.agent import TripAgent
from common.server import A2AServer
from common.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    MissingAPIKeyError,
)
from dotenv import load_dotenv
from task_manager import AgentTaskManager

load_dotenv()



@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10002)
def main(host, port):
    try:
        if not os.getenv('GOOGLE_GENAI_USE_VERTEXAI') == 'TRUE':
            if not os.getenv('GOOGLE_API_KEY'):
                raise MissingAPIKeyError(
                    'GOOGLE_API_KEY environment variable not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE.'
                )

        capabilities = AgentCapabilities(streaming=True)
        
        skill = AgentSkill(
            id='Trip planning',
            name='Trip Planning Expert',
            description='Comprehensive travel planning assistant that creates personalized itineraries based on your preferences. Provides customized recommendations for destinations, accommodations, activities, and transportation while respecting your budget, interests, and travel style.',
            tags=['trip planning', 'travel', 'vacation', 'itinerary', 'tourism'],
            examples=[
                'I want to plan a vacation to Japan next spring',
                'Help me plan a business trip to London for next month',
                'Can you suggest a family-friendly itinerary for Hawaii?',
            ],
        )

        agent_card = AgentCard(
            name='Trip Planning Expert',
            description='Personal travel consultant that creates customized trip plans with detailed itineraries, accommodation and flight recommendations, activity suggestions, and budget considerations. Perfect for vacation planning, business travel, family trips, and specialized travel experiences.',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=TripAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=TripAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=TripAgent()),
            host=host,
            port=port,
        )
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        exit(1)


if __name__ == '__main__':
    main()
