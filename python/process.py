#!/usr/bin/env python3
"""
Main processing script for SubPlayer with streaming and TTS support.
Outputs subtitles as they are ready, with optional voice-over generation.
"""

import sys
import json
import os
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from transcribe import transcribe_audio_streaming
from translate import translate_text_single, ensure_translation_ready

# TTS is optional - only import if needed
TTS_AVAILABLE = False
try:
    from tts import generate_speech_to_file, preload_model as preload_tts
    TTS_AVAILABLE = True
except ImportError:
    pass


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


def process_video_streaming(video_path: str, enable_tts: bool = False) -> list:
    """
    Process video file with streaming output.
    Subtitles are sent to UI as soon as they are ready.
    
    Args:
        video_path: Path to the video file
        enable_tts: Whether to generate TTS audio for each subtitle
        
    Returns:
        List of all subtitle dictionaries
    """
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    send_progress("extracting", 10, "Подготовка файла...")
    
    # Pre-load translation model
    send_progress("extracting", 30, "Загрузка модели перевода...")
    source_lang = ensure_translation_ready()
    
    # Pre-load TTS model if enabled
    tts_dir = None
    if enable_tts and TTS_AVAILABLE:
        send_progress("extracting", 50, "Загрузка модели озвучки...")
        try:
            preload_tts()
            # Create temp directory for TTS audio files
            tts_dir = tempfile.mkdtemp(prefix="subplayer_tts_")
        except Exception as e:
            print(f"TTS preload failed: {e}", file=sys.stderr)
            enable_tts = False
    
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
            "translatedText": translated,
            "audioFile": None
        }
        
        # Generate TTS if enabled
        if enable_tts and tts_dir and translated.strip():
            try:
                audio_path = os.path.join(tts_dir, f"tts_{subtitle_id}.wav")
                print(f"DEBUG: Generating TTS to {audio_path}", file=sys.stderr)
                if generate_speech_to_file(translated, audio_path):
                    subtitle["audioFile"] = audio_path
                    print(f"DEBUG: TTS saved, audioFile={audio_path}", file=sys.stderr)
                else:
                    print(f"DEBUG: TTS generation returned False", file=sys.stderr)
            except Exception as e:
                print(f"TTS generation failed for segment {subtitle_id}: {e}", file=sys.stderr)
        
        all_subtitles.append(subtitle)
        
        # Send subtitle immediately to UI
        send_subtitle(subtitle)
        
        # Update progress
        send_progress(
            "transcribing",
            min(95, segment.get("progress", 50)),
            f"Обработано: {segment['end']:.1f}s" + (" (с озвучкой)" if enable_tts else "")
        )
    
    send_progress("done", 100, f"Готово! {len(all_subtitles)} субтитров")
    
    return all_subtitles


def main():
    if len(sys.argv) < 2:
        print("Usage: python process.py <video_path> [--tts]", file=sys.stderr)
        sys.exit(1)
    
    video_path = sys.argv[1]
    enable_tts = "--tts" in sys.argv
    
    # Debug logging
    print(f"DEBUG: args={sys.argv}", file=sys.stderr)
    print(f"DEBUG: enable_tts={enable_tts}, TTS_AVAILABLE={TTS_AVAILABLE}", file=sys.stderr)
    
    try:
        subtitles = process_video_streaming(video_path, enable_tts)
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
