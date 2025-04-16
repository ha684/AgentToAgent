from mcp import ClientSession
from mcp.client.sse import sse_client

async def check():
    async with sse_client("http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()

            # List avail tool
            tools = await session.list_tools()
            print(tools)

if __name__ == "__main__":
    import asyncio
    asyncio.run(check())
