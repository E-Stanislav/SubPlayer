import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import { join } from 'path'
import { readFileSync, existsSync } from 'fs'
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
      webSecurity: false // Allow loading local video and audio files
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

// Read audio file and return as base64 data URL
ipcMain.handle('read-audio-file', async (event, filePath: string): Promise<string | null> => {
  try {
    if (!existsSync(filePath)) {
      return null
    }
    const buffer = readFileSync(filePath)
    const base64 = buffer.toString('base64')
    return `data:audio/wav;base64,${base64}`
  } catch {
    return null
  }
})

ipcMain.handle('process-video', async (event, videoPath: string, enableTts: boolean = false) => {
  if (!pythonBridge || !mainWindow) {
    throw new Error('Python bridge not initialized')
  }

  try {
    // Progress callback
    const onProgress = (update: { stage: string; progress: number; message: string }) => {
      mainWindow?.webContents.send('processing-update', update)
    }

    // Streaming subtitle callback - send each subtitle as it's ready
    const onSubtitle = (subtitle: { 
      id: number
      start: number
      end: number
      text: string
      translatedText: string
      audioFile?: string | null
    }) => {
      mainWindow?.webContents.send('subtitle-ready', subtitle)
    }

    // Process video with streaming support
    const subtitles = await pythonBridge.processVideo(
      videoPath, 
      onProgress, 
      onSubtitle,
      { enableTts }
    )
    return subtitles

  } catch (error) {
    mainWindow?.webContents.send('processing-update', {
      stage: 'error',
      progress: 0,
      message: error instanceof Error ? error.message : 'Unknown error'
    })
    throw error
  }
})
