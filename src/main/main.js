const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs').promises;

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default'
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  // Открываем DevTools в режиме разработки (можно удалить в продакшене)
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Обработка открытия файлов через диалог
ipcMain.handle('open-file-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Медиа файлы', extensions: ['mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'] },
      { name: 'Видео', extensions: ['mp4', 'avi', 'mov', 'mkv', 'webm'] },
      { name: 'Аудио', extensions: ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'] },
      { name: 'Все файлы', extensions: ['*'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Обработка открытия файлов субтитров
ipcMain.handle('open-subtitle-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Субтитры', extensions: ['srt', 'vtt'] },
      { name: 'Все файлы', extensions: ['*'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    try {
      const content = await fs.readFile(result.filePaths[0], 'utf-8');
      return { path: result.filePaths[0], content };
    } catch (error) {
      console.error('Ошибка чтения файла субтитров:', error);
      return null;
    }
  }
  return null;
});

// Обработка сохранения файлов субтитров
ipcMain.handle('save-subtitle-dialog', async (event, content) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [
      { name: 'SRT файлы', extensions: ['srt'] },
      { name: 'VTT файлы', extensions: ['vtt'] },
      { name: 'Все файлы', extensions: ['*'] }
    ],
    defaultPath: 'subtitle.srt'
  });

  if (!result.canceled && result.filePath) {
    try {
      await fs.writeFile(result.filePath, content, 'utf-8');
      return result.filePath;
    } catch (error) {
      console.error('Ошибка сохранения файла субтитров:', error);
      return null;
    }
  }
  return null;
});

