import { useState, useCallback } from 'react'

interface FileUploadProps {
  onFileSelect: (filePath: string, enableTts: boolean) => void
}

export default function FileUpload({ onFileSelect }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [enableTts, setEnableTts] = useState(false)

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
      const filePath = (file as any).path
      if (filePath && isVideoFile(file.name)) {
        onFileSelect(filePath, enableTts)
      }
    }
  }, [onFileSelect, enableTts])

  const handleOpenFile = useCallback(async () => {
    if (window.electron) {
      const filePath = await window.electron.openFile()
      if (filePath) {
        onFileSelect(filePath, enableTts)
      }
    }
  }, [onFileSelect, enableTts])

  const isVideoFile = (filename: string): boolean => {
    const videoExtensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.wmv']
    return videoExtensions.some(ext => filename.toLowerCase().endsWith(ext))
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-8 gap-6">
      {/* Drop zone */}
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

      {/* TTS Toggle */}
      <div className="flex items-center gap-4 p-4 rounded-xl bg-player-surface/50 border border-white/5">
        <label className="flex items-center gap-3 cursor-pointer select-none">
          <div className="relative">
            <input
              type="checkbox"
              checked={enableTts}
              onChange={(e) => setEnableTts(e.target.checked)}
              className="sr-only peer"
            />
            <div className="
              w-11 h-6 rounded-full transition-colors
              bg-white/10 peer-checked:bg-player-accent
            " />
            <div className="
              absolute top-0.5 left-0.5 w-5 h-5 rounded-full transition-transform
              bg-white peer-checked:translate-x-5
            " />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-white/90">
              Озвучка на русском
            </span>
            <span className="text-xs text-white/40">
              Silero TTS (замена оригинального голоса)
            </span>
          </div>
        </label>
        
        {/* TTS indicator */}
        {enableTts && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20">
            <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            <span className="text-xs text-orange-400">+150 МБ</span>
          </div>
        )}
      </div>
    </div>
  )
}
