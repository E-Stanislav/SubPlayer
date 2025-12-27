import { useState, useCallback } from 'react'

interface FileUploadProps {
  onFileSelect: (filePath: string) => void
}

export default function FileUpload({ onFileSelect }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      // Get the file path from Electron
      const filePath = (file as any).path
      if (filePath && isVideoFile(file.name)) {
        onFileSelect(filePath)
      }
    }
  }, [onFileSelect])

  const handleOpenFile = useCallback(async () => {
    if (window.electron) {
      const filePath = await window.electron.openFile()
      if (filePath) {
        onFileSelect(filePath)
      }
    }
  }, [onFileSelect])

  const isVideoFile = (filename: string): boolean => {
    const videoExtensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.wmv']
    return videoExtensions.some(ext => filename.toLowerCase().endsWith(ext))
  }

  return (
    <div className="w-full h-full flex items-center justify-center p-8">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleOpenFile}
        className={`
          relative w-full max-w-2xl aspect-video rounded-2xl
          border-2 border-dashed transition-all duration-300 cursor-pointer
          flex flex-col items-center justify-center gap-6
          ${isDragging 
            ? 'border-player-accent bg-player-accent/10 scale-105' 
            : 'border-white/20 hover:border-player-accent/50 hover:bg-white/5'
          }
        `}
      >
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden rounded-2xl">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-radial from-player-accent/10 to-transparent opacity-50" />
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-radial from-indigo-600/10 to-transparent opacity-50" />
        </div>

        {/* Icon */}
        <div className={`
          relative z-10 w-24 h-24 rounded-full 
          bg-gradient-to-br from-player-accent/20 to-indigo-600/20
          flex items-center justify-center
          transition-transform duration-300
          ${isDragging ? 'scale-110' : ''}
        `}>
          <svg 
            className={`w-12 h-12 transition-colors duration-300 ${isDragging ? 'text-player-accent' : 'text-white/60'}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={1.5} 
              d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" 
            />
          </svg>
        </div>

        {/* Text */}
        <div className="relative z-10 text-center">
          <h2 className={`
            text-xl font-semibold mb-2 transition-colors duration-300
            ${isDragging ? 'text-player-accent' : 'text-white/90'}
          `}>
            {isDragging ? 'Отпустите файл' : 'Загрузите видео'}
          </h2>
          <p className="text-sm text-white/50">
            Перетащите файл сюда или нажмите для выбора
          </p>
          <p className="text-xs text-white/30 mt-2">
            Поддерживаются: MP4, MKV, AVI, MOV, WebM
          </p>
        </div>

        {/* Feature badges */}
        <div className="relative z-10 flex gap-3 mt-4">
          <span className="px-3 py-1 rounded-full bg-player-accent/10 border border-player-accent/20 text-xs text-player-accent">
            Faster Whisper
          </span>
          <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
            Авто-субтитры
          </span>
          <span className="px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs text-amber-400">
            Перевод на RU
          </span>
        </div>
      </div>
    </div>
  )
}

