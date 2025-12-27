#!/usr/bin/env python3
"""
Audio transcription using Faster Whisper.
"""

from typing import Callable, List, Dict, Any
import os

# Try to import faster_whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: faster-whisper not installed. Run: pip install faster-whisper", file=__import__('sys').stderr)


# Model configuration
DEFAULT_MODEL = "base"  # Options: tiny, base, small, medium, large-v2, large-v3
COMPUTE_TYPE = "int8"   # Use int8 for CPU, float16 for GPU


def get_model() -> "WhisperModel":
    """
    Load and return the Whisper model.
    Model is cached after first load.
    """
    if not WHISPER_AVAILABLE:
        raise ImportError("faster-whisper is not installed")
    
    # Check for GPU availability
    device = "cpu"
    compute_type = "int8"
    
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
    except ImportError:
        pass
    
    model = WhisperModel(
        DEFAULT_MODEL,
        device=device,
        compute_type=compute_type,
        download_root=os.path.join(os.path.dirname(__file__), "models")
    )
    
    return model


def transcribe_audio(
    audio_path: str,
    on_progress: Callable[[float, str], None] = None
) -> List[Dict[str, Any]]:
    """
    Transcribe audio/video file using Faster Whisper.
    
    Args:
        audio_path: Path to audio or video file
        on_progress: Callback for progress updates (progress%, message)
        
    Returns:
        List of segment dictionaries with start, end, text
    """
    
    if on_progress:
        on_progress(5, "Инициализация модели...")
    
    model = get_model()
    
    if on_progress:
        on_progress(15, "Начало распознавания речи...")
    
    # Transcribe with word timestamps for better accuracy
    segments_generator, info = model.transcribe(
        audio_path,
        beam_size=5,
        language=None,  # Auto-detect language
        vad_filter=True,  # Voice activity detection
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=400
        )
    )
    
    if on_progress:
        detected_lang = info.language
        on_progress(25, f"Обнаружен язык: {detected_lang}")
    
    # Convert generator to list and track progress
    segments = []
    total_duration = info.duration if info.duration else 0
    
    for segment in segments_generator:
        segments.append({
            "id": len(segments) + 1,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
        
        # Calculate progress based on segment end time
        if total_duration > 0 and on_progress:
            progress = min(95, 25 + (segment.end / total_duration) * 70)
            on_progress(progress, f"Обработано: {segment.end:.1f}s / {total_duration:.1f}s")
    
    if on_progress:
        on_progress(100, f"Распознано {len(segments)} сегментов")
    
    return segments


# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_path>")
        sys.exit(1)
    
    def progress_callback(progress: float, message: str):
        print(f"[{progress:.0f}%] {message}")
    
    result = transcribe_audio(sys.argv[1], progress_callback)
    
    print("\n--- Results ---")
    for seg in result:
        print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")

