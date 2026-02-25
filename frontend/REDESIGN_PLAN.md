# Patty Peck Honda — Frontend Redesign Plan

> **Scope:** Frontend only. No backend files to be touched.
> **Assets available:** `src/assets/PattyPeck.png` (header logo) · `src/assets/logo-honda.png` (AI avatar + favicon)

---

## Design Direction

**Theme:** Clean automotive professionalism. Honda is a premium, trustworthy brand. The UI should feel like the digital equivalent of walking into a well-run Honda showroom — not a tech product, not a furniture store. Confident, spacious, and brand-aligned.

**Personality shift:** Gavigans was warm/cozy (burgundy, serif display). Patty Peck Honda should feel authoritative and modern — Honda blue as the hero, white space as a feature, Honda Red for urgency/accents only.

---

## 1. Color System

The entire palette swaps from burgundy to Honda Blue. The current design uses tinted shadows — that system stays, just re-tinted to blue.

| Token | Current | New | Where it Shows |
|---|---|---|---|
| `--brand-primary` | `#6f0302` | `#0066B3` | Buttons, header, send button, suggestion pills active state |
| `--brand-primary-dark` | `#5a0202` | `#004C8A` | Hover states, pressed buttons |
| `--brand-primary-light` | `#8a0403` | `#1A7AC2` | Lighter accents, focus rings |
| `--bubble-bg` | `#6f0302` | `#0066B3` | User message bubble background |
| `--teaser-bg` | `#6f0302` | `#0066B3` | Thinking indicator panel |
| `--brand-mandy` | `#c41e3a` | `#CC0000` | Honda Red — links, badges, highlights only |
| Shadow tints | `rgba(111,3,2,...)` | `rgba(0,102,179,...)` | All depth/shadow layers |

All other neutrals (`--layer-0` through `--layer-3`, text colors, borders) stay identical.

---

## 2. Header

**Current state:** Neutral bar, Gavigans furniture logo (external URL), "Gavigans" title + "Multi-Agent Platform" subtitle

**Redesigned:**

```
┌────────────────────────────────────────────────────────┐
│  [ PattyPeck.png wordmark logo ]   [ AI Assistant ]    │
└────────────────────────────────────────────────────────┘
```

- **Logo container:** Resize from `52×52px` square → `height: 48px / width: auto / max-width: 200px` to fit the wide horizontal wordmark
- **Logo image:** Replace external Gavigans URL with local `src/assets/PattyPeck.png`
- **Title `<h1>`:** Remove — the PattyPeck.png already contains the brand name; showing both is redundant
- **Subtitle:** Keep, update text to `"AI Assistant"` — styled as the existing badge (uppercase, muted, sunken pill)

---

## 3. Chat Message Bubbles

**User bubble (right side):**
- Background: Honda Blue `#0066B3` (was burgundy) — white text
- Bottom-right corner stays sharp (directional indicator)
- Shadow tint updates to blue

**Agent bubble (left side):**
- Stays white background, dark text — no change needed
- AI avatar beside it changes (see below)

**System bubble (centre):**
- No color change — stays neutral gray

---

## 4. AI Avatar

**Current:** External Cloudinary image URL (Gavigans-era asset)

**New:** Local `src/assets/logo-honda.png` — the official Honda "H" emblem badge imported directly into `ChatMessage.jsx`. Fits cleanly inside the existing circular `avatar-agent` container.

---

## 5. Input Area (Footer)

**Textarea placeholder:**
- `"Ask about furniture, locations, appointments..."` → `"Ask about vehicles, inventory, service, or financing..."`

**Send button:**
- Color updates automatically via CSS variable swap to Honda Blue

**Suggestion Pills — 4 pills, updated copy:**

| # | Old | New |
|---|---|---|
| 1 | What are your store hours? | What are your hours? |
| 2 | Tell me about financing | Tell me about financing |
| 3 | Book an appointment | Schedule service |
| 4 | Help me find furniture | Help me find a Honda |

---

## 6. Product Carousel (Vehicle Cards)

No layout changes needed. The color updates from the CSS variables propagate automatically to:
- "View" link color → Honda Blue
- Carousel button hover → Honda Blue

Cards already support `"Starting at $X"` and `"Contact Store for Pricing"` labels — correct for vehicles.

---

## 7. Page Meta

| Element | Current | New |
|---|---|---|
| `<title>` | `frontend` | `Patty Peck Honda \| AI Assistant` |
| Favicon | `/vite.svg` (Vite logo) | `/src/assets/logo-honda.png` |

---

## 8. Welcome Message

```
Welcome to Patty Peck Honda!

I'm your AI assistant. How can I help you with
vehicles, service, or financing today?
```

---

## 9. Environment / Storage Keys

| Variable | Current | New |
|---|---|---|
| `VITE_APP_NAME` fallback | `gavigans_agent` | `pattypeck_agent` |
| User ID storage key | `gavigans_chat_user_id` | `pattypeck_chat_user_id` |
| Session ID storage key | `gavigans_chat_session_id` | `pattypeck_chat_session_id` |

---

## 10. Files to Touch (Frontend Only)

| File | What Changes |
|---|---|
| `index.html` | Page title, favicon |
| `src/index.css` | All CSS color variables + all `rgba(111,3,2,...)` shadow tints + `.brand-logo` dimensions + `.continue-btn` gradient |
| `src/App.jsx` | Import `PattyPeck.png`, remove old logo URL, remove redundant `<h1>`, update subtitle |
| `src/components/ChatMessage.jsx` | Import `logo-honda.png`, replace Cloudinary avatar URL |
| `src/components/ChatInput.jsx` | Placeholder text, 4 suggestion pills |
| `src/hooks/useSSEChat.js` | Welcome message, `APP_NAME`, storage keys |
| `frontend/.env.example` | `VITE_APP_NAME` default value |

**Backend: zero touches.**

---

## 11. Visual Layout End-to-End

```
┌──────────────────────────────────────────────────────────────┐
│  [ PattyPeck wordmark logo ]              [ AI Assistant ]   │  ← Neutral header
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────────────────────────────┐              │
│   │  Welcome to Patty Peck Honda!          │  ← System   │
│   │  I'm your AI assistant. How can I help   │    bubble    │
│   │  you with vehicles, service, or          │  (gray bg)   │
│   │  financing today?                        │              │
│   └──────────────────────────────────────────┘              │
│  [H]  ← Honda badge avatar                                   │
│                                                              │
│             ┌────────────────────────────────────────────┐  │
│             │  Help me find a Honda                      │  │  ← User bubble
│             └────────────────────────────────────────────┘  │    (Blue bg)
│                                                         [U]  │
│                                                              │
│   [•••]  ← Thinking indicator                               │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────┐  [ → Send ]     │  ← Footer
│  │ Ask about vehicles, inventory...       │                  │
│  └────────────────────────────────────────┘                  │
│  [What are your hours?] [Financing] [Schedule service] [Find a Honda] │
└──────────────────────────────────────────────────────────────┘
```

---

## 12. Asset Usage Reference

| Asset | File | Used In |
|---|---|---|
| `src/assets/PattyPeck.png` | Full dealership wordmark — black "PattyPeck" + blue "Honda" | `App.jsx` header logo |
| `src/assets/logo-honda.png` | Honda "H" emblem badge in blue | `ChatMessage.jsx` AI avatar · `index.html` favicon |

---

*Plan documented for Patty Peck Honda frontend rebrand. Backend remains unchanged.*
