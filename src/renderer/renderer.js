const openFileBtn = document.getElementById('openFileBtn');
const mediaPlayer = document.getElementById('mediaPlayer');
const playerContainer = document.getElementById('playerContainer');
const emptyState = document.getElementById('emptyState');
const fileName = document.getElementById('fileName');
const filePath = document.getElementById('filePath');

// Элементы субтитров
const subtitleControls = document.getElementById('subtitleControls');
const openSubtitleBtn = document.getElementById('openSubtitleBtn');
const newSubtitleBtn = document.getElementById('newSubtitleBtn');
const saveSubtitleBtn = document.getElementById('saveSubtitleBtn');
const toggleEditorBtn = document.getElementById('toggleEditorBtn');
const subtitleEditor = document.getElementById('subtitleEditor');
const subtitleList = document.getElementById('subtitleList');
const subtitleDisplay = document.getElementById('subtitleDisplay');
const addSubtitleBtn = document.getElementById('addSubtitleBtn');

// Данные субтитров
let subtitles = [];
let subtitleUpdateInterval = null;
let activeSubtitleIndex = -1;
let subtitleSystemInitialized = false;

// Обработчик открытия файла
openFileBtn.addEventListener('click', async () => {
    try {
        const filePath = await window.electronAPI.openFileDialog();
        
        if (filePath) {
            loadMediaFile(filePath);
        }
    } catch (error) {
        console.error('Ошибка при открытии файла:', error);
        alert('Не удалось открыть файл. Пожалуйста, попробуйте еще раз.');
    }
});

// Загрузка медиа файла
function loadMediaFile(path) {
    // Определяем тип файла
    const extension = path.split('.').pop().toLowerCase();
    const audioExtensions = ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'];
    const isAudio = audioExtensions.includes(extension);

    // Устанавливаем источник (исправляем путь для Electron)
    // В Electron нужно использовать правильный формат пути
    let filePathFormatted = path.replace(/\\/g, '/');
    // Убираем лишние слеши и добавляем протокол
    if (!filePathFormatted.startsWith('/')) {
        filePathFormatted = '/' + filePathFormatted;
    }
    // Для Windows дисков (C:/, D:/ и т.д.)
    filePathFormatted = filePathFormatted.replace(/^\/+([A-Za-z]:\/)/, '$1');
    mediaPlayer.src = `file://${filePathFormatted}`;
    
    // Если это аудио, добавляем специальную обертку
    if (isAudio) {
        mediaPlayer.style.display = 'none';
        if (!document.querySelector('.audio-wrapper')) {
            const audioWrapper = document.createElement('div');
            audioWrapper.className = 'audio-wrapper';
            audioWrapper.innerHTML = `
                <div class="audio-visualizer">
                    <div class="audio-wave">
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                    </div>
                </div>
            `;
            mediaPlayer.parentNode.insertBefore(audioWrapper, mediaPlayer);
            
            // Добавляем стили для аудио визуализатора
            if (!document.querySelector('#audio-styles')) {
                const style = document.createElement('style');
                style.id = 'audio-styles';
                style.textContent = `
                    .audio-wrapper {
                        width: 100%;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 12px;
                        padding: 60px 40px;
                        margin-bottom: 20px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .audio-visualizer {
                        width: 100%;
                    }
                    .audio-wave {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        gap: 10px;
                        height: 200px;
                    }
                    .wave-bar {
                        width: 8px;
                        background: white;
                        border-radius: 4px;
                        animation: wave 1.2s ease-in-out infinite;
                        opacity: 0.8;
                    }
                    .wave-bar:nth-child(1) { animation-delay: 0s; height: 60px; }
                    .wave-bar:nth-child(2) { animation-delay: 0.1s; height: 120px; }
                    .wave-bar:nth-child(3) { animation-delay: 0.2s; height: 180px; }
                    .wave-bar:nth-child(4) { animation-delay: 0.3s; height: 120px; }
                    .wave-bar:nth-child(5) { animation-delay: 0.4s; height: 60px; }
                    @keyframes wave {
                        0%, 100% { transform: scaleY(0.5); }
                        50% { transform: scaleY(1); }
                    }
                `;
                document.head.appendChild(style);
            }
        }
        document.querySelector('.audio-wrapper').style.display = 'block';
    } else {
        mediaPlayer.style.display = 'block';
        const audioWrapper = document.querySelector('.audio-wrapper');
        if (audioWrapper) {
            audioWrapper.style.display = 'none';
        }
    }

    // Обновляем информацию о файле
    const fileNameText = path.split('/').pop() || path.split('\\').pop();
    fileName.textContent = fileNameText;
    filePath.textContent = path;

    // Показываем плеер и скрываем пустое состояние
    playerContainer.classList.remove('hidden');
    emptyState.style.display = 'none';
    
    // Показываем кнопки субтитров для видео
    if (!isAudio) {
        subtitleControls.classList.remove('hidden');
        initializeSubtitleSystem();
    } else {
        subtitleControls.classList.add('hidden');
        subtitleEditor.classList.add('hidden');
    }

    // Загружаем медиа
    mediaPlayer.load();

    // Обработчик ошибок
    mediaPlayer.addEventListener('error', (e) => {
        console.error('Ошибка воспроизведения:', e);
        alert('Не удалось воспроизвести файл. Убедитесь, что формат файла поддерживается.');
    });
}

