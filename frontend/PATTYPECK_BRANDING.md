# Patty Peck Honda — Frontend Branding Specification

> **Purpose:** Complete branding guide for rebranding the chat frontend from Gavigans (furniture dealer) to Patty Peck Honda (Honda dealership). Use this document to implement all frontend branding updates. **Backend must not be touched.**

---

## 1. Brand Overview

| Attribute | Value |
|-----------|-------|
| **Business** | Patty Peck Honda — Honda dealership |
| **Location** | 555 Sunnybrook Road, Ridgeland, MS 39157 |
| **Website** | https://www.pattypeckhonda.com/ |
| **Platform** | DealerInspire |
| **Focus** | New/used vehicles, service, parts, financing, appointments |

---

## 2. Color Palette

### Primary Colors (Replace Current Burgundy)

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Brand Primary (Blue)** | `#0066B3` | rgb(0, 102, 179) | Main brand color — buttons, links, nav, CTAs |
| **Brand Primary Dark** | `#004C8A` | rgb(0, 76, 138) | Hover states, pressed states |
| **Brand Primary Light** | `#1A7AC2` | rgb(26, 122, 194) | Lighter accents |
| **Honda Red (Accent)** | `#CC0000` | rgb(204, 0, 0) | Honda brand accent — links, highlights, badges |
| **White** | `#FFFFFF` | rgb(255, 255, 255) | Text on blue, backgrounds |
| **Black** | `#1A1A1A` | rgb(26, 26, 26) | Primary text, logo |

### Neutral / UI Colors

| Role | Hex | Usage |
|------|-----|-------|
| **Text Primary** | `#1A1A1A` | Main body text |
| **Text Secondary** | `#4A5568` | Secondary text |
| **Text Muted** | `#718096` | Placeholders, hints |
| **Border** | `rgba(26, 26, 26, 0.08)` | Borders, dividers |
| **Background Base** | `#F5F5F5` | Page background |
| **Background Elevated** | `#FFFFFF` | Cards, panels |

### Current → New Mapping

| Current (Gavigans) | New (Patty Peck) |
|--------------------|------------------|
| `--bubble-bg: #6f0302` | `--bubble-bg: #0066B3` |
| `--teaser-bg: #6f0302` | `--teaser-bg: #0066B3` |
| `--brand-primary: #6f0302` | `--brand-primary: #0066B3` |
| `--brand-primary-dark: #5a0202` | `--brand-primary-dark: #004C8A` |
| `--brand-primary-light: #8a0403` | `--brand-primary-light: #1A7AC2` |
| `--brand-mandy: #c41e3a` | `--brand-mandy: #CC0000` (Honda red) |

---

## 3. Typography

| Role | Font Stack | Usage |
|------|------------|-------|
| **Display / Headings** | `'Source Serif 4', Georgia, serif` | Brand title, headings |
| **Body** | `'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif` | Body text, UI |
| **Mono** | `'JetBrains Mono', 'SF Mono', monospace` | Code, event badges |

*Note: Patty Peck website uses clean sans-serif. Current fonts (DM Sans, Source Serif 4) are acceptable; consider switching display to a bolder sans-serif if a more automotive feel is desired.*

---

## 4. Brand Copy — Exact Replacements

### Header

| Current | New |
|---------|-----|
| **Title:** Gavigans | **Title:** Patty Peck Honda |
| **Subtitle:** Multi-Agent Platform | **Subtitle:** AI Assistant |

### Page Title (`index.html`)

| Current | New |
|---------|-----|
| `<title>frontend</title>` | `<title>Patty Peck Honda | AI Assistant</title>` |

### Welcome Message (`useSSEChat.js`)

| Current | New |
|---------|-----|
| `Welcome to Gavigans! 🤖\n\nI'm your AI assistant powered by AiPRL Assist.\nHow can I help you today?` | `Welcome to Patty Peck Honda!\n\nI'm your AI assistant. How can I help you with vehicles, service, or financing today?` |

### Chat Input Placeholder (`ChatInput.jsx`)

| Current | New |
|---------|-----|
| `Ask about furniture, locations, appointments...` | `Ask about vehicles, inventory, service, or financing...` |

### Suggestion Pills (`ChatInput.jsx`)

