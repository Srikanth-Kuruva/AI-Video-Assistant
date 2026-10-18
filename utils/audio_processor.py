
import shutil
from pathlib import Path

import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Find FFmpeg executables using Windows PATH.
FFMPEG_EXE = shutil.which("ffmpeg")
FFPROBE_EXE = shutil.which("ffprobe")

if not FFMPEG_EXE or not FFPROBE_EXE:
    raise RuntimeError(
        "FFmpeg or FFprobe was not found. "
        "Verify your Windows PATH and restart the terminal."
    )

# Pydub needs the executable paths, not just the directory.
AudioSegment.converter = FFMPEG_EXE
AudioSegment.ffprobe = FFPROBE_EXE


def download_youtube_audio(url: str) -> str:
    """Download YouTube audio and convert it to WAV format."""

    output_template = str(DOWNLOAD_DIR / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "ffmpeg_location": str(Path(FFMPEG_EXE).parent),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = Path(ydl.prepare_filename(info))
        wav_path = filename.with_suffix(".wav")

    if not wav_path.is_file():
        raise FileNotFoundError(
            f"Expected WAV file was not created: {wav_path}"
        )

    return str(wav_path)


def convert_to_wav(input_path: str) -> str:
    """Convert a local audio/video file to mono, 16 kHz WAV."""

    input_file = Path(input_path)

    if not input_file.is_file():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    output_path = input_file.with_name(
        input_file.stem + "_converted.wav"
    )

    audio = AudioSegment.from_file(str(input_file))
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(str(output_path), format="wav")

    return str(output_path)


def chunk_audio(
    wav_path: str, chunk_minutes: int = 10
) -> list[str]:
    """Split WAV audio into chunks of the specified duration."""

    if chunk_minutes <= 0:
        raise ValueError("chunk_minutes must be greater than zero")

    wav_file = Path(wav_path)

    if not wav_file.is_file():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    audio = AudioSegment.from_wav(str(wav_file))
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = wav_file.with_name(
            f"{wav_file.stem}_chunk_{i}.wav"
        )

        chunk.export(str(chunk_path), format="wav")
        chunks.append(str(chunk_path))

    return chunks


def process_input(source: str) -> list[str]:
    """Download or convert input audio, then split it into chunks."""

    if source.startswith(("http://", "https://")):
        print("Detected URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks
