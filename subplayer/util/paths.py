"""Утилиты для работы с путями"""
import os
from pathlib import Path
from platform import system


def get_app_data_dir() -> Path:
    """Получить директорию для данных приложения"""
    system_name = system()
    
    if system_name == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system_name == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux и другие
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    
    app_dir = base / "SubPlayer"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_cache_dir() -> Path:
    """Получить директорию для кэша"""
    cache_dir = get_app_data_dir() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_temp_dir() -> Path:
    """Получить временную директорию"""
    temp_dir = get_app_data_dir() / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir

