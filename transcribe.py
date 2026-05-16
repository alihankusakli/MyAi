import os
import sys
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic()

EVAL_PROMPT = """This is a voice recording transcript from Alihan. 
Extract and summarize only what reveals his personality, thoughts, experiences, 
values, and worldview. Write in first person as Alihan. 
Ignore filler words, repetitions, and irrelevant parts.

Transcript:
{text}"""

def transcribe(audio_path):
    print(f"Transcribing {audio_path}...")

    with open(audio_path, "rb") as f:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    raw_text = result.text.strip()
    print("Transcribed. Evaluating with Claude and GPT...")

    # Claude değerlendirsin
    claude_response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": EVAL_PROMPT.format(text=raw_text)}]
    )
    claude_eval = claude_response.content[0].text.strip()

    # GPT değerlendirsin
    gpt_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[{"role": "user", "content": EVAL_PROMPT.format(text=raw_text)}]
    )
    gpt_eval = gpt_response.choices[0].message.content.strip()

    # İkisini birleştir
    combined = f"[Claude evaluation]\n{claude_eval}\n\n[GPT evaluation]\n{gpt_eval}"

    filename = os.path.basename(audio_path)
    name = os.path.splitext(filename)[0]
    output_path = f"data/{name}.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"Saved to {output_path}")
    print(f"\nPreview:\n{combined[:300]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file>")
    else:
        transcribe(sys.argv[1])