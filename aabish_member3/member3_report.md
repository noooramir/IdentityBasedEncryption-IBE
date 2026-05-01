# Member 3 — Aabish: Frontend & Application Development
## IBE Secure Mail — Boneh-Franklin Identity-Based Encryption

---

## 1. Overview

Member 3 (Aabish) is responsible for the complete **frontend application** for the IBE Secure Mail system. The frontend provides a clean, production-ready web UI that allows users to interact with all five core IBE operations:

1. **Identity Registration** — Register an identity (email) with the KGC
2. **Private Key Extraction** — Request SK_ID from the KGC
3. **Message Encryption** — Encrypt using recipient's identity as public key
4. **Message Decryption** — Recover plaintext using SK_ID
5. **Public Parameters Viewer** — Inspect the KGC's MPK

---

## 2. Deliverables

| # | Deliverable | File | Status |
|---|-------------|------|--------|
| 1 | Frontend single-page application | `index.html` | ✅ Complete |
| 2 | Member 3 documentation report | `member3_report.md` | ✅ Complete |

---

## 3. File Structure

```
member3_frontend/
├── index.html          ← Single-file SPA (HTML + CSS + JS)
└── member3_report.md   ← This document
```

---

## 4. Application Pages & Features

### 4.1 Register Identity Page
- Input field for identity string (email address)
- Calls `POST /register` with `X-Request-Timestamp` header
- Displays registration result (user ID, status)
- Step indicator guiding user to next action (Key Extract)

### 4.2 Key Extraction Page
- Input for registered identity
- Calls `POST /extract-key`
- Displays extracted private key SK_ID in styled mono box
- Copy-to-clipboard button for key transport
- Security warning: key must never be shared

### 4.3 Encrypt Message Page
- Recipient identity input (acts as public key — no lookup needed)
- Plaintext message textarea
- Calls `POST /encrypt` with `{ receiver_id, message }`
- Displays formatted ciphertext bundle
- Auto-fills ciphertext into Decrypt page for convenience

### 4.4 Decrypt Message Page
- Identity input, private key (SK_ID) textarea, ciphertext textarea
- Calls `POST /decrypt` with `{ identity, private_key, ciphertext }`
- Displays recovered plaintext

### 4.5 Public Parameters Page
- Fetches and renders KGC Master Public Key (MPK)
- Stat cards showing curve type, hash scheme, server status
- Calls `GET /public-params`
- Provides educational context on Boneh-Franklin IBE parameters

---

## 5. Backend API Integration

The frontend integrates with Member 2's (Noor's) Flask backend via REST API calls.

### Request Convention
All requests include the required `X-Request-Timestamp: <unix_epoch>` header to satisfy Member 2's replay-attack mitigation middleware.

```javascript
const headers = {
  'Content-Type': 'application/json',
  'X-Request-Timestamp': Math.floor(Date.now() / 1000).toString()
};
```

### API Endpoints Used

| Method | Endpoint | Used In |
|--------|----------|---------|
| `POST` | `/register` | Register page |
| `POST` | `/extract-key` | Key Extract page |
| `POST` | `/encrypt` | Encrypt page |
| `POST` | `/decrypt` | Decrypt page |
| `GET`  | `/public-params` | Public Params page |
| `GET`  | `/ibe/status` | Nav bar (health check) |

### Error Handling
- Network/server errors trigger toast notifications
- **Demo mode fallback**: when the server is unreachable (e.g. during development), the UI degrades gracefully by showing demo output so the UI flow can be demonstrated end-to-end without the backend running.
- HTTP error codes (400, 409, 404) are parsed and displayed as human-readable messages.

---

## 6. Technical Design Decisions

### 6.1 Single-File SPA (No Build Tool)
The entire application is a single `index.html` with embedded CSS and JavaScript. This was chosen because:
- Zero build toolchain dependency (no npm, webpack, etc.)
- Directly openable in a browser for demos
- Simple to hand off to teammates

### 6.2 Security-Conscious UI
- **Private key never auto-submitted** — user must explicitly paste it
- **No key storage** — keys exist only in DOM text nodes (session memory, not localStorage)
- **Timestamp on every API call** — matches backend replay-attack mitigation
- **Input sanitization**: identities are `.trim().toLowerCase()` before sending

### 6.3 Design Aesthetic
The UI uses a **dark terminal/cipher aesthetic** that matches the cryptographic theme:
- Dark background (`#0a0e14`) with cyan accent (`#00e5ff`)
- Monospaced font (Fira Code) for keys/ciphertext
- Syne display font for headings
- Subtle grid pattern background
- Animated loading states on async operations
- Status dot in navbar reflects live server health

---

## 7. Demo Flow (Walkthrough)

### Full End-to-End Demo Steps

1. **Open** `index.html` in browser (backend running at `localhost:5000`)
2. **Register** → Enter `alice@example.com` → Click "Register Identity" → ID confirmed
3. **Key Extract** → Enter `alice@example.com` → Click "Extract Key" → SK_ID displayed and copied
4. **Encrypt** → Recipient: `alice@example.com`, Message: `"Hello Alice, this is a secret!"` → Ciphertext displayed
5. **Decrypt** → Identity: `alice@example.com`, paste SK_ID and ciphertext → Plaintext recovered
6. **Public Params** → Click "Refresh Parameters" → MPK components shown

---

## 8. Key Design Choices for IBE UX

| IBE Property | UX Expression |
|---|---|
| Identity = Public Key | Recipient field labeled "Recipient Identity (Public Key)" |
| No certificate lookup | UI note: "No certificate or key exchange needed" |
| KGC is trusted third party | KGC status indicator always visible in nav |
| Private key is secret | Warning banner on key extraction page |
| Ciphertext is data bundle | Output displayed as formatted JSON, not opaque blob |

---

## 9. Testing Checklist

- [x] Register new identity → 201 response shown
- [x] Register duplicate identity → 409 handled gracefully
- [x] Extract key for registered identity → SK_ID displayed
- [x] Extract key for unregistered identity → error message shown
- [x] Encrypt with valid recipient → ciphertext bundle shown
- [x] Decrypt with correct key → plaintext recovered
- [x] Decrypt with wrong key → error message shown
- [x] Public params fetch → MPK components rendered
- [x] Server offline → demo mode fallback, no crash
- [x] Copy-to-clipboard → all output boxes have copy buttons
- [x] Server status dot → live health check every 15s

---

## 10. Security Notes

- Private keys are **never persisted** client-side (no localStorage, no cookies)
- All sensitive output is displayed in-page and cleared on page reload
- The `X-Request-Timestamp` header is sent with every API call to satisfy backend anti-replay checks
- CORS is handled by Member 2's backend (`Flask-CORS`)

---

**Member 3 — Aabish**  
Frontend & Application Development  
Information Security Term Project — IBE Boneh-Franklin  
2026
