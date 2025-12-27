#!/usr/bin/env python3
"""
Main processing script for SubPlayer.
Extracts audio, transcribes with Faster Whisper, and translates to Russian.
"""

import sys
import json
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from transcribe import transcribe_audio
from translate import translate_subtitles


def send_progress(stage: str, progress: float, message: str):
    """Send progress update to Electron."""
    data = {
        "stage": stage,
        "progress": progress,
        "message": message
    }
    print(f"PROGRESS:{json.dumps(data)}", flush=True)


def send_result(subtitles: list):
    """Send final result to Electron."""
    data = {"subtitles": subtitles}
    print(f"RESULT:{json.dumps(data)}", flush=True)


def process_video(video_path: str) -> list:
    """
    Process video file: extract audio, transcribe, translate.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        List of subtitle dictionaries with original and translated text
    """
    
    # Stage 1: Extract audio (Faster Whisper can handle video files directly)
    send_progress("extracting", 10, "Подготовка файла...")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    send_progress("extracting", 30, "Файл готов к обработке")
    
    # Stage 2: Transcribe with Faster Whisper
    send_progress("transcribing", 0, "Загрузка модели Faster Whisper...")
    
    def on_transcribe_progress(progress: float, message: str):
        send_progress("transcribing", progress, message)
    
    segments = transcribe_audio(video_path, on_transcribe_progress)
    
    send_progress("transcribing", 100, f"Распознано {len(segments)} сегментов")
    
    # Stage 3: Translate to Russian
    send_progress("translating", 0, "Загрузка модели перевода...")
    
    def on_translate_progress(progress: float, message: str):
        send_progress("translating", progress, message)
    
    subtitles = translate_subtitles(segments, on_translate_progress)
    
    send_progress("done", 100, "Обработка завершена!")
    
    return subtitles


def main():
    if len(sys.argv) < 2:
        print("Usage: python process.py <video_path>", file=sys.stderr)
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    try:
        subtitles = process_video(video_path)
        send_result(subtitles)
        sys.exit(0)
    except Exception as e:
        send_progress("error", 0, str(e))
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

