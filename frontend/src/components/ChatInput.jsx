/**
 * ChatInput - Message input with quick suggestions
 * AiPRL powered assistant
 */
import { useRef, useEffect, useState } from 'react'
import { ArrowRight, Loader2, StopCircle } from 'lucide-react'

const SUGGESTIONS = [
  'What are your hours?',
  'Tell me about financing',
  'Schedule service',
  'Help me find a Honda'
]

const PLACEHOLDER_PHRASES = [
  'Ask about vehicles',
  'Tell me about financing',
  'Schedule service',
  'Help me find a Honda'
]

export function ChatInput({ value, onChange, onSend, onCancel, status }) {
  const inputRef = useRef(null)
  const isLoading = status === 'loading'
  const isStreaming = status === 'streaming'
  const isBusy = isLoading || isStreaming

  const [placeholderText, setPlaceholderText] = useState('')
  const [phraseIndex, setPhraseIndex] = useState(0)
  const [charIndex, setCharIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)

  // Focus on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  // Re-focus when not busy (after loading completes)
  useEffect(() => {
    if (!isBusy) {
      inputRef.current?.focus()
    }
  }, [isBusy])

  useEffect(() => {
    const phrase = PLACEHOLDER_PHRASES[phraseIndex]
    const typingSpeed = isDeleting ? 50 : 100
    const pauseAfterType = 2500
    const pauseAfterDelete = 500

    const timer = setTimeout(() => {
      if (isDeleting) {
        if (charIndex > 0) {
          setPlaceholderText(phrase.substring(0, charIndex - 1))
          setCharIndex((i) => i - 1)
        } else {
          setIsDeleting(false)
          setPhraseIndex((prev) => (prev + 1) % PLACEHOLDER_PHRASES.length)
        }
      } else {
        if (charIndex < phrase.length) {
          setPlaceholderText(phrase.substring(0, charIndex + 1))
          setCharIndex((i) => i + 1)
        } else {
          setIsDeleting(true)
        }
      }
    }, isDeleting
      ? (charIndex > 0 ? typingSpeed : pauseAfterDelete)
      : (charIndex < phrase.length ? typingSpeed : pauseAfterType))

    return () => clearTimeout(timer)
  }, [phraseIndex, charIndex, isDeleting])

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (value.trim() && !isBusy) {
      onSend(value)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleSuggestion = (text) => {
    onChange(text)
    inputRef.current?.focus()
  }

  return (
    <div className="chat-input-container">
      {/* Quick suggestions - above input */}
      <div className="suggestions">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => handleSuggestion(suggestion)}
            className="suggestion-btn"
            disabled={isBusy}
          >
            {suggestion}
          </button>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="chat-input-bar">
          <div className="input-wrapper input-wrapper-relative">
            <textarea
              ref={inputRef}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder=""
              rows={1}
              className="chat-textarea"
              disabled={isBusy}
              aria-label="Type your message"
            />
            {!value.trim() && (
              <div className="animated-placeholder" aria-hidden>
                {placeholderText}
                <span className="placeholder-cursor" />
              </div>
            )}
          </div>
          {isStreaming ? (
          <button
            type="button"
            onClick={onCancel}
            className="send-btn cancel-btn"
            aria-label="Cancel"
          >
            <StopCircle className="w-5 h-5" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!value.trim() || isBusy}
            className="send-btn"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <ArrowRight className="w-5 h-5" />
            )}
          </button>
        )}
        </div>
      </form>
    </div>
  )
}

export default ChatInput

