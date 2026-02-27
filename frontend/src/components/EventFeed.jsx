/**
 * EventFeed - Live streaming events display
 */
import { useState, useEffect } from 'react'

const THINKING_MESSAGES = [
  "Thinking...",
  "Processing...",
  "One moment...",
  "Just a sec...",
  "Working on it...",
  "Let me check...",
  "Give me a moment...",
  "Almost there...",
]

function ThinkingIndicator() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    // Pick a random message when component mounts
    const randomMessage = THINKING_MESSAGES[Math.floor(Math.random() * THINKING_MESSAGES.length)]
    setMessage(randomMessage)
  }, [])

  return (
    <div className="thinking-indicator">
      <div className="thinking-message-wrapper">
        <div className="thinking-tire" />
        <div className="thinking-message-text">
          {message}
        </div>
      </div>
    </div>
  )
}

export function EventFeed({ isStreaming }) {
  if (!isStreaming) return null

  return <ThinkingIndicator />
}

export default EventFeed

