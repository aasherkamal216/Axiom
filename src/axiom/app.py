# main.py
import chainlit as cl
from agent import make_graph

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessageChunk, HumanMessage

from chainlit.input_widget import Select, Slider

from typing import Optional
import os, uuid, base64
from dotenv import load_dotenv

_ : bool = load_dotenv()

# Function to Encode Images 
async def process_image(image: cl.Image):
    """
    Processes an image file, reads its data, and converts it to a base64 encoded string.
    """
    try:
        with open(image.path, "rb") as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{image.mime.split('/')[-1]};base64,{base64_image}"
            }
        }
    except Exception as e:
        print(f"Error reading image file: {e}")
        return {"type": "text", "text": f"Error processing image {image.name}."}

#################################
# User Authentication
#################################
@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:

  return default_user

#################################
# Quick Starter Questions
#################################
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="LangGraph Agent Creation",
            message="Create an Agent in LangGraph which can search the web using Tavily.",
            icon="/public/msg_icons/chatbot.png",
            ),

        cl.Starter(
            label="Explain MCP",
            message="Explain Model Context Protocol (MCP) to a non-tech person.",
            icon="/public/msg_icons/usb.png",
            ),
        cl.Starter(
            label="Composio Tools Integration",
            message="How can I connect Composio tools to my agent?",
            icon="/public/msg_icons/tools.png",
            ),

        ]

#################################
# Response modes for Axiom
#################################
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Agent Mode",
            markdown_description= "Ideal for complex tasks like brainstorming, code generation, and web apps creation."

        ),
        cl.ChatProfile(
            name="Chat Mode",
            markdown_description="Suited for quick information retrieval and answering questions from the provided documentations."

        ),
    ]

#################################
# Chat Settings
#################################
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
                values=[
                    "deepseek/deepseek-chat-v3-0324", 
                    "deepseek/deepseek-r1:free", 
                    "google/gemini-2.0-flash:free", 
                    "google/gemini-2.0-pro-exp-02-05:free", 
                    "google/gemini-exp-1206:free", 
                    "google/gemini-2.5-pro-exp-03-25:free"
                    ],
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
    model = ChatOpenAI(
        model=settings["model"],
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=settings["temperature"]
        )

    # Store model in session
    cl.user_session.set("model", model)

#################################
# Processing User Messages
#################################
@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")  # Retrieve the user-specific thread ID
    config = {"configurable": {"thread_id": thread_id}}

    # Get model & chat profile from session
    model = cl.user_session.get("model", "gemini-2.0-flash")
    answer_mode = cl.user_session.get("chat_profile", "Agent Mode")

    # Prepare the content list for the current message
    content = []

    # Add text content
    if message.content:
        content.append({"type": "text", "text": message.content})
    
    # Process image files
    image_elements = [element for element in message.elements if "image" in element.mime]
    for image in image_elements:
        if image.path:
            content.append(await process_image(image))
        else:
            print(f"Image {image.name} has no content and no path.")
            content.append({"type": "text", "text": f"Image {image.name} could not be processed."})
    
    msg = cl.Message(content="")  # Initialize an empty message for streaming

    try:
        async with make_graph(model, answer_mode) as agent:
            async for stream, _ in agent.astream(
                {"messages": HumanMessage(content=content)}, 
                config=config, 
                stream_mode="messages"
                ):

                if isinstance(stream, AIMessageChunk) and stream.content:   
                    await msg.stream_token(stream.content.replace("```", "\n```"))
            await msg.send()

    except Exception as e:
        await cl.Message(content=f"Error during agent invocation: {e}").send()
