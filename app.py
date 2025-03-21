# main.py
import chainlit as cl
from agent import make_graph

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessageChunk

from chainlit.input_widget import Select, Slider

import os, uuid
from dotenv import load_dotenv

_ : bool = load_dotenv()

@cl.on_chat_start
async def on_chat_start():
    thread_id = f"thread-{uuid.uuid4()}"
    # Store thread ID in session
    cl.user_session.set("thread_id", thread_id)

    # Get model settings from user
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Gemini - Model",
                values=["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.0-pro-exp"],
                initial_index=0,
            ),
            Slider(
                id="temperature",
                label="Temperature",
                initial=1,
                min=0,
                max=2,
                step=0.1,
            ),
        ]
    ).send()
    # Create model with given settings
    model = ChatGoogleGenerativeAI(
        model=settings["model"], 
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=settings["temperature"]
        )
    # Store model in session
    cl.user_session.set("model", model)

@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")  # Retrieve the user-specific thread ID

    # Get model from session
    model = cl.user_session.get("model", "gemini-2.0-flash")
    # 
    config = {"configurable": {"thread_id": thread_id}}

    msg = cl.Message(content="")  # Initialize an empty message for streaming

    try:
        async with make_graph(model) as agent:
            async for stream, metadata in agent.astream({"messages": message.content}, config=config, stream_mode="messages"):
                print(stream, metadata)
                if isinstance(stream, AIMessageChunk) and stream.content:
                    
                    await msg.stream_token(stream.content.replace("```", "\n\n```\n"))
            await msg.send()
    except Exception as e:
        await cl.Message(content=f"Error during agent invocation: {e}").send()
