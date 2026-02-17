/**
 * Gavigans Multi-Agent Platform - Webchat
 * Live streaming chat interface with real-time event display
 * Powered by Google ADK
 */
import { useState, useRef, useEffect } from 'react'
import { RotateCcw } from 'lucide-react'
import { useSSEChat } from './hooks/useSSEChat'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import EventFeed from './components/EventFeed'
import './index.css'

function App() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  
  const {
    messages,
    liveEvents,
    status,
    streamingText,
    sendMessage,
    reset,
    cancelStream,
    aiPaused  // 🆕 Track if human is handling the conversation
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
  const isHumanMode = status === 'human_mode' || aiPaused  // 🆕 Don't show "thinking" in human mode

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-brand">
            <div className="brand-logo">
              <span className="logo-emoji">🤖</span>
            </div>
            <div className="brand-text">
              <h1 className="brand-title">Gavigans</h1>
              <p className="brand-subtitle">Multi-Agent Platform</p>
            </div>
          </div>
          
          <button
            onClick={reset}
            className="reset-btn"
            title="New conversation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Messages */}
      <main className="messages-container">
        <div className="messages">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          
          {/* Live Event Feed - Shows during streaming (NOT in human mode) */}
          {(isLoading || isStreaming) && !isHumanMode && (
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
          status={status}
        />
      </footer>
    </div>
  )
}

export default App
