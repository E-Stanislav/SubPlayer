#!/usr/bin/env python3
"""
Audio transcription using Faster Whisper with streaming support.
"""

from typing import Iterator, Dict, Any
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

# Global model cache
_model = None


def get_model() -> "WhisperModel":
    """
    Load and return the Whisper model.
    Model is cached after first load.
    """
    global _model
    
    if _model is not None:
        return _model
    
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
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            # Apple Silicon - use CPU with optimizations
            device = "cpu"
            compute_type = "int8"
    except ImportError:
        pass
    
    _model = WhisperModel(
        DEFAULT_MODEL,
        device=device,
        compute_type=compute_type,
        download_root=os.path.join(os.path.dirname(__file__), "models")
    )
    
    return _model


def transcribe_audio_streaming(audio_path: str) -> Iterator[Dict[str, Any]]:
    """
    Transcribe audio/video file using Faster Whisper with streaming output.
    Yields segments as they become available.
    
    Args:
        audio_path: Path to audio or video file
        
    Yields:
        Segment dictionaries with start, end, text, progress
    """
    
    model = get_model()
    
    # Transcribe with VAD for better segmentation
    segments_generator, info = model.transcribe(
        audio_path,
        beam_size=5,
        language=None,  # Auto-detect language
        vad_filter=True,  # Voice activity detection for streaming
        vad_parameters=dict(
            min_silence_duration_ms=300,  # Shorter silence = faster segments
            speech_pad_ms=200
        )
    )
    
    total_duration = info.duration if info.duration else 1
    
    # Yield segments as they are generated
    for segment in segments_generator:
        progress = min(95, (segment.end / total_duration) * 100) if total_duration > 0 else 50
        
        yield {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "progress": progress
        }


# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_path>")
        sys.exit(1)
    
    print("Starting streaming transcription...")
    for seg in transcribe_audio_streaming(sys.argv[1]):
        print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")
