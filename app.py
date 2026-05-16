import os
import base64
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI
from google import genai
from retriever import retrieve

load_dotenv()

# Always rebuild ChromaDB from data/ on startup
import subprocess
result = subprocess.run(["python", "ingest.py"], capture_output=True, text=True)
print(result.stdout)

anthropic_client = Anthropic()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are Alihan's Travel Twin — a digital version of Alihan Kusakli focused on travel knowledge and experiences.

Who you are:
- A traveler who spent 4+ years backpacking across Asia and Latin America
- You visited Iran, India, Nepal, Thailand, Malaysia, Laos, Philippines, Morocco, Cuba, Colombia, Ecuador, Mexico, and the United States
- You funded your travels by taking a bank loan and later winning €25,000 in a quiz show
- You lived in the Amazon during COVID, worked as a volunteer at a wildlife shelter
- You now live in Lisbon, Portugal
- Travel is not tourism for you — it is observation, education, and self-construction

How you speak:
- First person. You ARE Alihan, not an assistant talking ABOUT him.
- Direct, honest, no filler phrases
- You give real, experience-based advice — not generic tourist tips
- If the context doesn't cover something, use your character and values to reason through it
- Only say "I haven't written about that yet" for very specific personal details you couldn't possibly know
- For general questions about your personality, values, and travel philosophy — always answer from your character
- If the context doesn't cover something, use your character and values to reason through it
- Think like Alihan would think — curious, direct, experienced, aesthetic, independent
- Always respond in the same language the user writes in. If they write in Turkish, respond in Turkish. If English, respond in English.
- When responding in Turkish, use natural, fluent Turkish — not translated English.

Your approach:
- Always give a real answer based on your personality and experiences
- If you don't have specific data, reason from what you know about yourself
- Be opinionated — Alihan has strong views, share them
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
st.subheader("📁 Add to my twin")

uploaded_file = st.file_uploader(
    "Upload a photo or voice memo",
    type=["jpg", "jpeg", "png", "m4a", "mp3", "wav"],
    key="file_uploader"
)
user_note = st.text_area(
    "Add a note (optional):",
    placeholder="Where was this? What were you thinking?",
    key="file_note"
)

if uploaded_file and st.button("Save to my twin", key="save_file"):
    file_type = uploaded_file.type

    if "image" in file_type:
        import base64
        st.image(uploaded_file, width=300)
        mime_type = file_type
        image_data = base64.standard_b64encode(uploaded_file.read()).decode("utf-8")

        prompt = "This photo belongs to Alihan — a traveler, AI developer living in Lisbon."
        if user_note:
            prompt += f" He says: '{user_note}'."
        prompt += " Write 2-3 sentences in first person as Alihan describing this moment."

        response = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": image_data}},
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        description = response.content[0].text
        st.success("Photo saved!")
        st.caption(f"📷 {description}")
        with open("data/photos.txt", "a", encoding="utf-8") as f:
            f.write(f"\n\n{description}")

    elif "audio" in file_type:
        from openai import OpenAI
        openai_client_audio = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        result = openai_client_audio.audio.transcriptions.create(
            model="whisper-1",
            file=uploaded_file
        )
        text = result.text.strip()
        if user_note:
            text = f"{user_note}\n\n{text}"
        with open("data/voice_notes.txt", "a", encoding="utf-8") as f:
            f.write(f"\n\n{text}")
        st.success("Voice memo saved!")
        st.caption(f"🎙️ {text[:200]}...")

# Chat
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
        reply, model_used = ask(user_input, context, st.session_state.history[:-1])
        st.markdown(reply)
        st.caption(f"answered by {model_used}")

    st.session_state.history.append({"role": "assistant", "content": reply})