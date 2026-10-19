# 🎬 AI Video Assistant

**Turn long videos and meeting recordings into searchable, actionable knowledge.**

AI Video Assistant is a Python application that transcribes audio from YouTube videos or local media files, creates a concise summary, extracts action items and decisions, and lets you ask questions about the transcript using retrieval-augmented generation (RAG).

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"></a>
  <a href="https://www.langchain.com/"><img src="https://img.shields.io/badge/AI%20Orchestration-LangChain-1C3C3C" alt="LangChain"></a>
  <a href="https://www.trychroma.com/"><img src="https://img.shields.io/badge/Vector%20Store-ChromaDB-6B4FBB" alt="ChromaDB"></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run the Application](#run-the-application)
- [Usage](#usage)
- [How RAG Works](#how-rag-works)
- [Troubleshooting](#troubleshooting)
- [Limitations and Security Notes](#limitations-and-security-notes)
- [Future Improvements](#future-improvements)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Overview

Long recordings often contain useful information that is difficult to find by manually watching or replaying the entire video. AI Video Assistant automates the first stage of reviewing that content by producing a transcript, summary, action items, key decisions, and open questions.

You can also ask natural-language questions about the processed transcript. The application retrieves text chunks that are semantically relevant to the question and passes them to a language model to generate an answer grounded in the retrieved context.

The project provides two ways to use the processing pipeline:

- **Streamlit web app** — an interactive interface with processing status, analysis results, and a chat panel.
- **Command-line interface (CLI)** — a terminal-based workflow for processing a source and asking follow-up questions.

## Features

- **YouTube audio extraction:** Download audio from a supported YouTube URL using `yt-dlp` and FFmpeg.
- **Local media processing:** Process a local audio or video file by supplying its path.
- **Audio preprocessing:** Convert local media to mono, 16 kHz WAV audio, extract YouTube audio to WAV, and split long recordings into manageable chunks.
- **Speech transcription:** Use a locally running OpenAI Whisper model for the English option.
- **Hinglish transcription and translation:** Use the Sarvam AI speech-to-text translation API to produce English text for the Hinglish option.
- **Automatic title generation:** Generate a short title based on the transcript.
- **Meeting summarization:** Summarize transcript sections and combine the partial summaries into a final summary.
- **Action-item extraction:** Identify tasks, owners, and deadlines when they are mentioned.
- **Decision extraction:** Extract key decisions from the transcript.
- **Open-question extraction:** Identify unresolved questions and topics that may need follow-up.
- **Ask questions about a recording:** Use embeddings and ChromaDB retrieval with a Mistral language model to answer questions based on retrieved transcript content.
- **Interactive results:** View the title, summary, full transcript, action items, decisions, and open questions in the Streamlit interface.
- **Chat history controls:** Review the current chat and clear it from the interface.

> **Note:** The application accepts a YouTube URL or a local file path. The current interface does not provide a file-upload widget. When hosted remotely, a local path must refer to a file accessible to the host machine, not merely a path on the user's computer.

## How It Works

```text
YouTube URL or local media file
            │
            ▼
   Audio acquisition / conversion
     yt-dlp · Pydub · FFmpeg
            │
            ▼
    Normalize audio and chunk it
       10-minute WAV chunks
            │
            ▼
       Speech transcription
   Whisper (English) / Sarvam (Hinglish)
            │
            ▼
        Transcript text
            │
            ├──────────────► Generate a title
            │
            ├──────────────► Summarize the meeting
            │
            ├──────────────► Extract action items
            │
            ├──────────────► Extract key decisions
            │
            ├──────────────► Extract open questions
            │
            ▼
     Split transcript into text chunks
            │
            ▼
       Create text embeddings
     all-MiniLM-L6-v2 / Hugging Face
            │
            ▼
       Store vectors in ChromaDB
            │
            ▼
      Retrieve relevant text for a query
            │
            ▼
    Mistral generates a contextual answer
```

### Processing details

1. The input module downloads audio from a YouTube URL or converts a local media file to WAV.
2. For local files, audio is converted to mono 16 kHz WAV. YouTube audio is extracted to WAV, and both input paths are divided into approximately 10-minute chunks.
3. English chunks are transcribed locally by Whisper. Hinglish chunks are subdivided into pieces of up to 25 seconds and sent to Sarvam AI's speech-to-text translation API.
4. Mistral AI generates the title, summary, action items, key decisions, and open questions.
5. The transcript is split into overlapping text chunks, embedded with the `all-MiniLM-L6-v2` model, and indexed in ChromaDB.
6. When a question is submitted, the retriever selects the four most similar chunks by default. The relevant text and question are passed to Mistral to generate an answer.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Main programming language |
| Streamlit | Interactive web interface |
| OpenAI Whisper | Local English speech recognition |
| Sarvam AI API | Hinglish speech-to-text translation into English |
| Mistral AI (`mistral-small-latest`) | Summarization, title generation, extraction, and RAG answers |
| LangChain | Prompt templates and language-model pipeline orchestration |
| `yt-dlp` | YouTube media download |
| FFmpeg | Media decoding and audio extraction/conversion |
| Pydub | Audio manipulation and chunking |
| Hugging Face Sentence Transformers | Text embeddings using `all-MiniLM-L6-v2` |
| ChromaDB | Persistent vector storage and semantic retrieval |
| `python-dotenv` | Load environment variables from `.env` |

## Project Structure

```text
AI-Video-Assistant-/
├── app.py                    # Streamlit web application
├── main.py                   # CLI entry point and shared pipeline orchestration
├── test.py                   # Manual pipeline example
├── Requirements.txt          # Python dependency list
├── .gitignore                # Git ignore rules
├── core/
│   ├── transcriber.py        # Whisper and Sarvam transcription
│   ├── summarizer.py         # Transcript summarization and title generation
│   ├── extractor.py          # Action items, decisions, and open questions
│   ├── vector_store.py       # Embeddings and ChromaDB operations
│   └── rag_engine.py         # Retrieval-augmented question answering
├── utils/
│   └── audio_processor.py    # Download, convert, and split audio
├── downloades/               # Generated media files (created at runtime)
└── vector_db/                 # Persistent ChromaDB data (created at runtime)
```

The `downloades/` and `vector_db/` directories are created by the application when required; they may not exist in a fresh clone.

## Prerequisites

Before installing the project, make sure you have:

- **Python 3.10 or later.** A virtual environment is recommended.
- **FFmpeg installed and available on your system `PATH`.** `ffmpeg-python` is only a Python wrapper; it does not install the FFmpeg executable itself. See the [FFmpeg download page](https://ffmpeg.org/download.html).
- **A Mistral API key** for summaries, title generation, extraction, and question answering. See [Mistral AI](https://console.mistral.ai/).
- **A Sarvam AI API key** if you want to use the Hinglish transcription option. See [Sarvam AI](https://www.sarvam.ai/).
- An internet connection for YouTube downloads, model downloads on first use, and external API calls.

Whisper and the embedding model may take additional time and disk space to download on their first run. The Whisper model runs locally after it is downloaded; Mistral and Sarvam calls still require network access.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Srikanth-Kuruva/AI-Video-Assistant
cd AI-Video-Assistant-
```

### 2. Create and activate a virtual environment

**Windows — PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows — Command Prompt**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

The repository currently names its dependency file `Requirements.txt` with a capital `R`. Use that exact name on case-sensitive systems:

```bash
python -m pip install --upgrade pip
python -m pip install -r Requirements.txt
```

The current source also imports the LangChain Chroma integration and text-splitter package. If these are not installed by the dependency resolution above, install them explicitly:

```bash
python -m pip install langchain-chroma langchain-text-splitters
```

### 4. Install FFmpeg

Install FFmpeg for your operating system and ensure that both `ffmpeg` and, where needed, `ffprobe` can be found from a terminal. Verify with:

```bash
ffmpeg -version
```

If the command is not found, add the FFmpeg executable directory to `PATH` and reopen the terminal.

## Configuration

Create a file named `.env` in the project root, beside `app.py` and `main.py`:

```dotenv
# Required for summaries, title generation, extraction, and RAG answers
MISTRAL_API_KEY=your_mistral_api_key_here

# Required only for the Hinglish transcription option
SARVAM_API_KEY=your_sarvam_api_key_here

# Optional: Whisper model size (defaults to small)
WHISPER_MODEL=small

# Optional: Sarvam STT translation model (defaults to `saaras:v2.5` in the code)
SARVAM_STT_MODEL=saaras:v2.5
```

Replace the example values with your own API keys. Do not commit `.env` or publish API keys in source code, screenshots, logs, or issues.

Available Whisper model sizes depend on the models supported by Whisper, for example `tiny`, `base`, `small`, `medium`, and `large`. Smaller models usually require fewer resources but may be less accurate. The repository defaults to `small`.

### Configuration note

In the current code, `core/transcriber.py` reads the Sarvam key and transcription-model settings when the module is imported, while `app.py` calls `load_dotenv()` after importing that module. If the Hinglish option reports that `SARVAM_API_KEY` is missing despite being present in `.env`, move `load_dotenv()` to the beginning of `app.py`, before imports from `core` and `utils`, or export the variables in the shell before launching the application.

## Run the Application

### Streamlit web interface

From the project root, with your virtual environment activated:

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually `http://localhost:8501`. Open that URL in your browser.

### Command-line interface

Run:

```bash
python main.py
```

When prompted, enter a YouTube URL or a path to a local audio/video file. Then choose `english` or `hinglish` when prompted. Once processing is complete, the CLI prints the title, summary, action items, decisions, and open questions, then lets you ask questions about the transcript. Type `exit`, `quit`, or `q` to end the chat.

## Usage

### Using the web app

1. Start the app using `streamlit run app.py`.
2. In the sidebar, enter either a supported YouTube URL or a local file path accessible to the machine running Streamlit.
3. Choose **English** or **Hinglish**.
4. Click **Analyse** and let the processing pipeline complete. Longer recordings may take several minutes or longer, depending on duration, hardware, API response times, and model settings.
5. Review the generated title, summary, transcript, action items, key decisions, and open questions.
6. Enter a question in the chat area to ask about the processed meeting. Clear the current chat with **Clear Chat** when needed.

### Example questions

- What are the most important points discussed?
- What tasks were assigned, and who owns them?
- What decisions were made?
- Which questions remain unresolved?
- Was a deadline mentioned for the next milestone?
- What did the meeting say about a particular topic?

The quality of the answers depends on audio clarity, transcription quality, the relevance of retrieved transcript chunks, and the language model. Verify important details against the original recording.

## How RAG Works

**Retrieval-Augmented Generation (RAG)** combines document retrieval with language-model generation. Rather than passing the entire transcript to the model for every question, the application retrieves a small set of relevant text chunks and uses them as context.

This project uses the following configuration:

- **Text splitter:** `RecursiveCharacterTextSplitter`
- **Chunk size:** 500 characters
- **Chunk overlap:** 50 characters
- **Embedding model:** `all-MiniLM-L6-v2`
- **Vector store:** ChromaDB
- **Retrieval:** Similarity search, top 4 chunks by default
- **Answer model:** Mistral `mistral-small-latest`

The RAG prompt tells the model to answer using the supplied transcript context and to say when the requested information cannot be found. This instruction helps ground answers but does not guarantee that every generated response is correct.

## Troubleshooting

### `ModuleNotFoundError: No module named 'langchain_chroma'`

Install the missing integration package in your active virtual environment:

```bash
python -m pip install langchain-chroma
```

### `ModuleNotFoundError: No module named 'langchain_text_splitters'`

Install the text-splitter package:

```bash
python -m pip install langchain-text-splitters
```

### `MISTRAL_API_KEY` is missing or API calls fail

- Confirm that `.env` is in the project root and contains a valid key.
- Restart the Streamlit process after changing `.env`.
- Check the Mistral console for API access, usage limits, and billing status.
- Do not paste API keys into chat messages, public issues, or source files.

### Hinglish transcription says the Sarvam API key is missing

Confirm that `SARVAM_API_KEY` is set. Because of the current import order, load `.env` before importing `core.transcriber`, or set the variable in your terminal environment before starting Streamlit or the CLI.

### `ffmpeg` is not found

Install FFmpeg and make sure the directory containing the executable is available on `PATH`. Installing the Python package `ffmpeg-python` alone is not sufficient.

### Local file cannot be opened

Use an absolute path to a file that exists and is readable by the process running the application. When using a remotely hosted Streamlit app, a path on your own laptop will not automatically be available to the server.

### Whisper takes a long time on first use

The selected Whisper model may need to be downloaded before transcription begins. The default `small` model also requires more processing resources than the smaller `tiny` or `base` models. You can try a smaller model by setting `WHISPER_MODEL` before starting the app.

### Answers appear to include details from another recording

The current implementation uses a persistent ChromaDB directory and a fixed collection name. Reusing that store across runs can cause old and new transcript chunks to coexist. For dependable use, isolate the vector store by recording/session and clear or filter stored data appropriately before processing a different recording.

## Limitations and Security Notes

- **Prototype status:** This project is best treated as a learning project/prototype, not a production-ready meeting management platform.
- **No speaker attribution:** The current transcription path does not preserve Whisper timestamps, and the Sarvam request sets `with_diarization` to `false`.
- **External processing:** English transcription runs locally through Whisper, but transcript text is sent to Mistral for analysis. The Hinglish option sends audio pieces to Sarvam AI. Do not process confidential recordings unless this data sharing is acceptable under your organization's policies.
- **Persistent vector data:** ChromaDB data is stored locally in `vector_db/`. The current implementation does not fully isolate all recordings by user or session, so avoid using it for multi-user or sensitive production workloads without fixing data isolation.
- **Temporary media files:** Downloaded, converted, and chunked audio may remain on disk after a run. Review and clean generated files if storage or privacy is a concern.
- **Answer accuracy:** AI-generated summaries, action items, and answers can omit or misinterpret details. Review important outputs against the original recording.
- **Safe HTML rendering:** The current interface renders some transcript and generated content using raw HTML. Avoid exposing the application to untrusted users until user-controlled and model-generated content is escaped or rendered safely.
- **Media rights:** Only download or process recordings that you have permission to access and use. Respect platform terms and copyright laws.
- **API costs and limits:** Mistral and Sarvam usage may incur costs or be subject to rate limits depending on your account and chosen services.

## Future Improvements

Potential improvements include:

- Add a file-upload control and validate file size, format, and duration.
- Preserve timestamps and, where supported, speaker labels for searchable playback and evidence links.
- Add source citations and retrieved transcript excerpts to RAG answers.
- Isolate vector collections by recording and user/session, with a clear retention policy.
- Replace raw text extraction with validated structured outputs for tasks, owners, deadlines, and decisions.
- Add retry logic, better error messages, API usage tracking, and progress reporting.
- Clean up temporary media files automatically.
- Add unit and integration tests with `pytest` and mock external API calls.
- Consolidate duplicated pipeline orchestration in the CLI and Streamlit interface into a shared service layer.
- Document deployment options, data retention, and privacy controls.

## Acknowledgements

This project builds on the work of the following tools and services:

- [OpenAI Whisper](https://github.com/openai/whisper) — speech recognition
- [Sarvam AI](https://www.sarvam.ai/) — speech-to-text translation API
- [Mistral AI](https://mistral.ai/) — language model API
- [LangChain](https://www.langchain.com/) — LLM application orchestration
- [ChromaDB](https://www.trychroma.com/) — vector database
- [Hugging Face](https://huggingface.co/) — embedding model ecosystem
- [Streamlit](https://streamlit.io/) — web interface
- [yt-dlp](https://github.com/yt-dlp/yt-dlp), [Pydub](https://github.com/jiaaro/pydub), and [FFmpeg](https://ffmpeg.org/) — audio acquisition and processing

## License

No license file is currently included in the repository. Until a license is added by the repository owner, do not assume that the project is licensed for unrestricted reuse, redistribution, or modification.

---

<p align="center">
  Made to make long recordings easier to understand, search, and act on.
</p>
