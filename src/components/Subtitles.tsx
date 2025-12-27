import type { Subtitle } from '../App'

interface SubtitlesProps {
  subtitle: Subtitle | null
  showSubtitles?: boolean
  showTranslation?: boolean
}

export default function Subtitles({ 
  subtitle, 
  showSubtitles = true, 
  showTranslation = true 
}: SubtitlesProps) {
  if (!subtitle || !showSubtitles) return null

  return (
    <div className="absolute bottom-24 left-0 right-0 flex justify-center px-8 pointer-events-none">
      <div className="max-w-4xl text-center animate-fade-in">
        {/* Translated text (Russian) */}
        {subtitle.translatedText && showTranslation && (
          <div className="mb-2">
            <span className="
              inline-block px-4 py-2 rounded-lg
              bg-subtitle-bg
              text-white text-xl font-subtitle font-medium
              subtitle-text leading-relaxed
            ">
              {subtitle.translatedText}
            </span>
          </div>
        )}
        
        {/* Original text */}
        <div>
          <span className="
            inline-block px-3 py-1 rounded-md
            bg-black/50
            text-white/70 text-sm font-subtitle
            subtitle-text
          ">
            {subtitle.text}
          </span>
        </div>
      </div>
    </div>
  )
}


