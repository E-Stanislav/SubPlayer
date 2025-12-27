#!/usr/bin/env python3
"""
Translation module using Argos Translate with streaming support.
Translates subtitles to Russian one at a time for low latency.
"""

from typing import Optional
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
DEFAULT_SOURCE_LANG = "en"

# Global translation cache
_translator = None
_source_lang = None


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


def ensure_language_package(from_code: str, to_code: str) -> bool:
    """
    Ensure the translation package is installed.
    Downloads if necessary.
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


def get_translator(from_code: str):
    """Get or create translator for the given source language."""
    global _translator, _source_lang
    
    if _translator is not None and _source_lang == from_code:
        return _translator
    
    if not ARGOS_AVAILABLE:
        return None
    
    if from_code == TARGET_LANG:
        return None  # No translation needed
    
    installed = argostranslate.translate.get_installed_languages()
    from_lang = next((l for l in installed if l.code == from_code), None)
    to_lang = next((l for l in installed if l.code == TARGET_LANG), None)
    
    if from_lang and to_lang:
        _translator = from_lang.get_translation(to_lang)
        _source_lang = from_code
        return _translator
    
    return None


def ensure_translation_ready(source_lang: str = DEFAULT_SOURCE_LANG) -> str:
    """
    Pre-load translation model for faster first translation.
    Returns detected/default source language.
    """
    if not ARGOS_AVAILABLE:
        return source_lang
    
    # Ensure package is installed
    ensure_language_package(source_lang, TARGET_LANG)
    
    # Pre-load translator
    get_translator(source_lang)
    
    return source_lang


def translate_text_single(text: str, source_lang: Optional[str] = None) -> str:
    """
    Translate a single text string to Russian.
    Optimized for low latency in streaming mode.
    
    Args:
        text: Text to translate
        source_lang: Source language code (auto-detect if None)
        
    Returns:
        Translated text
    """
    if not text.strip():
        return text
    
    # Detect language if not provided
    if source_lang is None:
        source_lang = detect_language(text)
    
    # No translation needed if already Russian
    if source_lang == TARGET_LANG:
        return text
    
    # Get translator
    translator = get_translator(source_lang)
    
    if translator is None:
        # Try to install package on-the-fly
        if ensure_language_package(source_lang, TARGET_LANG):
            translator = get_translator(source_lang)
    
    if translator:
        try:
            return translator.translate(text)
        except Exception as e:
            print(f"Translation error: {e}", file=__import__('sys').stderr)
    
    return text  # Return original on error


# For testing
if __name__ == "__main__":
    print("Testing translation...")
    
    # Ensure model is ready
    ensure_translation_ready("en")
    
    test_texts = [
        "Hello, how are you?",
        "This is a test of the streaming translation system.",
        "The quick brown fox jumps over the lazy dog."
    ]
    
    for text in test_texts:
        translated = translate_text_single(text, "en")
        print(f"EN: {text}")
        print(f"RU: {translated}")
        print()
