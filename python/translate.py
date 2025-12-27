#!/usr/bin/env python3
"""
Translation module using Argos Translate.
Translates subtitles to Russian.
"""

from typing import Callable, List, Dict, Any
import os

# Try to import argostranslate
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    print("Warning: argostranslate not installed. Run: pip install argostranslate", file=__import__('sys').stderr)


# Language codes
TARGET_LANG = "ru"
# Common source languages to support
SOURCE_LANGS = ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"]


def ensure_language_package(from_code: str, to_code: str) -> bool:
    """
    Ensure the translation package is installed.
    Downloads if necessary.
    
    Args:
        from_code: Source language code
        to_code: Target language code
        
    Returns:
        True if package is available, False otherwise
    """
    if not ARGOS_AVAILABLE:
        return False
    
    # Check if already installed
    installed = argostranslate.translate.get_installed_languages()
    from_lang = next((l for l in installed if l.code == from_code), None)
    to_lang = next((l for l in installed if l.code == to_code), None)
    
    if from_lang and to_lang:
        translation = from_lang.get_translation(to_lang)
        if translation:
            return True
    
    # Try to download and install
    try:
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()
        
        package = next(
            (p for p in available if p.from_code == from_code and p.to_code == to_code),
            None
        )
        
        if package:
            argostranslate.package.install_from_path(package.download())
            return True
    except Exception as e:
        print(f"Failed to install language package: {e}", file=__import__('sys').stderr)
    
    return False


def detect_language(text: str) -> str:
    """
    Simple language detection based on character analysis.
    Returns language code.
    """
    # Check for Cyrillic (Russian)
    if any('\u0400' <= c <= '\u04FF' for c in text):
        return "ru"
    
    # Check for CJK characters
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"
    
    # Check for Japanese (Hiragana/Katakana)
    if any('\u3040' <= c <= '\u30ff' for c in text):
        return "ja"
    
    # Check for Korean (Hangul)
    if any('\uac00' <= c <= '\ud7af' for c in text):
        return "ko"
    
    # Default to English for Latin scripts
    return "en"


def translate_text(text: str, from_code: str, to_code: str) -> str:
    """
    Translate text from one language to another.
    
    Args:
        text: Text to translate
        from_code: Source language code
        to_code: Target language code
        
    Returns:
        Translated text
    """
    if not ARGOS_AVAILABLE:
        return text  # Return original if translation not available
    
    if from_code == to_code:
        return text  # No translation needed
    
    try:
        installed = argostranslate.translate.get_installed_languages()
        from_lang = next((l for l in installed if l.code == from_code), None)
        to_lang = next((l for l in installed if l.code == to_code), None)
        
        if from_lang and to_lang:
            translation = from_lang.get_translation(to_lang)
            if translation:
                return translation.translate(text)
    except Exception as e:
        print(f"Translation error: {e}", file=__import__('sys').stderr)
    
    return text  # Return original on error


def translate_subtitles(
    segments: List[Dict[str, Any]],
    on_progress: Callable[[float, str], None] = None
) -> List[Dict[str, Any]]:
    """
    Translate subtitle segments to Russian.
    
    Args:
        segments: List of subtitle segments with 'text' field
        on_progress: Callback for progress updates
        
    Returns:
        List of segments with added 'translatedText' field
    """
    
    if not segments:
        return []
    
    if on_progress:
        on_progress(5, "Определение языка...")
    
    # Detect source language from first few segments
    sample_text = " ".join(seg["text"] for seg in segments[:5])
    source_lang = detect_language(sample_text)
    
    if on_progress:
        on_progress(10, f"Исходный язык: {source_lang}")
    
    # If already Russian, no translation needed
    if source_lang == "ru":
        if on_progress:
            on_progress(100, "Перевод не требуется (уже на русском)")
        return [
            {**seg, "translatedText": seg["text"]}
            for seg in segments
        ]
    
    # Ensure translation package is available
    if on_progress:
        on_progress(15, "Проверка модели перевода...")
    
    if not ensure_language_package(source_lang, TARGET_LANG):
        if on_progress:
            on_progress(100, f"Модель перевода {source_lang}→ru недоступна")
        return [
            {**seg, "translatedText": seg["text"]}
            for seg in segments
        ]
    
    if on_progress:
        on_progress(20, "Начало перевода...")
    
    # Translate each segment
    result = []
    total = len(segments)
    
    for i, seg in enumerate(segments):
        translated = translate_text(seg["text"], source_lang, TARGET_LANG)
        result.append({
            **seg,
            "translatedText": translated
        })
        
        if on_progress:
            progress = 20 + (i + 1) / total * 80
            on_progress(progress, f"Переведено: {i + 1} / {total}")
    
    if on_progress:
        on_progress(100, f"Переведено {len(result)} сегментов")
    
    return result


# For testing
if __name__ == "__main__":
    test_segments = [
        {"id": 1, "start": 0.0, "end": 2.5, "text": "Hello, how are you?"},
        {"id": 2, "start": 2.5, "end": 5.0, "text": "I'm doing great, thanks!"},
        {"id": 3, "start": 5.0, "end": 8.0, "text": "Let's learn something new today."}
    ]
    
    def progress_callback(progress: float, message: str):
        print(f"[{progress:.0f}%] {message}")
    
    result = translate_subtitles(test_segments, progress_callback)
    
    print("\n--- Results ---")
    for seg in result:
        print(f"[{seg['id']}] {seg['text']}")
        print(f"    → {seg['translatedText']}")