// Обработка перетаскивания файлов
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
    });

    document.addEventListener('drop', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            // В Electron файлы имеют свойство path с абсолютным путем
            if (file.path) {
                loadMediaFile(file.path);
            } else {
                // Fallback: используем File API (может не работать для всех форматов)
                const url = URL.createObjectURL(file);
                const extension = file.name.split('.').pop().toLowerCase();
                const audioExtensions = ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'];
                const isAudio = audioExtensions.includes(extension);
                
                mediaPlayer.src = url;
                
                if (isAudio) {
                    mediaPlayer.style.display = 'none';
                    if (!document.querySelector('.audio-wrapper')) {
                        const audioWrapper = document.createElement('div');
                        audioWrapper.className = 'audio-wrapper';
                        audioWrapper.innerHTML = `
                            <div class="audio-visualizer">
                                <div class="audio-wave">
                                    <div class="wave-bar"></div>
                                    <div class="wave-bar"></div>
                                    <div class="wave-bar"></div>
                                    <div class="wave-bar"></div>
                                    <div class="wave-bar"></div>
                                </div>
                            </div>
                        `;
                        mediaPlayer.parentNode.insertBefore(audioWrapper, mediaPlayer);
                    }
                    document.querySelector('.audio-wrapper').style.display = 'block';
                } else {
                    mediaPlayer.style.display = 'block';
                    const audioWrapper = document.querySelector('.audio-wrapper');
                    if (audioWrapper) {
                        audioWrapper.style.display = 'none';
                    }
                }
                
                fileName.textContent = file.name;
                filePath.textContent = 'Локальный файл';
                
                playerContainer.classList.remove('hidden');
                emptyState.style.display = 'none';
                
                if (!isAudio) {
                    subtitleControls.classList.remove('hidden');
                    initializeSubtitleSystem();
                }
                
                mediaPlayer.load();
            }
        }
    });
});

// Инициализация системы субтитров
function initializeSubtitleSystem() {
    if (subtitleSystemInitialized) return;
    subtitleSystemInitialized = true;
    
    // Обработчики кнопок
    if (openSubtitleBtn) openSubtitleBtn.addEventListener('click', openSubtitleFile);
    if (newSubtitleBtn) newSubtitleBtn.addEventListener('click', createNewSubtitles);
    if (saveSubtitleBtn) saveSubtitleBtn.addEventListener('click', saveSubtitles);
    if (toggleEditorBtn) toggleEditorBtn.addEventListener('click', toggleEditor);
    if (addSubtitleBtn) addSubtitleBtn.addEventListener('click', addSubtitle);
    
    // Обновление отображения субтитров во время воспроизведения
    mediaPlayer.addEventListener('timeupdate', updateSubtitleDisplay);
    mediaPlayer.addEventListener('play', () => {
        if (subtitleUpdateInterval) clearInterval(subtitleUpdateInterval);
        subtitleUpdateInterval = setInterval(updateSubtitleDisplay, 100);
    });
    mediaPlayer.addEventListener('pause', () => {
        if (subtitleUpdateInterval) clearInterval(subtitleUpdateInterval);
    });
}

