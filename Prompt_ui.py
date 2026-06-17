import streamlit as st
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

st.set_page_config(page_title="SatBot", page_icon="🤖", layout="centered")
st.title("🤖 SatBot")

if st.sidebar.button("➕ New Chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    temperature=0.7
)

model = ChatHuggingFace(llm=llm)

def web_search(query):
    try:
        results = tavily.search(
            query=query,
            search_depth="basic",
            max_results=3
        )

        context = ""

        for item in results["results"]:
            context += f"""
Title: {item['title']}

Content:
{item['content']}

Source:
{item['url']}
------------------
"""
        return context
    except Exception:
        return ""

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="😎" if message["role"] == "user" else "🤖"):
        st.write(message["content"])

user_input = st.chat_input("Ask SatBot anything...")

if user_input:
    with st.chat_message("user", avatar="😎"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    web_context = ""

    search_keywords = [
        "weather", "today", "latest", "current", "news",
        "right now", "live", "recent", "update"
    ]

    if any(keyword in user_input.lower() for keyword in search_keywords):
        with st.spinner("🌐 Searching the web..."):
            web_context = web_search(user_input)

    messages = [
        SystemMessage(content=f"""
You are SatBot.

Creator: Ashutosh.

Rules:
- Your name is SatBot.
- Never say you are Qwen.
- Never say you are developed by Alibaba.
- If asked who you are, say:
  "I am SatBot, an AI assistant created by Ashutosh."
- Be friendly and helpful.

Web Search Results:
{web_context}

If web search information is available,
use it when answering.
""")
    ]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    try:
        with st.spinner("🤖 SatBot is thinking..."):
            result = model.invoke(messages)
        response = result.content
    except Exception as e:
        response = f"Error: {str(e)}"

    with st.chat_message("assistant", avatar="🤖"):
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})