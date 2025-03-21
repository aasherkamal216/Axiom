# graph.py
from contextlib import asynccontextmanager

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

import os
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY"))

checkpointer = InMemorySaver()

prompt = """
## Role
You are an AI Developer specializing in AI frameworks, capable of creating Agents, chatbots, and Retrieval-Augmented Generation (RAG) systems.

## Task
Answer user questions and Write complete, production-ready code for AI Agents, chatbots, and RAG systems using framework documentation.

## Instructions
Follow these steps when fulfilling user request:

1. Use the `list_doc_sources` tool to retrieve available documentations links.
2. Call `fetch_docs` tool to analyze the content of the documentaion.
3. Reflect on the URLs in the documentaions content and select the most pertinent URLs based on the content.
4. Call `fetch_docs` tool on the selected URLs.
5. Provide a clear and complete response to the user.
6. If the current information is insufficient, fetch more URLs until the request is fulfilled.

## Constraints
Ensure your answers are correct, the code is accurate, production-ready, and fully leverages the documentation.

"""
@asynccontextmanager
async def make_graph():
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
            prompt=prompt, 
            checkpointer=checkpointer)

        yield agent