// Открытие файла субтитров
async function openSubtitleFile() {
    try {
        const result = await window.electronAPI.openSubtitleDialog();
        if (result && result.content) {
            subtitles = parseSRT(result.content);
            renderSubtitleList();
            subtitleEditor.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Ошибка при открытии файла субтитров:', error);
        alert('Не удалось открыть файл субтитров');
    }
}

// Создание новых субтитров
function createNewSubtitles() {
    subtitles = [];
    renderSubtitleList();
    subtitleEditor.classList.remove('hidden');
}

// Сохранение субтитров
async function saveSubtitles() {
    if (subtitles.length === 0) {
        alert('Нет субтитров для сохранения');
        return;
    }
    
    try {
        const srtContent = generateSRT(subtitles);
        await window.electronAPI.saveSubtitleDialog(srtContent);
        alert('Субтитры успешно сохранены');
    } catch (error) {
        console.error('Ошибка при сохранении субтитров:', error);
        alert('Не удалось сохранить субтитры');
    }
}

// Переключение видимости редактора
function toggleEditor() {
    subtitleEditor.classList.toggle('hidden');
}

// Добавление нового субтитра
function addSubtitle() {
    const currentTime = mediaPlayer.currentTime || 0;
    const newSubtitle = {
        index: subtitles.length + 1,
        startTime: currentTime,
        endTime: currentTime + 3, // По умолчанию 3 секунды
        text: ''
    };
    subtitles.push(newSubtitle);
    renderSubtitleList();
    // Фокусируемся на новом субтитре
    const items = subtitleList.querySelectorAll('.subtitle-item');
    if (items.length > 0) {
        const newItem = items[items.length - 1];
        newItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        newItem.querySelector('.subtitle-text-input').focus();
    }
}

// Рендеринг списка субтитров
function renderSubtitleList() {
    subtitleList.innerHTML = '';
    
    subtitles.forEach((subtitle, index) => {
        const item = document.createElement('div');
        item.className = 'subtitle-item';
        item.dataset.index = index;
        
        item.innerHTML = `
            <div class="subtitle-item-header">
                <span class="subtitle-item-number">#${index + 1}</span>
                <div class="subtitle-item-actions">
                    <button class="btn-play" onclick="playFromSubtitle(${index})">▶</button>
                    <button class="btn-delete" onclick="deleteSubtitle(${index})">Удалить</button>
                </div>
            </div>
            <div class="subtitle-time-inputs">
                <input type="text" class="start-time" value="${formatTimeString(subtitle.startTime)}" 
                       onchange="updateSubtitleTime(${index}, 'start', this.value)">
                <span>→</span>
                <input type="text" class="end-time" value="${formatTimeString(subtitle.endTime)}" 
                       onchange="updateSubtitleTime(${index}, 'end', this.value)">
                <button onclick="setSubtitleTimeFromPlayer(${index}, 'start')">Установить начало</button>
                <button onclick="setSubtitleTimeFromPlayer(${index}, 'end')">Установить конец</button>
            </div>
            <textarea class="subtitle-text-input" onchange="updateSubtitleText(${index}, this.value)">${escapeHtml(subtitle.text)}</textarea>
        `;
        
        subtitleList.appendChild(item);
    });
}

// Обновление времени субтитра
function updateSubtitleTime(index, type, timeString) {
    const time = parseTimeString(timeString);
    if (!isNaN(time) && time >= 0) {
        if (type === 'start') {
            subtitles[index].startTime = time;
            if (subtitles[index].endTime <= time) {
                subtitles[index].endTime = time + 1;
                renderSubtitleList();
            }
        } else {
            subtitles[index].endTime = time;
            if (subtitles[index].startTime >= time) {
                subtitles[index].startTime = Math.max(0, time - 1);
                renderSubtitleList();
            }
        }
    }
}

// Установка времени из плеера
function setSubtitleTimeFromPlayer(index, type) {
    const currentTime = mediaPlayer.currentTime;
    updateSubtitleTime(index, type, formatTimeString(currentTime));
    renderSubtitleList();
}

// Обновление текста субтитра
function updateSubtitleText(index, text) {
    subtitles[index].text = text;
}

// Удаление субтитра
function deleteSubtitle(index) {
    if (confirm('Удалить этот субтитр?')) {
        subtitles.splice(index, 1);
        renderSubtitleList();
    }
}

// Воспроизведение с позиции субтитра
function playFromSubtitle(index) {
    mediaPlayer.currentTime = subtitles[index].startTime;
    mediaPlayer.play();
}

// Экранирование HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Отображение субтитров во время воспроизведения
function updateSubtitleDisplay() {
    const currentTime = mediaPlayer.currentTime;
    let found = false;
    
    for (let i = 0; i < subtitles.length; i++) {
        const subtitle = subtitles[i];
        if (currentTime >= subtitle.startTime && currentTime <= subtitle.endTime) {
            subtitleDisplay.textContent = subtitle.text;
            subtitleDisplay.classList.add('active');
            found = true;
            activeSubtitleIndex = i;
            
            // Подсвечиваем активный субтитр в редакторе
            const items = subtitleList.querySelectorAll('.subtitle-item');
            items.forEach((item, idx) => {
                item.classList.toggle('active', idx === i);
            });
            break;
        }
    }
    
    if (!found) {
        subtitleDisplay.classList.remove('active');
        subtitleDisplay.textContent = '';
        activeSubtitleIndex = -1;
        
        const items = subtitleList.querySelectorAll('.subtitle-item');
        items.forEach(item => item.classList.remove('active'));
    }
}

// Экспорт функций в глобальную область для использования в HTML
window.updateSubtitleTime = updateSubtitleTime;
window.setSubtitleTimeFromPlayer = setSubtitleTimeFromPlayer;
window.updateSubtitleText = updateSubtitleText;
window.deleteSubtitle = deleteSubtitle;
window.playFromSubtitle = playFromSubtitle;

