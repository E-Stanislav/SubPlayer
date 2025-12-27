#!/usr/bin/env python3
"""
Main processing script for SubPlayer with streaming support.
Outputs subtitles as they are ready, allowing immediate playback.
"""

import sys
import json
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from transcribe import transcribe_audio_streaming
from translate import translate_text_single, ensure_translation_ready


def send_progress(stage: str, progress: float, message: str):
    """Send progress update to Electron."""
    data = {
        "stage": stage,
        "progress": progress,
        "message": message
    }
    print(f"PROGRESS:{json.dumps(data)}", flush=True)


def send_subtitle(subtitle: dict):
    """Send a single subtitle to Electron (streaming mode)."""
    print(f"SUBTITLE:{json.dumps(subtitle)}", flush=True)


def send_result(subtitles: list):
    """Send final result to Electron."""
    data = {"subtitles": subtitles}
    print(f"RESULT:{json.dumps(data)}", flush=True)


def process_video_streaming(video_path: str) -> list:
    """
    Process video file with streaming output.
    Subtitles are sent to UI as soon as they are ready.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        List of all subtitle dictionaries
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    send_progress("extracting", 20, "Подготовка файла...")
    
    # Pre-load translation model
    send_progress("extracting", 40, "Загрузка модели перевода...")
    source_lang = ensure_translation_ready()
    
    send_progress("transcribing", 0, "Запуск распознавания речи...")
    
    all_subtitles = []
    subtitle_id = 0
    
    # Stream transcription results
    for segment in transcribe_audio_streaming(video_path):
        subtitle_id += 1
        
        # Translate immediately
        translated = translate_text_single(segment["text"], source_lang)
        
        subtitle = {
            "id": subtitle_id,
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"],
            "translatedText": translated
        }
        
        all_subtitles.append(subtitle)
        
        # Send subtitle immediately to UI
        send_subtitle(subtitle)
        
        # Update progress
        send_progress(
            "transcribing",
            min(95, segment.get("progress", 50)),
            f"Обработано: {segment['end']:.1f}s"
        )
    
    send_progress("done", 100, f"Готово! {len(all_subtitles)} субтитров")
    
    return all_subtitles


def main():
    if len(sys.argv) < 2:
        print("Usage: python process.py <video_path>", file=sys.stderr)
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    try:
        subtitles = process_video_streaming(video_path)
        send_result(subtitles)
        sys.exit(0)
    except Exception as e:
        send_progress("error", 0, str(e))
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
