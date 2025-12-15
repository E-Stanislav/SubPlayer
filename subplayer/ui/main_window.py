"""Главное окно приложения"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QSlider, QProgressBar, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal as QSignal
from PySide6.QtGui import QAction
from subplayer.ui.mpv_widget import MPVWidget
from subplayer.media.mpv_player import MPVPlayer
from subplayer.subs.asr_fasterwhisper import FasterWhisperASR
from subplayer.translate.argos import ArgosTranslator
from subplayer.subs.srt import get_srt_path_for_media
from subplayer.util.settings import Settings
from subplayer.util.cache import Cache
from subplayer.ui.settings_dialog import SettingsDialog
from pathlib import Path


class MainWindow(QMainWindow):
    """Главное окно плеера"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SubPlayer")
        self.setMinimumSize(800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        
        # Меню
        self._create_menu()
        
        # Видео виджеты (mpv и placeholder)
        self.video_stack = QStackedWidget()
        
        # Placeholder для начального состояния
        self.video_label = QLabel("Откройте видео файл для воспроизведения")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setMinimumHeight(400)
        self.video_stack.addWidget(self.video_label)
        
        # MPV виджет
        self.mpv_widget = MPVWidget()
        self.mpv_widget.setMinimumHeight(400)
        self.video_stack.addWidget(self.mpv_widget)
        
        # Показываем placeholder
        self.video_stack.setCurrentWidget(self.video_label)
        main_layout.addWidget(self.video_stack)
        
        # MPV плеер
        self.mpv_player = None
        self._init_mpv_player()
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        # Кнопки управления
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self._toggle_play_pause)
        control_layout.addWidget(self.play_pause_btn)
        
        # Таймлайн
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(100)
        self.time_slider.valueChanged.connect(self._on_seek)
        control_layout.addWidget(self.time_slider)
        
        # Метка времени
        self.time_label = QLabel("00:00 / 00:00")
        control_layout.addWidget(self.time_label)
        
        main_layout.addLayout(control_layout)
        
        # Кнопки субтитров
        subtitle_layout = QHBoxLayout()
        
        self.generate_subs_btn = QPushButton("Сгенерировать субтитры")
        self.generate_subs_btn.setEnabled(False)
        self.generate_subs_btn.clicked.connect(self._generate_subtitles)
        subtitle_layout.addWidget(self.generate_subs_btn)
        
        self.translate_subs_btn = QPushButton("Перевести на русский")
        self.translate_subs_btn.setEnabled(False)
        self.translate_subs_btn.clicked.connect(self._translate_subtitles)
        subtitle_layout.addWidget(self.translate_subs_btn)
        
        main_layout.addLayout(subtitle_layout)
        
        # Прогресс-бар для операций
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Статус-бар
        self.statusBar().showMessage("Готов")
        
        # Таймер для обновления времени
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_time)
        self.update_timer.setInterval(100)  # 100ms
        
        # Текущий файл
        self.current_file = None
        self.is_playing = False
        self._seeking = False  # флаг для предотвращения циклов при перемотке
        
        # ASR для генерации субтитров
        self.asr = None
        self._subtitle_thread = None
        
        # Переводчик
        self.translator = None
        self._translation_thread = None
        
        # Текущий SRT файл
        self.current_srt_file = None
        
        # Настройки и кэш
        self.settings = Settings()
        self.cache = Cache() if self.settings.get('cache', 'enabled', True) else None
    
    def _create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        
        open_action = QAction("Открыть файл...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Настройки
        settings_menu = menubar.addMenu("Настройки")
        
        settings_action = QAction("Настройки...", self)
        settings_action.triggered.connect(self._show_settings)
        settings_menu.addAction(settings_action)
    
    def _init_mpv_player(self):
        """Инициализация mpv плеера"""
        try:
            # Получаем widget ID после того, как виджет показан
            # Для этого используем таймер
            QTimer.singleShot(100, self._setup_mpv_player)
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка инициализации mpv: {str(e)}")
    
    def _setup_mpv_player(self):
        """Настройка mpv плеера с виджетом"""
        try:
            widget_id = self.mpv_widget.get_widget_id()
            
            # Создаём плеер с правильным wid
            self.mpv_player = MPVPlayer(self, widget_id=widget_id)
            
            # Подключаем сигналы
            self.mpv_player.position_changed.connect(self._on_position_changed)
            self.mpv_player.duration_changed.connect(self._on_duration_changed)
            self.mpv_player.state_changed.connect(self._on_state_changed)
            self.mpv_player.error_occurred.connect(self._on_player_error)
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка настройки mpv: {str(e)}")
    
    def _on_position_changed(self, position: float):
        """Обработка изменения позиции"""
        if not self._seeking:
            duration = self.mpv_player.get_duration()
            if duration > 0:
                # Обновляем слайдер
                max_value = self.time_slider.maximum()
                new_value = int((position / duration) * max_value)
                self.time_slider.setValue(new_value)
            
            # Обновляем метку времени
            self._update_time_label()
    
    def _on_duration_changed(self, duration: float):
        """Обработка изменения длительности"""
        # Обновляем максимальное значение слайдера
        # Используем секунды * 100 для точности
        self.time_slider.setMaximum(int(duration * 100))
        self._update_time_label()
    
    def _on_state_changed(self, state: str):
        """Обработка изменения состояния"""
        if state == 'playing':
            self.is_playing = True
            self.play_pause_btn.setText("⏸")
            self.update_timer.start()
        elif state == 'paused':
            self.is_playing = False
            self.play_pause_btn.setText("▶")
            self.update_timer.stop()
        elif state == 'stopped':
            self.is_playing = False
            self.play_pause_btn.setText("▶")
            self.update_timer.stop()
    
    def _on_player_error(self, error: str):
        """Обработка ошибок плеера"""
        self.statusBar().showMessage(f"Ошибка: {error}")
    
    def _open_file(self):
        """Открытие медиа файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть медиа файл",
            "",
            "Медиа файлы (*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac);;Все файлы (*)"
        )
        
        if file_path:
            self.current_file = file_path
            self._load_file(file_path)
    
    def _load_file(self, file_path: str):
        """Загрузка файла в плеер"""
        if not self.mpv_player:
            self.statusBar().showMessage("Плеер не инициализирован. Попробуйте еще раз.")
            return
        
        self.statusBar().showMessage(f"Загрузка: {file_path}...")
        
        # Переключаемся на mpv виджет
        self.video_stack.setCurrentWidget(self.mpv_widget)
        
        # Загружаем файл
        if self.mpv_player.load_file(file_path):
            self.current_file = file_path
            self.statusBar().showMessage(f"Загружен: {file_path}")
            self.play_pause_btn.setEnabled(True)
            self.time_slider.setEnabled(True)
            self.generate_subs_btn.setEnabled(True)
        else:
            self.statusBar().showMessage("Ошибка загрузки файла")
            # Возвращаемся к placeholder
            self.video_stack.setCurrentWidget(self.video_label)
    
    def _toggle_play_pause(self):
        """Переключение воспроизведения/паузы"""
        if self.mpv_player:
            self.mpv_player.toggle_play_pause()
    
    def _on_seek(self, value: int):
        """Обработка перемотки"""
        if not self.mpv_player or self._seeking:
            return
        
        # Преобразуем значение слайдера в секунды
        max_value = self.time_slider.maximum()
        if max_value > 0:
            duration = self.mpv_player.get_duration()
            if duration > 0:
                position = (value / max_value) * duration
                self._seeking = True
                self.mpv_player.seek(position)
                # Сбрасываем флаг через небольшую задержку
                QTimer.singleShot(200, lambda: setattr(self, '_seeking', False))
    
    def _update_time(self):
        """Обновление времени воспроизведения"""
        if self.mpv_player:
            self._update_time_label()
    
    def _update_time_label(self):
        """Обновление метки времени"""
        if not self.mpv_player:
            return
        
        position = self.mpv_player.get_position()
        duration = self.mpv_player.get_duration()
        
        pos_str = self._format_time(position)
        dur_str = self._format_time(duration) if duration > 0 else "00:00"
        
        self.time_label.setText(f"{pos_str} / {dur_str}")
    
    def _format_time(self, seconds: float) -> str:
        """Форматирование времени в MM:SS"""
        total_seconds = int(seconds)
        minutes = total_seconds // 60
        secs = total_seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _show_settings(self):
        """Показать окно настроек"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Пересоздаём ASR с новыми настройками
            self.asr = None
            self.statusBar().showMessage("Настройки сохранены")
    
    def _get_asr(self) -> FasterWhisperASR:
        """Получить или создать экземпляр ASR"""
        if self.asr is None:
            model_path = self.settings.get('whisper', 'model_path')
            device = self.settings.get('whisper', 'device', 'auto')
            compute_type = self.settings.get('whisper', 'compute_type', 'default')
            self.asr = FasterWhisperASR(
                model_path=model_path,
                device=device,
                compute_type=compute_type
            )
        return self.asr
    
    def _generate_subtitles(self):
        """Генерация субтитров"""
        if not self.current_file:
            self.statusBar().showMessage("Сначала откройте медиа файл")
            return
        
        # Проверяем, не запущена ли уже генерация
        if self._subtitle_thread and self._subtitle_thread.isRunning():
            self.statusBar().showMessage("Генерация субтитров уже выполняется...")
            return
        
        media_path = Path(self.current_file)
        
        # Проверяем кэш
        if self.cache:
            params = {
                'model': self.settings.get_whisper_model(),
                'language': self.settings.get_whisper_language(),
            }
            cached_srt = self.cache.get_cached_srt(media_path, 'subtitle', params)
            if cached_srt:
                self.statusBar().showMessage("Используются закэшированные субтитры")
                self._on_subtitles_generated(cached_srt)
                return
        
        # Создаём поток для генерации
        self._subtitle_thread = SubtitleGenerationThread(
            media_path,
            self._get_asr(),
            self.settings,
            self.cache
        )
        self._subtitle_thread.progress.connect(self._on_subtitle_progress)
        self._subtitle_thread.finished.connect(self._on_subtitles_generated)
        self._subtitle_thread.error.connect(self._on_subtitle_error)
        
        # Блокируем кнопку
        self.generate_subs_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Запускаем
        self._subtitle_thread.start()
        self.statusBar().showMessage("Генерация субтитров...")
    
    def _on_subtitle_progress(self, message: str, progress: int):
        """Обработка прогресса генерации субтитров"""
        self.progress_bar.setValue(progress)
        self.statusBar().showMessage(message)
    
    def _on_subtitles_generated(self, srt_path: Path):
        """Обработка завершения генерации субтитров"""
        self.progress_bar.setVisible(False)
        self.generate_subs_btn.setEnabled(True)
        
        # Сохраняем путь к SRT файлу
        self.current_srt_file = srt_path
        
        # Загружаем субтитры в mpv
        if self.mpv_player:
            if self.mpv_player.add_subtitle_file(str(srt_path)):
                self.statusBar().showMessage(f"Субтитры загружены: {srt_path.name}")
                self.translate_subs_btn.setEnabled(True)
            else:
                self.statusBar().showMessage("Ошибка загрузки субтитров в плеер")
        else:
            self.statusBar().showMessage(f"Субтитры созданы: {srt_path.name}")
            self.translate_subs_btn.setEnabled(True)
    
    def _on_subtitle_error(self, error: str):
        """Обработка ошибки генерации субтитров"""
        self.progress_bar.setVisible(False)
        self.generate_subs_btn.setEnabled(True)
        self.statusBar().showMessage(f"Ошибка: {error}")
    
    def _get_translator(self) -> ArgosTranslator:
        """Получить или создать экземпляр переводчика"""
        if self.translator is None:
            self.translator = ArgosTranslator()
        return self.translator
    
    def _translate_subtitles(self):
        """Перевод субтитров на русский"""
        if not self.current_srt_file or not self.current_srt_file.exists():
            # Пытаемся найти SRT файл рядом с медиа файлом
            if self.current_file:
                self.current_srt_file = get_srt_path_for_media(Path(self.current_file))
                if not self.current_srt_file.exists():
                    self.statusBar().showMessage("Сначала сгенерируйте субтитры")
                    return
            else:
                self.statusBar().showMessage("Сначала откройте медиа файл и сгенерируйте субтитры")
                return
        
        # Проверяем, не запущен ли уже перевод
        if self._translation_thread and self._translation_thread.isRunning():
            self.statusBar().showMessage("Перевод уже выполняется...")
            return
        
        # Создаём поток для перевода
        self._translation_thread = TranslationThread(
            self.current_srt_file,
            self._get_translator()
        )
        self._translation_thread.progress.connect(self._on_translation_progress)
        self._translation_thread.finished.connect(self._on_translation_finished)
        self._translation_thread.error.connect(self._on_translation_error)
        
        # Блокируем кнопку
        self.translate_subs_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Запускаем
        self._translation_thread.start()
        self.statusBar().showMessage("Перевод субтитров...")
    
    def _on_translation_progress(self, message: str, progress: int):
        """Обработка прогресса перевода"""
        self.progress_bar.setValue(progress)
        self.statusBar().showMessage(message)
    
    def _on_translation_finished(self, srt_path: Path):
        """Обработка завершения перевода"""
        self.progress_bar.setVisible(False)
        self.translate_subs_btn.setEnabled(True)
        
        # Загружаем переведённые субтитры в mpv
        if self.mpv_player:
            if self.mpv_player.add_subtitle_file(str(srt_path)):
                self.statusBar().showMessage(f"Переведённые субтитры загружены: {srt_path.name}")
            else:
                self.statusBar().showMessage("Ошибка загрузки переведённых субтитров в плеер")
        else:
            self.statusBar().showMessage(f"Переведённые субтитры созданы: {srt_path.name}")
    
    def _on_translation_error(self, error: str):
        """Обработка ошибки перевода"""
        self.progress_bar.setVisible(False)
        self.translate_subs_btn.setEnabled(True)
        self.statusBar().showMessage(f"Ошибка: {error}")


class TranslationThread(QThread):
    """Поток для перевода субтитров"""
    
    progress = QSignal(str, int)  # сообщение, прогресс 0-100
    finished = QSignal(Path)  # путь к переведённому SRT файлу
    error = QSignal(str)  # сообщение об ошибке
    
    def __init__(self, srt_path: Path, translator: ArgosTranslator):
        super().__init__()
        self.srt_path = srt_path
        self.translator = translator
    
    def run(self):
        """Запуск перевода"""
        try:
            from subplayer.subs.srt import get_srt_path_for_media
            
            output_path = get_srt_path_for_media(self.srt_path, "ru")
            
            def progress_callback(message: str, progress: int):
                self.progress.emit(message, progress)
            
            self.translator.translate_srt_file(
                self.srt_path,
                output_path=output_path,
                from_lang=None,  # автоопределение
                to_lang="ru",
                progress_callback=progress_callback
            )
            
            self.finished.emit(output_path)
        
        except Exception as e:
            self.error.emit(str(e))


class SubtitleGenerationThread(QThread):
    """Поток для генерации субтитров"""
    
    progress = QSignal(str, int)  # сообщение, прогресс 0-100
    finished = QSignal(Path)  # путь к SRT файлу
    error = QSignal(str)  # сообщение об ошибке
    
    def __init__(self, media_path: Path, asr: FasterWhisperASR, settings: Settings, cache: Optional[Cache]):
        super().__init__()
        self.media_path = media_path
        self.asr = asr
        self.settings = settings
        self.cache = cache
    
    def run(self):
        """Запуск генерации субтитров"""
        try:
            from subplayer.subs.srt import get_srt_path_for_media
            
            srt_path = get_srt_path_for_media(self.media_path)
            
            def progress_callback(message: str, progress: int):
                self.progress.emit(message, progress)
            
            model = self.settings.get_whisper_model()
            language = self.settings.get_whisper_language()
            
            self.asr.generate_subtitles(
                self.media_path,
                output_srt_path=srt_path,
                language=language,
                model=model,
                progress_callback=progress_callback
            )
            
            # Сохраняем в кэш
            if self.cache:
                params = {
                    'model': model,
                    'language': language,
                }
                self.cache.cache_srt(self.media_path, srt_path, 'subtitle', params)
            
            self.finished.emit(srt_path)
        
        except Exception as e:
            self.error.emit(str(e))
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.mpv_player:
            self.mpv_player.cleanup()
        event.accept()

