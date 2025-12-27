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

  // Process video (transcribe + translate)
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

  // Remove processing update listener
  removeProcessingListener: () => {
    ipcRenderer.removeAllListeners('processing-update')
  }
})

