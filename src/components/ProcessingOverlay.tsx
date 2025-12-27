import type { ProcessingStatus } from '../App'

interface ProcessingOverlayProps {
  status: ProcessingStatus
}

export default function ProcessingOverlay({ status }: ProcessingOverlayProps) {
  const getStageInfo = () => {
    switch (status.stage) {
      case 'extracting':
        return {
          icon: (
            <svg className="w-8 h-8 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          ),
          title: 'Извлечение аудио',
          color: 'text-blue-400'
        }
      case 'transcribing':
        return {
          icon: (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          ),
          title: 'Распознавание речи',
          color: 'text-player-accent'
        }
      case 'translating':
        return {
          icon: (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
            </svg>
          ),
          title: 'Перевод на русский',
          color: 'text-emerald-400'
        }
      case 'error':
        return {
          icon: (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          ),
          title: 'Ошибка',
          color: 'text-red-400'
        }
      default:
        return {
          icon: null,
          title: '',
          color: ''
        }
    }
  }

  const stageInfo = getStageInfo()

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-50">
      <div className="glass rounded-2xl p-8 max-w-md w-full mx-4 animate-fade-in">
        {/* Icon */}
        <div className={`flex justify-center mb-4 ${stageInfo.color}`}>
          {stageInfo.icon}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-center text-white mb-2">
          {stageInfo.title}
        </h3>

        {/* Message */}
        <p className="text-sm text-white/60 text-center mb-6">
          {status.message}
        </p>

        {/* Progress bar */}
        {status.stage !== 'error' && (
          <div className="relative h-2 bg-white/10 rounded-full overflow-hidden">
            <div 
              className={`
                absolute inset-y-0 left-0 rounded-full transition-all duration-300
                ${status.stage === 'extracting' ? 'bg-blue-500' : ''}
                ${status.stage === 'transcribing' ? 'bg-player-accent' : ''}
                ${status.stage === 'translating' ? 'bg-emerald-500' : ''}
                ${status.progress < 100 ? 'progress-animate' : ''}
              `}
              style={{ width: `${status.progress}%` }}
            />
          </div>
        )}

        {/* Progress percentage */}
        {status.stage !== 'error' && (
          <p className="text-xs text-white/40 text-center mt-2">
            {Math.round(status.progress)}%
          </p>
        )}

        {/* Stage indicators */}
        <div className="flex justify-center gap-6 mt-6">
          <StageIndicator 
            label="Аудио" 
            isActive={status.stage === 'extracting'}
            isComplete={['transcribing', 'translating', 'done'].includes(status.stage)}
          />
          <StageIndicator 
            label="Субтитры" 
            isActive={status.stage === 'transcribing'}
            isComplete={['translating', 'done'].includes(status.stage)}
          />
          <StageIndicator 
            label="Перевод" 
            isActive={status.stage === 'translating'}
            isComplete={status.stage === 'done'}
          />
        </div>
      </div>
    </div>
  )
}

function StageIndicator({ 
  label, 
  isActive, 
  isComplete 
}: { 
  label: string
  isActive: boolean
  isComplete: boolean 
}) {
  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`
        w-3 h-3 rounded-full transition-all
        ${isComplete ? 'bg-emerald-500' : ''}
        ${isActive ? 'bg-player-accent animate-pulse' : ''}
        ${!isActive && !isComplete ? 'bg-white/20' : ''}
      `} />
      <span className={`
        text-xs transition-colors
        ${isActive ? 'text-white' : 'text-white/40'}
        ${isComplete ? 'text-emerald-400' : ''}
      `}>
        {label}
      </span>
    </div>
  )
}


