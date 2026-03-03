/**
 * SkeletonMessage - Skeleton loading placeholder for chat messages
 */
import { useState, useEffect } from 'react'

const LOADING_MESSAGES = [
  "Finding the perfect vehicle for you...",
  "Checking our inventory...",
  "Searching through our Honda selection...",
  "Getting the latest information...",
  "Looking through available vehicles...",
  "Checking our current offers...",
  "Gathering vehicle details...",
  "Let me find that for you...",
  "One moment while I check our inventory...",
]

export function SkeletonMessage({ variant = 'agent' }) {
  const [message, setMessage] = useState('')

  useEffect(() => {
    // Pick a random message when component mounts
    const randomMessage = LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)]
    setMessage(randomMessage)
  }, [])

  return (
    <div className={`chat-message skeleton-message ${variant === 'user' ? 'chat-message-user' : ''}`}>
      <div className={`message-avatar skeleton-avatar-wrap ${variant === 'user' ? 'avatar-user' : 'avatar-agent'}`}>
        <div className="skeleton-avatar" />
      </div>
      <div className="message-body">
        <div className={`message-bubble skeleton-bubble ${variant === 'user' ? 'bubble-user' : 'bubble-agent'}`}>
          <div className="skeleton-text-content">
            {message}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SkeletonMessage
