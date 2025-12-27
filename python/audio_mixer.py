#!/usr/bin/env python3
"""
Audio mixer module for combining original audio with TTS voice-over.
"""

import os
import subprocess
import tempfile
from typing import List, Dict, Any, Optional


def extract_audio_from_video(video_path: str, output_path: str) -> bool:
    """
    Extract audio track from video using ffmpeg.
    
    Args:
        video_path: Path to video file
        output_path: Path to save extracted audio (WAV)
        
    Returns:
        True if successful
    """
    try:
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM WAV
            '-ar', '48000',  # 48kHz
            '-ac', '2',  # Stereo
            output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"Failed to extract audio: {e}", file=__import__('sys').stderr)
        return False


def create_dubbed_audio(
    original_audio: str,
    subtitles_with_audio: List[Dict[str, Any]],
    output_path: str,
    original_volume: float = 0.15,  # 15% of original volume (background)
    tts_volume: float = 1.0
) -> bool:
    """
    Create dubbed audio by mixing original (quiet) with TTS voice-over.
    
    Args:
        original_audio: Path to original audio WAV
        subtitles_with_audio: List of subtitles with 'audioFile', 'start', 'end'
        output_path: Path to save mixed audio
        original_volume: Volume of original audio (0.0-1.0)
        tts_volume: Volume of TTS audio (0.0-1.0)
        
    Returns:
        True if successful
    """
    try:
        from pydub import AudioSegment
        
        # Load original audio
        original = AudioSegment.from_wav(original_audio)
        
        # Lower original volume (keep as background)
        original_db_change = 20 * __import__('math').log10(original_volume) if original_volume > 0 else -60
        background = original + original_db_change
        
        # Create output audio starting with background
        output = background
        
        # Overlay TTS segments
        for sub in subtitles_with_audio:
            audio_file = sub.get('audioFile')
            if not audio_file or not os.path.exists(audio_file):
                continue
            
            start_ms = int(sub['start'] * 1000)
            end_ms = int(sub['end'] * 1000)
            duration_ms = end_ms - start_ms
            
            # Load TTS audio
            tts = AudioSegment.from_wav(audio_file)
            
            # Adjust TTS speed if needed to fit duration
            if len(tts) > duration_ms * 1.2:  # If TTS is >20% longer
                # Speed up (simple approach: truncate for now)
                tts = tts[:duration_ms]
            
            # Apply TTS volume
            if tts_volume != 1.0:
                tts_db_change = 20 * __import__('math').log10(tts_volume) if tts_volume > 0 else -60
                tts = tts + tts_db_change
            
            # Overlay at the correct position
            output = output.overlay(tts, position=start_ms)
        
        # Export
        output.export(output_path, format='wav')
        return True
        
    except Exception as e:
        print(f"Failed to mix audio: {e}", file=__import__('sys').stderr)
        import traceback
        traceback.print_exc()
        return False


def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    except:
        return 0.0


# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_mixer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_audio = "/tmp/extracted_audio.wav"
    
    print(f"Extracting audio from {video_path}...")
    if extract_audio_from_video(video_path, output_audio):
        print(f"Saved to: {output_audio}")
        print(f"Duration: {get_audio_duration(output_audio):.2f}s")
    else:
        print("Failed!")

