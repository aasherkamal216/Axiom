# main.py
import chainlit as cl
from agent import make_graph

from langchain_core.messages import AIMessageChunk
import uuid

@cl.on_chat_start
async def on_chat_start():

    thread_id = f"thread-{uuid.uuid4()}"

    cl.user_session.set("thread_id", thread_id)

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")  # Retrieve the agent from user session
    thread_id = cl.user_session.get("thread_id")  # Retrieve the user-specific thread ID

    config = {"configurable": {"thread_id": thread_id}}


    msg = cl.Message(content="fdasfasdf")  # Initialize an empty message for streaming

    try:
        async with make_graph() as agent:
            async for stream, metadata in agent.astream({"messages": message.content}, config=config, stream_mode="messages"):
                print(stream, metadata)
                if isinstance(stream, AIMessageChunk) and stream.content:
                    print("working here=========")
                    # await msg.stream_token(stream.content)

                # await msg.send()

        await msg.send()
    except Exception as e:
        await cl.Message(content=f"Error during agent invocation: {e}").send()

@cl.on_stop
async def on_stop():
    agent = cl.user_session.get("agent")
    await agent.__aexit__(None, None, None)