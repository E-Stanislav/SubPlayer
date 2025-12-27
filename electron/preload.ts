import { contextBridge, ipcRenderer } from 'electron'

// Type definitions
interface ProcessingUpdate {
  stage: 'extracting' | 'transcribing' | 'translating' | 'done' | 'error'
  progress: number
  message: string
}

interface SubtitleResult {
  id: number
  start: number
  end: number
  text: string
  translatedText: string
}

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electron', {
  // Open file dialog
  openFile: (): Promise<string | null> => {
    return ipcRenderer.invoke('open-file')
  },

  // Process video (transcribe + translate) with streaming support
  processVideo: (
    videoPath: string, 
    _onProgress: (update: ProcessingUpdate) => void
  ): Promise<SubtitleResult[]> => {
    return ipcRenderer.invoke('process-video', videoPath)
  },

  // Listen for processing updates
  onProcessingUpdate: (callback: (update: ProcessingUpdate) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, update: ProcessingUpdate) => {
      callback(update)
    }
    ipcRenderer.on('processing-update', handler)
  },

  // Listen for streaming subtitles (real-time as they are ready)
  onSubtitleReady: (callback: (subtitle: SubtitleResult) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, subtitle: SubtitleResult) => {
      callback(subtitle)
    }
    ipcRenderer.on('subtitle-ready', handler)
  },

  // Remove all listeners
  removeProcessingListener: () => {
    ipcRenderer.removeAllListeners('processing-update')
  },

  removeSubtitleListener: () => {
    ipcRenderer.removeAllListeners('subtitle-ready')
  }
})
