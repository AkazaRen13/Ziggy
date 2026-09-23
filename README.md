# Ziggy — Local AI Search Assistant

Ziggy is a lightweight always-on-top desktop assistant that lives as a small animated circle in the corner of your screen. Click it, type a question, and it searches the web in real time — then uses a locally-running Qwen2.5 1.5B language model to synthesize the top results into a single, direct plain-language answer. No browser tab, no links, no account, no cloud. Everything runs on your machine.

---

## Demo

![demo](demo.gif)

---

## What It Does

Most AI assistants either require a paid subscription, send your queries to a remote server, or need a powerful GPU to run locally. Ziggy is different — it combines live web retrieval with on-device language model inference to give you Google AI Overview-style answers, completely offline after the initial search. It runs on a mid-range CPU with no GPU, no API key, and no data leaving your machine except for the search query itself.

The workflow is simple:
- Ziggy sits as a small animated circle in the bottom-right corner of your screen, always on top
- Click it and a clean input bubble appears
- Type your question and hit Enter
- Ziggy searches DuckDuckGo for the top 5 results and feeds them to Qwen2.5-1.5B running locally
- The model reads the search snippets and writes a direct 2-4 sentence answer
- The answer appears in the bubble in seconds — no links, no bullet points, just information

Right-click Ziggy to quit. Drag him anywhere on screen.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Desktop UI | Python `tkinter` — frameless, always-on-top, transparent background |
| Animations | Custom canvas-drawn face with blink, wink, look around, UwU, surprised, squint states |
| Web search | `ddgs` (DuckDuckGo, no API key required) |
| Language model | Qwen2.5-1.5B-Instruct, IQ4_XS quantization (~895 MB) |
| Inference runtime | `llama-cpp-python`, CPU only, no GPU layers |
| Packaging | PyInstaller single-file Windows EXE with model bundled inside |

---

## Download

1. Go to [Releases](../../releases)
2. Download `Ziggy.zip`
3. Extract and double-click `Ziggy.exe`

No Python required. No installation. No terminal. It just works.

Requires Windows 10/11. Works on any modern CPU — no GPU needed. First response takes 10-20 seconds while the model loads into RAM. Every query after that is 5-10 seconds.

---

## Build From Source

Requirements: Python 3.10+, Windows

```bash
git clone https://github.com/*whatever my github username is*/ziggy
cd ziggy
```

Run `setup.bat` — this creates a virtual environment, installs all dependencies, and downloads the model (895 MB, one time only).

Run `run.bat` to test the app.

Run `build.bat` to package everything into `dist\Ziggy.exe`.

---

## Project Structure

ziggy/
├── src/
│ ├── app.py # Main application — UI, animations, search, inference
│ ├── make_icon.py # Generates ziggy.ico from scratch, no dependencies
│ └── models/ # Model weights go here (downloaded by setup.bat)
├── setup.bat # Dev environment setup
├── run.bat # Launch for testing
├── build.bat # PyInstaller packaging
└── README.md



---

## How the RAG Pipeline Works

Ziggy implements a minimal retrieval-augmented generation loop:

1. **Retrieve** — the user's question is sent to DuckDuckGo via `ddgs`. The top 5 result snippets are collected and concatenated into a context string.
2. **Augment** — the context is injected into a prompt alongside the original question and passed to the local LLM.
3. **Generate** — Qwen2.5-1.5B reads the context and generates a direct answer grounded in the retrieved content, not its training data. This means Ziggy can answer questions about events that happened after its training cutoff, as long as the web has the answer.

The model runs via `llama-cpp-python` using pure CPU inference with 6 threads. The IQ4_XS quantization keeps the model at 895 MB while preserving answer quality for this task. Generation is capped at 180 tokens to keep responses snappy.

---

## Why Qwen2.5-1.5B

At 1.5 billion parameters it is small enough to load in under 20 seconds on a CPU and generate a response in 5-10 seconds, while being capable enough to synthesize search snippets into coherent prose. Larger models would be more capable but unusable on CPU for interactive queries.

---

*Built as part of my CS portfolio to demonstrate practical application of retrieval-augmented generation, local LLM inference, and desktop application development.*