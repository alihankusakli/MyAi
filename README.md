# MyAI — Alihan's Travel Twin

A personal digital twin focused on travel knowledge and experiences. Built on real voice recordings, writings, and personal data from 4+ years of backpacking across Asia and Latin America.

## What it does
- Answers questions about travel experiences, destinations, and life on the road
- Responds as Alihan — in first person, based on real data
- Uses RAG (Retrieval-Augmented Generation) to ground answers in personal knowledge
- Routes questions to the best AI model (Claude, GPT-4o mini, or Gemini)

## Data sources
- Personal writings and reflections
- Voice recordings from travels (Iran, India, Nepal, Thailand, Malaysia, Laos, Philippines, Morocco, Cuba, Colombia, Ecuador, Mexico, USA)
- Instagram captions
- Travel notes and stories

## Tech stack
- Python
- ChromaDB — vector database
- RAG — Retrieval-Augmented Generation
- Anthropic Claude, OpenAI GPT-4o mini, Google Gemini
- OpenAI Whisper — voice to text
- Streamlit — web interface

## How it works
Voice recordings / writings
↓
Whisper transcribes audio
↓
Claude + GPT evaluate and summarize
↓
ChromaDB stores as vectors
↓
User asks a question
↓
Retriever finds relevant chunks
↓
Best LLM generates response

## Run locally
```bash
pip install -r requirements.txt
python ingest.py
streamlit run app.py
```

## Add new data
```bash
python transcribe.py "your_recording.m4a"
python ingest.py
```

## Live demo
https://alihan-twin.streamlit.app

## Author
Alihan Kusakli — traveler, AI developer in progress.