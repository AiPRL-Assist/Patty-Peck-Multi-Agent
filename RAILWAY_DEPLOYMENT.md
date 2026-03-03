# Gavigans ADK Agent - Railway Deployment

## Quick Deploy to Railway

1. Push code to GitHub (or deploy directly from folder)
2. Create new project in Railway
3. Set environment variables (see below)
4. Deploy!

---

## Environment Variables for Gavigans Agent (Railway)

**Set these in Railway Dashboard → Variables. Never commit real values to git.**

```bash
# Google API Key for Gemini (get from Google AI Studio / Cloud Console)
GOOGLE_API_KEY=<your-google-api-key>

# Database for ADK sessions (PostgreSQL)
# Use your own Neon/Supabase database or Railway Postgres
# For async SQLAlchemy use: postgresql+asyncpg://...?ssl=require
DATABASE_URL=<your-database-url>

# Inbox integration
INBOX_WEBHOOK_URL=https://gavigans-inbox.up.railway.app/webhook/message
WOODSTOCK_API_KEY=<your-inbox-api-key>

# JWT Secret (for Prisma auth - if using original Gavigans dashboard)
JWT_SECRET=<your-jwt-secret>

# Port (Railway sets this automatically)
PORT=8000
```

---

## Environment Variables for Chatrace-Inbox Backend (Railway)

Add these to the **gavigans-only** backend:

```bash
# 🆕 NEW: Gavigans Agent API URL
GAVIGANS_API_URL=https://YOUR-GAVIGANS-AGENT.up.railway.app/api/inbox
GAVIGANS_API_KEY=gavigans_api_key_2024

# Existing vars (keep these)
DATABASE_URL=postgresql://...
BUSINESS_ID=gavigans
JWT_SECRET=...
NODE_ENV=production
FRONTEND_URL=https://frontend-inbox-production.up.railway.app
# ... other existing vars
```

---

## How It Connects

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│                 │     │                      │     │                 │
│  WEBCHAT        │────▶│  GAVIGANS ADK AGENT  │◀───▶│  CHATRACE-INBOX │
│  (frontend)     │     │  (Railway)           │     │  (Railway)      │
│                 │     │                      │     │                 │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
        │                        │                           │
        │ SSE Stream             │ Webhook                   │ SSE Stream
        │ /run_sse               │ /webhook/message          │ /events
        ▼                        ▼                           ▼
   Real-time chat          New messages              Inbox sidebar
                           pushed here               real-time updates
```

### Connection Flow:

1. **Webchat → Agent**: User sends message via SSE stream
2. **Agent → Inbox**: Agent sends webhook to `INBOX_WEBHOOK_URL` for new messages
3. **Inbox → Agent**: Inbox calls `GAVIGANS_API_URL` to:
   - Fetch conversations (`/conversations`)
   - Get messages (`/conversations/:id/messages`)
   - Send human agent messages (`/messages`)
   - Toggle AI (`/toggle-ai`)
   - Mark as read (`/conversations/:id/read`)

---

## Deployment Checklist

### 1. Deploy Gavigans Agent to Railway
- [ ] Push `april_agents_adk` to GitHub
- [ ] Create Railway project from repo
- [ ] Set environment variables
- [ ] Note the deployed URL (e.g., `https://gavigans-agent-xxx.up.railway.app`)

### 2. Update Inbox Backend
- [ ] Add `GAVIGANS_API_URL=https://gavigans-agent-xxx.up.railway.app/api/inbox`
- [ ] Add `GAVIGANS_API_KEY=gavigans_api_key_2024`
- [ ] Redeploy inbox backend

### 3. Test the Connection
```bash
# Test agent health
curl https://gavigans-agent-xxx.up.railway.app/health

# Test inbox connection
curl https://gavigans-agent-xxx.up.railway.app/api/inbox/conversations \
  -H "Authorization: Bearer gavigans_api_key_2024"

# Test from inbox side
curl https://gavigans-inbox.up.railway.app/api/inbox/conversations
```

---

## API Endpoints Reference

### Gavigans Agent API (`/api/inbox/*`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/inbox/conversations` | GET | List all conversations |
| `/api/inbox/conversations/:id/messages` | GET | Get messages for conversation |
| `/api/inbox/messages` | POST | Send message from human agent |
| `/api/inbox/toggle-ai` | POST | Toggle AI on/off |
| `/api/inbox/conversations/:id/read` | POST | Mark as read |
| `/api/inbox/listen/global` | GET | SSE for sidebar updates |
| `/api/inbox/listen/:id` | GET | SSE for specific conversation |

### ADK Agent API (`/apps/*`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/list-apps` | GET | List available agents |
| `/run_sse` | POST | Run agent with SSE streaming |
| `/apps/:appName/users/:userId/sessions` | POST | Create session |
| `/apps/:appName/users/:userId/sessions/:sessionId` | GET | Get session |
