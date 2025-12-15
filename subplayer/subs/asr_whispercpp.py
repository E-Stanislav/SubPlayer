"""Генерация субтитров через whisper.cpp"""
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
import json
import tempfile
from subplayer.subs.srt import SubtitleSegment, write_srt_file
from subplayer.util.paths import get_temp_dir


class WhisperCppASR:
    """Класс для генерации субтитров через whisper.cpp"""
    
    def __init__(self, whisper_cpp_path: Optional[str] = None, model_path: Optional[str] = None):
        """
        Инициализация
        
        Args:
            whisper_cpp_path: путь к исполняемому файлу whisper.cpp (если None, ищет в PATH)
            model_path: путь к модели Whisper (если None, использует модель по умолчанию)
        """
        self.whisper_cpp_path = whisper_cpp_path or self._find_whisper_cpp()
        self.model_path = model_path
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_whisper_cpp(self) -> Optional[str]:
        """Найти whisper.cpp в системе"""
        # Сначала проверяем рядом с приложением (для portable версии)
        import sys
        if getattr(sys, 'frozen', False):
            # Запущено из PyInstaller
            app_dir = Path(sys._MEIPASS)
            for name in ['whisper', 'whisper.exe']:
                exe_path = app_dir / name
                if exe_path.exists():
                    return str(exe_path)
        
        # Проверяем стандартные имена в PATH
        for name in ['whisper', 'whisper.cpp', 'main']:
            path = shutil.which(name)
            if path:
                return path
        return None
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Найти ffmpeg в системе"""
        # Сначала проверяем рядом с приложением (для portable версии)
        import sys
        if getattr(sys, 'frozen', False):
            # Запущено из PyInstaller
            app_dir = Path(sys._MEIPASS)
            for name in ['ffmpeg', 'ffmpeg.exe']:
                exe_path = app_dir / name
                if exe_path.exists():
                    return str(exe_path)
        
        # Проверяем стандартные имена в PATH
        path = shutil.which('ffmpeg')
        if not path:
            # Пробуем альтернативные имена
            for name in ['ffmpeg.exe', 'ffmpeg']:
                path = shutil.which(name)
                if path:
                    return path
        return path
    
    def extract_audio(self, media_path: Path, output_path: Path) -> bool:
        """
        Извлечь аудио из медиа файла
        
        Args:
            media_path: путь к медиа файлу
            output_path: путь для сохранения аудио (WAV, 16kHz, mono)
        
        Returns:
            True если успешно
        """
        if not self.ffmpeg_path:
            raise RuntimeError("ffmpeg не найден. Установите ffmpeg.")
        
        if not media_path.exists():
            raise FileNotFoundError(f"Медиа файл не найден: {media_path}")
        
        try:
            # Извлекаем аудио в формат, подходящий для whisper.cpp
            # 16kHz, mono, WAV
            cmd = [
                self.ffmpeg_path,
                '-i', str(media_path),
                '-ar', '16000',  # sample rate
                '-ac', '1',  # mono
                '-f', 'wav',  # формат
                '-y',  # перезаписать если существует
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка извлечения аудио: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("ffmpeg не найден")
    
    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        model: str = "base",
        output_format: str = "srt"
    ) -> List[SubtitleSegment]:
        """
        Транскрибировать аудио
        
        Args:
            audio_path: путь к аудио файлу
            language: код языка (например, 'en', 'ru', 'auto' для автоопределения)
            model: модель Whisper (tiny, base, small, medium, large)
            output_format: формат вывода ('srt', 'json', 'txt')
        
        Returns:
            Список сегментов субтитров
        """
        if not self.whisper_cpp_path:
            raise RuntimeError("whisper.cpp не найден. Установите whisper.cpp.")
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Аудио файл не найден: {audio_path}")
        
        # Определяем модель
        if self.model_path:
            model_path = Path(self.model_path)
        else:
            # Используем стандартный путь к моделям
            # Обычно модели находятся в ~/.cache/whisper или рядом с бинарником
            model_path = self._get_default_model_path(model)
        
        if not model_path or not model_path.exists():
            raise FileNotFoundError(f"Модель не найдена: {model_path}")
        
        # Создаём временный файл для вывода
        temp_dir = get_temp_dir()
        output_file = temp_dir / f"whisper_output_{audio_path.stem}.{output_format}"
        
        try:
            # Команда whisper.cpp
            cmd = [
                self.whisper_cpp_path,
                '-m', str(model_path),
                '-f', str(audio_path),
                '-of', str(output_file.parent / output_file.stem),
                '-otxt',  # текстовый вывод
                '-osrt',  # SRT вывод
            ]
            
            # Добавляем язык если указан
            if language and language != 'auto':
                cmd.extend(['-l', language])
            
            # Запускаем whisper.cpp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=3600  # таймаут 1 час
            )
            
            # Читаем результат
            srt_file = output_file.with_suffix('.srt')
            if srt_file.exists():
                from subplayer.subs.srt import parse_srt_file
                segments = parse_srt_file(srt_file)
                return segments
            else:
                raise RuntimeError(f"SRT файл не создан: {srt_file}")
        
        except subprocess.TimeoutExpired:
            raise RuntimeError("Таймаут при транскрибации")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка транскрибации: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("whisper.cpp не найден")
    
    def _get_default_model_path(self, model: str) -> Optional[Path]:
        """Получить путь к модели по умолчанию"""
        # Сначала проверяем рядом с приложением (для portable версии)
        import sys
        if getattr(sys, 'frozen', False):
            # Запущено из PyInstaller
            app_dir = Path(sys._MEIPASS)
            model_paths = [
                app_dir / "models" / f"ggml-{model}.bin",
                app_dir / "models" / f"ggml-{model}.q4_0.bin",
            ]
            for path in model_paths:
                if path.exists():
                    return path
        
        # Проверяем стандартные места
        possible_paths = [
            Path.home() / ".cache" / "whisper" / f"ggml-{model}.bin",
            Path.home() / ".cache" / "whisper" / f"ggml-{model}.q4_0.bin",
        ]
        
        # Если есть путь к whisper.cpp, проверяем рядом
        if self.whisper_cpp_path:
            whisper_path = Path(self.whisper_cpp_path)
            possible_paths.extend([
                whisper_path.parent / "models" / f"ggml-{model}.bin",
                whisper_path.parent.parent / "models" / f"ggml-{model}.bin",
            ])
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def generate_subtitles(
        self,
        media_path: Path,
        output_srt_path: Optional[Path] = None,
        language: Optional[str] = None,
        model: str = "base",
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        Полный пайплайн: извлечение аудио + транскрибация + сохранение SRT
        
        Args:
            media_path: путь к медиа файлу
            output_srt_path: путь для сохранения SRT (если None, создаётся рядом с медиа)
            language: код языка
            model: модель Whisper
            progress_callback: функция для обновления прогресса (принимает сообщение, прогресс 0-100)
        
        Returns:
            Путь к созданному SRT файлу
        """
        if progress_callback:
            progress_callback("Извлечение аудио...", 10)
        
        # Извлекаем аудио
        temp_dir = get_temp_dir()
        audio_file = temp_dir / f"{media_path.stem}_audio.wav"
        
        try:
            self.extract_audio(media_path, audio_file)
            
            if progress_callback:
                progress_callback("Транскрибация аудио...", 30)
            
            # Транскрибируем
            segments = self.transcribe(audio_file, language=language, model=model)
            
            if progress_callback:
                progress_callback("Сохранение субтитров...", 90)
            
            # Сохраняем SRT
            if output_srt_path is None:
                output_srt_path = media_path.parent / f"{media_path.stem}.srt"
            
            write_srt_file(output_srt_path, segments)
            
            if progress_callback:
                progress_callback("Готово", 100)
            
            return output_srt_path
        
        finally:
            # Удаляем временный аудио файл
            if audio_file.exists():
                try:
                    audio_file.unlink()
                except:
                    pass

