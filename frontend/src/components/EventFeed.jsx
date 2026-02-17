/**
 * EventFeed - Live streaming events display
 * Shows AiPRL actions and responses in real-time
 */
import { Zap, Check, Loader2, ShoppingBag, Sparkles, Wrench, Database, Search, BookOpen } from 'lucide-react'
import { EventType } from '../hooks/useSSEChat'

// Map internal tool names to friendly, user-facing descriptions
const FRIENDLY_TOOL_NAMES = {
  // Product/Catalog tools (hide "Magento")
  'magento': 'Browsing catalog',
  'product': 'Finding products',
  'search_products': 'Searching inventory',
  'get_products': 'Loading products',
  'products': 'Checking catalog',
  'catalog': 'Browsing store',
  'inventory': 'Checking stock',
  
  // Knowledge/RAG tools (hide "RAG")
  'rag': 'Checking store info',
  'knowledge': 'Looking up details',
  'query_knowledge': 'Finding information',
  'search_knowledge': 'Searching store info',
  
  // Customer/Order tools
  'customer': 'Checking account',
  'order': 'Looking up orders',
  'orders': 'Finding order info',
  
  // Default friendly names
  'default': 'Working on it'
}

const getToolIcon = (name) => {
  if (!name) return <Search className="w-3.5 h-3.5" />
  const lowerName = name.toLowerCase()
  if (lowerName.includes('product') || lowerName.includes('magento') || lowerName.includes('catalog') || lowerName.includes('inventory')) 
    return <ShoppingBag className="w-3.5 h-3.5" />
  if (lowerName.includes('rag') || lowerName.includes('knowledge')) 
    return <BookOpen className="w-3.5 h-3.5" />
  if (lowerName.includes('customer') || lowerName.includes('order')) 
    return <Database className="w-3.5 h-3.5" />
  return <Sparkles className="w-3.5 h-3.5" />
}

const formatToolName = (name) => {
  if (!name) return 'Processing'
  const lowerName = name.toLowerCase()
  
  // Check for matching friendly names
  for (const [key, friendlyName] of Object.entries(FRIENDLY_TOOL_NAMES)) {
    if (lowerName.includes(key)) {
      return friendlyName
    }
  }
  
  // Fallback: clean up the name but keep it friendly
  return name
    .replace(/_tool$/, '')
    .replace(/^(get_|search_|query_|fetch_)/, '')
    .replace(/_/g, ' ')
    .replace(/magento/gi, 'store')
    .replace(/rag/gi, 'info')
}

function EventItem({ event, isLatest }) {
  const isFunctionCall = event.type === EventType.FUNCTION_CALL
  const isFunctionResponse = event.type === EventType.FUNCTION_RESPONSE
  
  return (
    <div className={`event-item ${isLatest ? 'event-item-latest' : ''}`}>
      <div className={`event-badge ${isFunctionCall ? 'event-calling' : 'event-complete'}`}>
        <span className="event-icon">
          {isFunctionCall ? (
            <Zap className="w-3.5 h-3.5" />
          ) : (
            <Check className="w-3.5 h-3.5" />
          )}
        </span>
        
        {getToolIcon(event.name)}
        
        <span className="event-name">
          {formatToolName(event.name)}
        </span>
        
        {isFunctionCall && isLatest && (
          <Loader2 className="w-3.5 h-3.5 animate-spin ml-1" />
        )}
      </div>
    </div>
  )
}

function ThinkingIndicator({ text }) {
  return (
    <div className="thinking-indicator">
      <div className="thinking-dots">
        <span className="thinking-dot" />
        <span className="thinking-dot" />
        <span className="thinking-dot" />
      </div>
      <span className="thinking-text">
        {text || 'Looking into that...'}
      </span>
    </div>
  )
}

export function EventFeed({ events, isStreaming, streamingText }) {
  if (!isStreaming && events.length === 0) return null
  
  const hasEvents = events.length > 0
  const lastEvent = events[events.length - 1]
  const isWaitingForResponse = lastEvent?.type === EventType.FUNCTION_CALL
  
  return (
    <div className="event-feed animate-slide-up">
      <div className="event-feed-header">
        <div className="event-feed-indicator" />
        <span>AiPRL is working on this...</span>
      </div>
      
      <div className="event-feed-content">
        {events.map((event, idx) => (
          <EventItem 
            key={event.id || idx} 
            event={event} 
            isLatest={idx === events.length - 1 && isWaitingForResponse}
          />
        ))}
        
        {isStreaming && !hasEvents && (
          <ThinkingIndicator text="AiPRL is thinking..." />
        )}
        
        {isStreaming && hasEvents && !isWaitingForResponse && (
          <ThinkingIndicator text="Crafting your answer..." />
        )}
        
        {streamingText && (
          <div className="streaming-preview">
            <span className="streaming-cursor" />
            <span className="streaming-text">{streamingText.slice(0, 100)}...</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default EventFeed

