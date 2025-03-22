# graph.py
from contextlib import asynccontextmanager

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from prompts import AGENT_PROMPT, CHATBOT_PROMPT

# Initialize checkpointer
checkpointer = InMemorySaver()

@asynccontextmanager
async def make_graph(model, answer_mode):
    async with MultiServerMCPClient(
        {
            "docs_mcp": {
                # make sure you start your server on port 8082
                "url": "http://localhost:8082/sse",
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(
            model, 
            client.get_tools(), 
            prompt=AGENT_PROMPT if answer_mode == "Agent Mode" else CHATBOT_PROMPT, 
            checkpointer=checkpointer)

        yield agent