/**
 * SkeletonMessage - Skeleton loading placeholder for chat messages
 */
export function SkeletonMessage({ variant = 'agent' }) {
  return (
    <div className={`chat-message skeleton-message ${variant === 'user' ? 'chat-message-user' : ''}`}>
      <div className={`message-avatar skeleton-avatar-wrap ${variant === 'user' ? 'avatar-user' : 'avatar-agent'}`}>
        <div className="skeleton-avatar" />
      </div>
      <div className="message-body">
        <div className={`message-bubble skeleton-bubble ${variant === 'user' ? 'bubble-user' : 'bubble-agent'}`}>
          <div className="skeleton-lines">
            <div className="skeleton-line skeleton-line-long" />
            <div className="skeleton-line skeleton-line-medium" />
            <div className="skeleton-line skeleton-line-short" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default SkeletonMessage
