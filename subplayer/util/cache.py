"""Кэширование результатов генерации субтитров и перевода"""
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from subplayer.util.paths import get_cache_dir


class Cache:
    """Класс для кэширования результатов"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация кэша
        
        Args:
            cache_dir: директория для кэша (если None, используется стандартная)
        """
        self.cache_dir = cache_dir or get_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self._metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Загрузить метаданные кэша"""
        if self.metadata_file.exists():
            try:
                return json.loads(self.metadata_file.read_text(encoding='utf-8'))
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Сохранить метаданные кэша"""
        try:
            self.metadata_file.write_text(
                json.dumps(self._metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Ошибка сохранения метаданных кэша: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Получить хэш файла (по пути, размеру и времени модификации)"""
        try:
            stat = file_path.stat()
            # Используем путь, размер и время модификации
            data = f"{file_path.absolute()}{stat.st_size}{stat.st_mtime}"
            return hashlib.md5(data.encode()).hexdigest()
        except:
            return hashlib.md5(str(file_path.absolute()).encode()).hexdigest()
    
    def _get_cache_key(
        self,
        file_path: Path,
        operation: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Получить ключ кэша
        
        Args:
            file_path: путь к медиа файлу
            operation: тип операции ('subtitle' или 'translation')
            params: параметры операции (модель, язык и т.д.)
        
        Returns:
            Ключ кэша
        """
        file_hash = self._get_file_hash(file_path)
        params_str = json.dumps(params, sort_keys=True)
        key_data = f"{operation}:{file_hash}:{params_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_srt(
        self,
        media_path: Path,
        operation: str,
        params: Dict[str, Any]
    ) -> Optional[Path]:
        """
        Получить закэшированный SRT файл
        
        Args:
            media_path: путь к медиа файлу
            operation: тип операции ('subtitle' или 'translation')
            params: параметры операции
        
        Returns:
            Путь к SRT файлу или None если не найден
        """
        cache_key = self._get_cache_key(media_path, operation, params)
        
        if cache_key in self._metadata:
            cached_path = Path(self._metadata[cache_key]['srt_path'])
            if cached_path.exists():
                return cached_path
        
        return None
    
    def cache_srt(
        self,
        media_path: Path,
        srt_path: Path,
        operation: str,
        params: Dict[str, Any]
    ):
        """
        Сохранить SRT файл в кэш
        
        Args:
            media_path: путь к медиа файлу
            srt_path: путь к SRT файлу
            operation: тип операции
            params: параметры операции
        """
        cache_key = self._get_cache_key(media_path, operation, params)
        
        self._metadata[cache_key] = {
            'media_path': str(media_path.absolute()),
            'srt_path': str(srt_path.absolute()),
            'operation': operation,
            'params': params
        }
        
        self._save_metadata()
    
    def clear_cache(self):
        """Очистить весь кэш"""
        try:
            # Удаляем все SRT файлы из кэша
            for cache_key, info in list(self._metadata.items()):
                srt_path = Path(info.get('srt_path', ''))
                if srt_path.exists():
                    try:
                        srt_path.unlink()
                    except:
                        pass
            
            # Очищаем метаданные
            self._metadata = {}
            self._save_metadata()
        except Exception as e:
            print(f"Ошибка очистки кэша: {e}")
    
    def get_cache_size(self) -> int:
        """Получить размер кэша в байтах"""
        total_size = 0
        for cache_key, info in self._metadata.items():
            srt_path = Path(info.get('srt_path', ''))
            if srt_path.exists():
                try:
                    total_size += srt_path.stat().st_size
                except:
                    pass
        return total_size

