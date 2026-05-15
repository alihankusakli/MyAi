import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe(audio_path):
    print(f"Transcribing {audio_path}...")

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    text = result.text.strip()

    filename = os.path.basename(audio_path)
    name = os.path.splitext(filename)[0]
    output_path = f"data/{name}.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved to {output_path}")
    print(f"\nTranscript preview:\n{text[:300]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file>")
    else:
        transcribe(sys.argv[1])
