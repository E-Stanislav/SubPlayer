#!/usr/bin/env python3
"""
Text-to-Speech module using Silero TTS.
Generates Russian voice-over for subtitles.
"""

import os
import torch
import numpy as np
from typing import Optional, List, Dict, Any

# Global model cache
_model = None
_sample_rate = 48000


def get_tts_model():
    """Load and cache Silero TTS model."""
    global _model
    
    if _model is not None:
        return _model
    
    # Download and load Silero model
    device = torch.device('cpu')
    
    # Use v4 model for better quality
    _model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language='ru',
        speaker='v4_ru'
    )
    _model.to(device)
    
    return _model


def generate_speech(
    text: str,
    speaker: str = 'xenia',  # Options: aidar, baya, kseniya, xenia, eugene
    sample_rate: int = 48000
) -> Optional[torch.Tensor]:
    """
    Generate speech audio from Russian text.
    
    Args:
        text: Russian text to synthesize
        speaker: Voice to use (xenia is natural female, aidar is male)
        sample_rate: Output sample rate
        
    Returns:
        Audio tensor or None on error
    """
    if not text.strip():
        return None
    
    try:
        model = get_tts_model()
        
        # Generate audio
        audio = model.apply_tts(
            text=text,
            speaker=speaker,
            sample_rate=sample_rate
        )
        
        return audio
        
    except Exception as e:
        print(f"TTS error: {e}", file=__import__('sys').stderr)
        return None


def generate_speech_to_file(
    text: str,
    output_path: str,
    speaker: str = 'xenia',
    sample_rate: int = 48000
) -> bool:
    """
    Generate speech and save to WAV file.
    
    Args:
        text: Russian text to synthesize
        output_path: Path to save WAV file
        speaker: Voice to use
        sample_rate: Output sample rate
        
    Returns:
        True if successful
    """
    audio = generate_speech(text, speaker, sample_rate)
    
    if audio is None:
        return False
    
    try:
        # Use scipy to save WAV (more reliable than torchaudio)
        from scipy.io import wavfile
        
        # Convert to numpy and scale to int16
        audio_np = audio.numpy()
        if audio_np.max() > 1.0 or audio_np.min() < -1.0:
            audio_np = audio_np / max(abs(audio_np.max()), abs(audio_np.min()))
        
        audio_int16 = (audio_np * 32767).astype(np.int16)
        
        wavfile.write(output_path, sample_rate, audio_int16)
        return True
        
    except Exception as e:
        print(f"Failed to save audio: {e}", file=__import__('sys').stderr)
        return False


def generate_voiceover_for_subtitles(
    subtitles: List[Dict[str, Any]],
    output_dir: str,
    speaker: str = 'xenia',
    on_progress: callable = None
) -> List[Dict[str, Any]]:
    """
    Generate voice-over audio files for each subtitle.
    
    Args:
        subtitles: List of subtitle dicts with 'translatedText', 'start', 'end'
        output_dir: Directory to save audio files
        speaker: Voice to use
        on_progress: Progress callback (progress%, message)
        
    Returns:
        List of subtitles with added 'audioFile' field
    """
    os.makedirs(output_dir, exist_ok=True)
    
    result = []
    total = len(subtitles)
    
    for i, sub in enumerate(subtitles):
        text = sub.get('translatedText', '')
        
        if text.strip():
            audio_file = os.path.join(output_dir, f"tts_{sub['id']}.wav")
            
            if generate_speech_to_file(text, audio_file, speaker):
                sub_with_audio = {**sub, 'audioFile': audio_file}
            else:
                sub_with_audio = {**sub, 'audioFile': None}
        else:
            sub_with_audio = {**sub, 'audioFile': None}
        
        result.append(sub_with_audio)
        
        if on_progress:
            progress = (i + 1) / total * 100
            on_progress(progress, f"Озвучено: {i + 1} / {total}")
    
    return result


def preload_model():
    """Pre-load TTS model for faster first synthesis."""
    try:
        get_tts_model()
        return True
    except Exception as e:
        print(f"Failed to preload TTS model: {e}", file=__import__('sys').stderr)
        return False


# For testing
if __name__ == "__main__":
    print("Loading Silero TTS model...")
    preload_model()
    
    test_texts = [
        "Привет! Как дела?",
        "Это тестовая озвучка для субтитров.",
        "Видеоплеер с автоматическим переводом."
    ]
    
    for i, text in enumerate(test_texts):
        output = f"/tmp/test_tts_{i}.wav"
        print(f"Generating: {text}")
        if generate_speech_to_file(text, output):
            print(f"  Saved to: {output}")
        else:
            print("  Failed!")
