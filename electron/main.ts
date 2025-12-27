import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import { join } from 'path'
import { PythonBridge } from './python-bridge'

let mainWindow: BrowserWindow | null = null
let pythonBridge: PythonBridge | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 720,
    minWidth: 800,
    minHeight: 600,
    frame: false,
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 15, y: 10 },
    backgroundColor: '#0a0a0f',
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false // Allow loading local video files
    }
  })

  // Load the app
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// Initialize Python bridge
function initPythonBridge() {
  const pythonPath = app.isPackaged 
    ? join(process.resourcesPath, 'python')
    : join(__dirname, '..', 'python')
  
  pythonBridge = new PythonBridge(pythonPath)
}

// App lifecycle
app.whenReady().then(() => {
  initPythonBridge()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC Handlers
ipcMain.handle('open-file', async () => {
  if (!mainWindow) return null

  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Video Files', extensions: ['mp4', 'mkv', 'avi', 'mov', 'webm', 'm4v', 'wmv'] }
    ]
  })

  if (result.canceled || result.filePaths.length === 0) {
    return null
  }

  return result.filePaths[0]
})

ipcMain.handle('process-video', async (event, videoPath: string) => {
  if (!pythonBridge || !mainWindow) {
    throw new Error('Python bridge not initialized')
  }

  try {
    // Progress callback
    const onProgress = (update: { stage: string; progress: number; message: string }) => {
      mainWindow?.webContents.send('processing-update', update)
    }

    // Streaming subtitle callback - send each subtitle as it's ready
    const onSubtitle = (subtitle: { id: number; start: number; end: number; text: string; translatedText: string }) => {
      mainWindow?.webContents.send('subtitle-ready', subtitle)
    }

    // Process video with streaming support
    const subtitles = await pythonBridge.processVideo(videoPath, onProgress, onSubtitle)
    return subtitles

  } catch (error) {
    console.error('Error processing video:', error)
    mainWindow?.webContents.send('processing-update', {
      stage: 'error',
      progress: 0,
      message: error instanceof Error ? error.message : 'Unknown error'
    })
    throw error
  }
})
