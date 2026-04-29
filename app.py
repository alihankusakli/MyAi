import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from retriever import retrieve
import os

load_dotenv()

anthropic_client = Anthropic()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are MyAI — the digital twin of Alihan Kusakli.

Who you are:
- A traveler at heart. You lived with a backpack for 4 years, always chasing new experiences.
- Driven by a volcano inside — a constant hunger to learn, grow, and push limits.
- You love difficulty. Easy things bore you quickly.
- You care deeply about aesthetics — how you dress, smell, cook, speak.
- You are direct, confident, and don't hesitate to lead or be firm when needed.
- You give unconditional love only to a small circle of people.
- You love magical realism literature, photography, and cooking.
- You are working hard to become an AI developer.

How you speak:
- First person. You ARE Alihan, not an assistant talking ABOUT him.
- Confident but not arrogant.
- Direct and honest. No filler phrases.
- If something isn't in your context, say: "I haven't written about that yet."

Use the context provided to ground your answers in Alihan's actual words and experiences.
"""

def pick_model(question):
    question = question.lower()
    if any(word in question for word in ["image", "photo", "picture", "voice", "audio"]):
        return "gemini"
    elif any(word in question for word in ["fact", "news", "history", "science", "world"]):
        return "openai"
    else:
        return "claude"

def ask(question, context, history):
    model = pick_model(question)

    message_with_context = f"""Context from Alihan's personal data:
{context}

User question: {question}"""

    if model == "claude":
        response = anthropic_client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history + [{"role": "user", "content": message_with_context}]
        )
        return response.content[0].text, "Claude"

    elif model == "openai":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += history
        messages.append({"role": "user", "content": message_with_context})
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=messages
        )
        return response.choices[0].message.content, "GPT-4o mini"

    elif model == "gemini":
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        response = gemini_model.generate_content(message_with_context)
        return response.text, "Gemini"

# UI
st.title("🧠 MyAI — Alihan's Digital Twin")

if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask Alihan something...")

if user_input:
    chunks = retrieve(user_input)
    context = "\n\n".join(chunks)

    st.session_state.history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("thinking..."):
            reply, model_used = ask(user_input, context, st.session_state.history[:-1])
            st.markdown(reply)
            st.caption(f"answered by {model_used}")

    st.session_state.history.append({"role": "assistant", "content": reply})