/**
 * Iframe chat content - Live streaming chat with bubble/teaser theme
 * Powered by Google ADK
 */
import { useState, useRef, useEffect } from 'react'
import { useSSEChat } from './hooks/useSSEChat'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import EventFeed from './components/EventFeed'
import SkeletonMessage from './components/SkeletonMessage'
import './index.css'
import PattyPeckLogo from './assets/PattyPeck.png'

function App() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  
  const {
    messages,
    liveEvents,
    status,
    streamingText,
    sendMessage,
    cancelStream,
    aiPaused,
    hasPendingRecovery,
    pendingMessageCount,
    confirmRecovery,
    declineRecovery,
    isInitializing
  } = useSSEChat()

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, liveEvents, status])

  const handleSend = (text) => {
    const messageText = text || input
    if (messageText.trim()) {
      sendMessage(messageText.trim())
      setInput('')
    }
  }

  const isStreaming = status === 'streaming'
  const isLoading = status === 'loading'
  const isHumanMode = status === 'human_mode' || aiPaused  // Don't show "thinking" in human mode

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-brand">
            <div className="brand-logo">
              <img src={PattyPeckLogo} alt="Patty Peck Honda" className="logo-image" />
            </div>
            <p className="brand-subtitle">AI Assistant</p>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="messages-container">
        <div className="messages">
          {/* Initial loading skeleton */}
          {isInitializing ? (
            <>
              <SkeletonMessage variant="agent" />
              <SkeletonMessage variant="user" />
            </>
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
            </>
          )}
          
          {/* Session Recovery Prompt */}
          {!isInitializing && hasPendingRecovery && (
            <div className="recovery-prompt">
              <div className="recovery-content">
                <p className="recovery-text">
                  You have a previous conversation with {pendingMessageCount} messages.
                </p>
                <div className="recovery-buttons">
                  <button 
                    onClick={confirmRecovery}
                    className="recovery-btn continue-btn"
                  >
                    Continue
                  </button>
                  <button 
                    onClick={declineRecovery}
                    className="recovery-btn fresh-btn"
                  >
                    Start Fresh
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Event Feed - Shows during AI response (NOT in human mode) */}
          {!isInitializing && (isLoading || isStreaming) && !isHumanMode && (
            <EventFeed
              events={liveEvents}
              isStreaming={isLoading || isStreaming}
              streamingText={streamingText}
            />
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="footer">
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          onCancel={cancelStream}
          status={hasPendingRecovery ? 'loading' : status}
        />
      </footer>
    </div>
  )
}

export default App