| Current | New |
|---------|-----|
| What are your store hours? | What are your hours? |
| Tell me about financing | Tell me about financing |
| Book an appointment | Schedule service |
| Help me find furniture | Help me find a Honda |

### Environment / Config

| Variable | Current | New |
|----------|---------|-----|
| `VITE_APP_NAME` | `gavigans_agent` | `pattypeck_agent` |
| Storage key (user) | `gavigans_chat_user_id` | `pattypeck_chat_user_id` |
| Storage key (session) | `gavigans_chat_session_id` | `pattypeck_chat_session_id` |

---

## 5. Logo & Assets

### Header Logo

| Current | New |
|---------|-----|
| `https://imageresizer.furnituredealer.net/img/remote/images.furnituredealer.net/img/dealer/13381/upload/logo/507d3c181b1545dc83336fd9cc1781cb.png` | **Patty Peck Honda logo** — Use official logo from pattypeckhonda.com or provided asset. If unavailable, use text-only: "Patty Peck Honda" styled per brand. |

### AI Avatar (Chat Bubbles)

| Current | New |
|---------|-----|
| `https://res.cloudinary.com/diqbbssim/image/upload/v1771349436/t1ioo2vtk4s9vys4auyh.png` | Replace with Patty Peck–branded avatar or Honda-style icon. Options: (1) Patty Peck logo scaled down, (2) Honda "H" icon, (3) Generic car/assistant icon in brand blue. |

### Favicon

| Current | New |
|---------|-----|
| `/vite.svg` | Replace with Patty Peck Honda favicon or Honda "H" icon. |

---

## 6. Files to Modify (Frontend Only)

| File | Changes |
|------|---------|
| `src/App.jsx` | Brand title, subtitle, logo URL |
| `index.html` | Page title, favicon |
| `src/index.css` | All CSS variables (colors) |
| `src/hooks/useSSEChat.js` | Welcome message, `APP_NAME`, storage keys |
| `src/components/ChatInput.jsx` | Placeholder, suggestion pills |
| `src/components/ChatMessage.jsx` | AI avatar URL |
| `frontend/.env.example` | `VITE_APP_NAME` default |

---

## 7. CSS Variable Replacements (index.css)

Replace the following in `:root`:

```css
/* OLD (Gavigans - burgundy) */
--bubble-bg: #6f0302;
--teaser-bg: #6f0302;
--brand-primary: #6f0302;
--brand-primary-dark: #5a0202;
--brand-primary-light: #8a0403;
--brand-mandy: #c41e3a;

/* NEW (Patty Peck Honda - blue) */
--bubble-bg: #0066B3;
--teaser-bg: #0066B3;
--brand-primary: #0066B3;
--brand-primary-dark: #004C8A;
--brand-primary-light: #1A7AC2;
--brand-mandy: #CC0000;
```

Also update shadow tints from burgundy to blue where applicable:

```css
/* OLD - rgba(111, 3, 2, ...) */
/* NEW - rgba(0, 102, 179, ...) */
```

Search for `rgba(111, 3, 2` and replace with `rgba(0, 102, 179` for consistency.

---

## 8. Summary Checklist

- [ ] Update all color variables in `index.css`
- [ ] Replace brand title: "Gavigans" → "Patty Peck Honda"
- [ ] Replace subtitle: "Multi-Agent Platform" → "AI Assistant"
- [ ] Replace header logo URL with Patty Peck Honda logo
- [ ] Replace AI avatar URL with Patty Peck–branded asset
- [ ] Update page title in `index.html`
- [ ] Update favicon
- [ ] Update welcome message in `useSSEChat.js`
- [ ] Update chat placeholder in `ChatInput.jsx`
- [ ] Update suggestion pills in `ChatInput.jsx`
- [ ] Update `VITE_APP_NAME` and storage keys in `useSSEChat.js`
- [ ] Update `.env.example` with new default
- [ ] Verify no backend files are modified

---

## 9. Reference: Patty Peck Honda Website

- **URL:** https://www.pattypeckhonda.com/
- **Logo:** "PattyPeck" (bold) + "Honda" (smaller) — typographic, black
- **Primary color:** Blue (nav, icons, CTAs)
- **Tone:** Professional, automotive, customer-service focused

---

*Document created for Patty Peck Honda frontend rebrand. Backend remains unchanged.*
