from app.utils.logger_conf import logger
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from contextlib import AsyncExitStack
import os

import click

from retrieve_agent.agent import RetrieveAgent
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
@click.option('--port', default=10003)
def main(host, port):
    try:
        if not os.getenv('GOOGLE_GENAI_USE_VERTEXAI') == 'TRUE':
            if not os.getenv('GOOGLE_API_KEY'):
                raise MissingAPIKeyError(
                    'GOOGLE_API_KEY environment variable not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE.'
                )

        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id='retrieve_information',
            name='Retrieve Information Tool',
            description='Helps with the retrieval of information from the database or the internet given the user query. It can also help in crawling data from a URL then save to database.',
            tags=['retrieve'],
            examples=[
                'Can you help me find the best places to visit in Tokyo?'
            ],
        )
        agent_card = AgentCard(
            name='Retrieve Agent',
            description='This agent handles the retrieval of information from the database or the internet given the user query. It can also help in crawling data from a URL then save to database.',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=RetrieveAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=RetrieveAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=RetrieveAgent()),
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
