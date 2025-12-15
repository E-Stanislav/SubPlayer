"""Генерация субтитров через faster-whisper"""
from pathlib import Path
from typing import Optional, List
import shutil
from faster_whisper import WhisperModel
from subplayer.subs.srt import SubtitleSegment, write_srt_file
from subplayer.util.paths import get_temp_dir


class FasterWhisperASR:
    """Класс для генерации субтитров через faster-whisper"""
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto", compute_type: str = "default"):
        """
        Инициализация
        
        Args:
            model_path: путь к модели Whisper (если None, скачивается автоматически)
            device: устройство для вычислений ('cpu', 'cuda', 'auto')
            compute_type: тип вычислений ('int8', 'int8_float16', 'int16', 'float16', 'default')
        """
        self.model_path = model_path
        self.device = device
        self.compute_type = compute_type
        self._model = None
        self.ffmpeg_path = self._find_ffmpeg()
    
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
            for name in ['ffmpeg.exe', 'ffmpeg']:
                path = shutil.which(name)
                if path:
                    return path
        return path
    
    def _get_model(self, model_name: str = "base"):
        """Получить или загрузить модель"""
        # Используем кэшированную модель если она уже загружена
        if self._model is not None:
            return self._model
        
        # Определяем путь к модели
        if self.model_path:
            model_path = self.model_path
        else:
            # Используем стандартное имя модели (будет скачано автоматически)
            model_path = model_name
        
        # Загружаем модель
        self._model = WhisperModel(
            model_path,
            device=self.device,
            compute_type=self.compute_type
        )
        
        return self._model
    
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
            import subprocess
            
            # Извлекаем аудио в формат, подходящий для Whisper
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
        beam_size: int = 5,
        vad_filter: bool = True
    ) -> List[SubtitleSegment]:
        """
        Транскрибировать аудио
        
        Args:
            audio_path: путь к аудио файлу
            language: код языка (например, 'en', 'ru', None для автоопределения)
            model: модель Whisper (tiny, base, small, medium, large-v2, large-v3)
            beam_size: размер луча для поиска (больше = точнее, но медленнее)
            vad_filter: использовать VAD фильтр для удаления тишины
        
        Returns:
            Список сегментов субтитров
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Аудио файл не найден: {audio_path}")
        
        try:
            # Загружаем модель
            whisper_model = self._get_model(model)
            
            # Транскрибируем
            segments, info = whisper_model.transcribe(
                str(audio_path),
                language=language,
                beam_size=beam_size,
                vad_filter=vad_filter,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Конвертируем в SubtitleSegment
            subtitle_segments = []
            index = 1
            
            for segment in segments:
                subtitle_segments.append(SubtitleSegment(
                    index=index,
                    start_time=segment.start,
                    end_time=segment.end,
                    text=segment.text.strip()
                ))
                index += 1
            
            return subtitle_segments
        
        except Exception as e:
            raise RuntimeError(f"Ошибка транскрибации: {str(e)}")
    
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
                progress_callback("Загрузка модели Whisper...", 20)
            
            # Загружаем модель (если еще не загружена)
            self._get_model(model)
            
            if progress_callback:
                progress_callback("Транскрибация аудио...", 30)
            
            # Транскрибируем
            segments = self.transcribe(audio_file, language=language, model=model)
            
            if progress_callback:
                progress_callback("Сохранение субтитров...", 90)
            
            # Сохраняем SRT
            if output_srt_path is None:
                from subplayer.subs.srt import get_srt_path_for_media
                output_srt_path = get_srt_path_for_media(media_path)
            
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

