/**
 * ChatMessage - Individual message display component
 * AiPRL branding with friendly tool names
 */
import { User, Bot, Zap, ShoppingBag, Sparkles, Database, BookOpen, Search } from 'lucide-react'
import ProductCarousel from './ProductCarousel'

// Map internal tool names to friendly, user-facing descriptions
const FRIENDLY_TOOL_NAMES = {
  // Product/Catalog tools (hide "Magento")
  'magento': 'Catalog',
  'product': 'Products',
  'search_products': 'Search',
  'get_products': 'Products',
  'products': 'Catalog',
  'catalog': 'Store',
  'inventory': 'Stock',
  
  // Knowledge/RAG tools (hide "RAG")
  'rag': 'Store info',
  'knowledge': 'Details',
  'query_knowledge': 'Info',
  'search_knowledge': 'Store info',
  
  // Customer/Order tools
  'customer': 'Account',
  'order': 'Orders',
  'orders': 'Orders',
}

// Format tool name for display - friendly version
const formatToolName = (name) => {
  if (!name) return 'Working'
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

// Get icon for tool type
const getToolIcon = (name) => {
  if (!name) return <Search className="w-3 h-3" />
  const lowerName = name.toLowerCase()
  if (lowerName.includes('product') || lowerName.includes('magento') || lowerName.includes('catalog') || lowerName.includes('inventory')) 
    return <ShoppingBag className="w-3 h-3" />
  if (lowerName.includes('rag') || lowerName.includes('knowledge')) 
    return <BookOpen className="w-3 h-3" />
  if (lowerName.includes('customer') || lowerName.includes('order')) 
    return <Database className="w-3 h-3" />
  return <Sparkles className="w-3 h-3" />
}

function ToolBadge({ name }) {
  return (
    <span className="tool-badge-mini">
      {getToolIcon(name)}
      <span>{formatToolName(name)}</span>
    </span>
  )
}

function MessageContent({ text }) {
  if (!text) return null

  // Process markdown-style formatting
  const renderLine = (line, lineIndex) => {
    // Handle bold **text**
    const parts = line.split(/(\*\*[^*]+\*\*)/g)
    
    return (
      <p key={lineIndex} className="message-line">
        {parts.map((part, i) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={i}>{part.slice(2, -2)}</strong>
          }
          // Handle URLs
          const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`[\]]+)/g
          const segments = part.split(urlRegex)
          return segments.map((seg, j) => {
            if (seg.match(/^https?:\/\//)) {
              return (
                <a 
                  key={`${i}-${j}`}
                  href={seg}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="message-link"
                >
                  {seg.length > 50 ? seg.slice(0, 50) + '...' : seg}
                </a>
              )
            }
            return <span key={`${i}-${j}`}>{seg}</span>
          })
        })}
      </p>
    )
  }

  return (
    <div className="message-content">
      {text.split('\n').map((line, index) => renderLine(line, index))}
    </div>
  )
}

export function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  
  return (
    <div className={`chat-message ${isUser ? 'chat-message-user' : ''} ${isSystem ? 'chat-message-system' : ''}`}>
      {/* Avatar */}
      <div className={`message-avatar ${isUser ? 'avatar-user' : isSystem ? 'avatar-system' : 'avatar-agent'}`}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : isSystem ? (
          <Zap className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>
      
      {/* Message Content */}
      <div className="message-body">
        <div className={`message-bubble ${isUser ? 'bubble-user' : isSystem ? 'bubble-system' : 'bubble-agent'}`}>
          <MessageContent text={message.text} />
          
          {/* Products */}
          {message.products && message.products.length > 0 && (
            <ProductCarousel products={message.products} />
          )}
        </div>
        
        {/* Tool calls indicator */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="message-tools">
            {message.toolCalls.map((tool, idx) => (
              <ToolBadge key={idx} name={tool.name} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage

