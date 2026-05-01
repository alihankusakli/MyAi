import os
import base64
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI
from google import genai
from retriever import retrieve

load_dotenv()

anthropic_client = Anthropic()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            temperature=0.9,
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
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=message_with_context
        )
        return response.text, "Gemini"

# UI
st.title("🧠 MyAI — Alihan's Digital Twin")

# Photo upload
uploaded_photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"], key="photo_uploader")

if uploaded_photo:
    st.image(uploaded_photo, width=300)
    
    photo_context = st.text_area(
        "Tell me about this photo:",
        placeholder="This was in Nepal, 2018. I had just crossed the Thorong La pass...",
        key="photo_context"
    )
    
    if st.button("Save to my twin", key="save_photo"):
        mime_type = uploaded_photo.type
        image_data = base64.standard_b64encode(uploaded_photo.read()).decode("utf-8")

        response = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": f"This is Alihan's photo. He says: '{photo_context}'. Based on both the image and what he wrote, write 3 sentences in first person as Alihan capturing what this moment meant to him."
                    }
                ]
            }]
        )

        description = response.content[0].text
        st.success("Saved to your twin!")
        st.caption(f"📷 {description}")

        with open("data/photos.txt", "a", encoding="utf-8") as f:
            f.write(f"\n\n{description}")