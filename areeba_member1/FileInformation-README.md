# FileInformation-README: IBE Backend Code Structure

This document explains the purpose and functionality of each code file in the IBE (Identity-Based Encryption) Flask backend.

---

## 📋 Project Overview

**IBE Secure Mail** is a Flask-based backend that implements Identity-Based Encryption workflows. It provides REST API endpoints for user registration, private key extraction, encryption, and decryption operations. Currently uses **mock cryptography** for demonstration purposes, ready for integration with real IBE algorithms (charm-crypto).

---

## 🗂️ Core Application Files

### **app.py**
**Purpose:** Flask application factory and main entry point  
**Key Responsibilities:**
- Creates the Flask application instance with configuration
- Registers API blueprints (auth and IBE routes)
- Sets up global middleware for request timestamp validation (replay attack defense)
- Configures error handlers (400, 404, 405, 500)
- Serves the frontend HTML at the root path (`/`)
- Initializes the SQLite database on startup

**Key Functions:**
- `create_app()` - Factory function that creates and configures the Flask app
- Global `@app.before_request` - Validates X-Request-Timestamp header on all requests

**Run Command:** `python app.py`

---

## ⚙️ Configuration & Database

### **config.py**
**Purpose:** Application configuration settings  
**Key Responsibilities:**
- Defines Flask configuration constants
- Sets the SQLite database path
- Configures security settings (SECRET_KEY)
- Sets JSON serialization behavior

**Key Settings:**
- `SECRET_KEY` - Flask session signing key (change in production)
- `DATABASE` - Path to `ibe.sqlite3`
- `JSON_SORT_KEYS = False` - Preserves JSON key order in responses

---

### **database.py**
**Purpose:** SQLite database connection and user data persistence  
**Key Responsibilities:**
- Manages database connection lifecycle with Flask's `g` context
- Initializes the users table on first run
- Creates, retrieves, and updates user records
- Handles private key storage

**Key Functions:**
- `get_db()` - Returns the active database connection
- `close_db()` - Safely closes database connection
- `init_db()` - Creates the users table if it doesn't exist
- `create_user(identity)` - Registers a new user with an identity string
- `get_user(identity)` - Retrieves user with full data (including private key)
- `get_user_public(identity)` - Retrieves only public user info (id, identity)
- `save_private_key(identity, key)` - Stores extracted private key for a user

**Database Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identity TEXT NOT NULL UNIQUE,
    private_key TEXT
)
```

---

### **models.py**
**Purpose:** User data model definition  
**Key Responsibilities:**
- Defines the `User` dataclass with type safety

**User Data Class:**
- `id` (int) - Database primary key
- `identity` (str) - Email/identity string (public key in IBE)
- `private_key` (str | None) - Extracted private key from KGC

**Key Methods:**
- `public_dict()` - Returns only public user data (excludes private_key)

---

## 🔐 Security & Request Handling

### **request_security.py**
**Purpose:** Request validation and replay attack defense  
**Key Responsibilities:**
- Validates incoming request timestamps
- Implements clock-skew based replay protection
- Validates JSON payload structure

**Key Functions:**
- `validate_request_timestamp(raw_timestamp)` - Checks if timestamp is within 300-second window of server time
- `validate_json_payload(payload, required_keys)` - Ensures required JSON fields are present

**Security Features:**
- X-Request-Timestamp header is mandatory on all requests
- Timestamps must be Unix epoch seconds
- Requests older/newer than ±300 seconds are rejected

---

### **api_response.py**
**Purpose:** Standardized JSON response formatting  
**Key Responsibilities:**
- Provides consistent response format across all API endpoints

**Key Functions:**
- `success_response(data, message, status_code)` - Returns `{"status": "success", "data": {...}, "message": "..."}`
- `error_response(message, status_code)` - Returns `{"status": "error", "message": "..."}`

**Response Format:**
```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message"
}
```

---

## 🛣️ API Routes

### **routes/auth_routes.py**
**Purpose:** User authentication and registration endpoints  
**Blueprint Name:** `auth`

**Endpoints:**
- `POST /register` - Registers a new identity
  - Calls: `register_user()` from auth_service

---

### **routes/ibe_routes.py**
**Purpose:** Identity-Based Encryption operation endpoints  
**Blueprint Name:** `ibe`

**Endpoints:**
- `GET /ibe/status` - KGC status check
  - Calls: `get_ibe_status()` from ibe_service
- `GET /public-params` - Retrieves public parameters (MPK)
  - Calls: `get_public_params()` from ibe_service
- `POST /extract-key` - Extracts private key for identity
  - Calls: `extract_private_key_service()` from ibe_service
- `POST /encrypt` - Encrypts message to a recipient identity
  - Calls: `encrypt_message_service()` from ibe_service
- `POST /decrypt` - Decrypts ciphertext using private key
  - Calls: `decrypt_message_service()` from ibe_service

---

## 🔧 Business Logic Services

### **services/auth_service.py**
**Purpose:** User registration business logic  
**Key Responsibilities:**
- Validates registration payload
- Checks if identity is already registered
- Creates new user in database
- Returns formatted success/error response

**Key Functions:**
- `register_user(payload)` - Orchestrates identity registration
  - Validates: JSON structure, identity uniqueness
  - Returns: User ID and identity on success
  - Status Code: 201 on success, 409 if duplicate

---

### **services/ibe_service.py**
**Purpose:** IBE cryptographic operations orchestration  
**Key Responsibilities:**
- Orchestrates all IBE operations (setup, extract, encrypt, decrypt)
- Validates request payloads
- Calls cryptographic functions from ibe_core
- Persists private keys to database
- Handles error conditions

**Key Functions:**
- `get_ibe_status()` - Returns KGC operational status
- `get_public_params()` - Generates and returns public parameters (MPK)
  - Calls: `setup()` from ibe_core
- `extract_private_key(payload)` - Extracts and stores private key for identity
  - Validates: Identity exists in database
  - Calls: `extract()` from ibe_core, then saves key to database
- `encrypt_message(payload)` - Encrypts plaintext message to recipient identity
  - Validates: Receiver identity is registered
  - Calls: `setup()` and `encrypt()` from ibe_core
- `decrypt_message(payload)` - Decrypts ciphertext using private key
  - Calls: `decrypt()` from ibe_core

---

## 🔬 Cryptography Module

### **ibe_module/ibe_core.py**
**Purpose:** Identity-Based Encryption cryptographic operations  
**Current Status:** Mock implementation (placeholders for real Charm-crypto)  
**Key Responsibilities:**
- Implements Boneh-Franklin IBE scheme operations
- Generates and validates cryptographic parameters

**Key Functions:**

#### `setup()`
- **Purpose:** KGC setup - generates master secret and public parameters
- **Returns:** 
  ```python
  {
    "success": True,
    "public_params": {
      "curve": "SS512",
      "generator": "dummy_generator",
      "hash_function": "SHA-256"
    }
  }
  ```
- **Note:** Master secret is generated internally, only public_params returned

#### `extract(identity)`
- **Purpose:** Generates private key for given identity
- **Input:** `identity` (str) - Email/identity string
- **Returns:** 
  ```python
  {
    "success": True,
    "identity": identity,
    "private_key": "mock-private-key-for:identity"
  }
  ```
- **Security:** Should only be callable by authenticated users

#### `encrypt(public_params, identity, message)`
- **Purpose:** Encrypts plaintext message for recipient identity
- **Inputs:**
  - `public_params` (dict) - Public parameters from setup
  - `identity` (str) - Recipient's identity (public key)
  - `message` (str) - Plaintext message
- **Returns:**
  ```python
  {
    "success": True,
    "ciphertext": "mock-ciphertext-for:identity",
    "message_preview": message
  }
  ```
- **Key Feature:** Only requires recipient's identity, no certificates needed

#### `decrypt(ciphertext, private_key)`
- **Purpose:** Decrypts ciphertext using private key
- **Inputs:**
  - `ciphertext` (str) - Encrypted message
  - `private_key` (str) - Recipient's private key (SK_ID)
- **Returns:**
  ```python
  {
    "success": True,
    "plaintext": "recovered message"
  }
  ```

---

## 🎨 Frontend Interface

### **index.html**
**Purpose:** Single-page web application frontend  
**Key Responsibilities:**
- Provides user interface for all IBE operations
- Handles timestamp header injection for API requests
- Displays results and error messages
- Manages client-side form state

**Frontend Pages:**
1. **Register** - Register new identity in KGC
2. **Key Extract** - Request private key from KGC
3. **Encrypt** - Encrypt message to recipient identity
4. **Decrypt** - Decrypt received ciphertext
5. **Public Params** - View KGC public parameters (MPK)

**Key Features:**
- Auto-generates X-Request-Timestamp header for all API calls
- Displays server status (online/offline)
- Copy-to-clipboard functionality for keys and ciphertext
- Dark theme with cybersecurity aesthetic
- Fallback to demo mode if backend is unreachable
- Form validation and error handling

---

## 📦 Dependencies

### **requirements.txt**
```
Flask>=3.0.0        # Web framework
Flask-Cors>=4.0.0   # Cross-Origin Resource Sharing
charm-crypto        # Cryptography library (for real IBE implementation)
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (index.html)                 │
│  Register → KeyExtract → Encrypt → Decrypt → Params    │
└─────────────────┬───────────────────────────────────────┘
                  │ (HTTP + X-Request-Timestamp)
                  ▼
┌─────────────────────────────────────────────────────────┐
│           FLASK APP (app.py)                            │
│  - Middleware: Timestamp validation                     │
│  - Error handlers: 400, 404, 405, 500                   │
│  - Blueprint registration                              │
└─────────────────┬───────────────────────────────────────┘
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
┌──────────────────┐  ┌────────────────────┐
│  auth_routes.py  │  │  ibe_routes.py     │
│  ─────────────   │  │  ──────────────    │
│  POST /register  │  │  GET /ibe/status   │
└──────────┬───────┘  │  GET /public-params│
           │          │  POST /extract-key │
           │          │  POST /encrypt     │
           │          │  POST /decrypt     │
           │          └────────────┬───────┘
           │                       │
           ▼                       ▼
    ┌─────────────────────────────────────┐
    │     SERVICES LAYER                  │
    │ ───────────────────────────────    │
    │ auth_service.py   ibe_service.py   │
    │ (register logic)   (IBE operations) │
    └────────┬──────────────────┬────────┘
             │                  │
    ┌────────▼────────┐  ┌──────▼──────────────┐
    │  database.py    │  │  ibe_module/       │
    │  ────────────   │  │  ibe_core.py       │
    │  User CRUD      │  │  ──────────────    │
    │  Private Key    │  │  setup()           │
    │  Management     │  │  extract()         │
    │                 │  │  encrypt()         │
    │                 │  │  decrypt()         │
    └────────┬────────┘  └──────────────────┘
             │
             ▼
    ┌─────────────────────┐
    │  ibe.sqlite3        │
    │  (SQLite Database)  │
    │  ─────────────────  │
    │  users table:       │
    │  - id               │
    │  - identity         │
    │  - private_key      │
    └─────────────────────┘
```

---

## 🔄 Typical Workflow

1. **User opens index.html** → Frontend loads
2. **User registers identity** → `POST /register`
   - Service validates, creates user in database
3. **User extracts key** → `POST /extract-key`
   - Service calls KGC extract, saves private key to database
4. **User encrypts message** → `POST /encrypt`
   - Service encrypts to recipient's identity
   - Recipient receives ciphertext
5. **User decrypts message** → `POST /decrypt`
   - Service decrypts using their private key
   - Plaintext recovered

---

## 🚀 Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py

# Open browser to http://localhost:5000
```

---

## 🔐 Security Notes

- **Timestamp Validation:** All requests must include X-Request-Timestamp header (prevents replay attacks)
- **CORS Enabled:** Frontend can be on different origin
- **Database:** SQLite in dev mode; use PostgreSQL for production
- **Private Keys:** Stored in database (encrypted at rest recommended for production)
- **Mock Crypto:** Current implementation uses mock functions; replace with real Charm-crypto for production

---

## 📝 File Categories Summary

| Category | Files | Purpose |
|----------|-------|---------|
| **Core App** | app.py | Flask application factory |
| **Configuration** | config.py | App settings |
| **Database** | database.py, models.py | User data persistence |
| **Security** | request_security.py, api_response.py | Validation & responses |
| **Routes** | auth_routes.py, ibe_routes.py | HTTP endpoints |
| **Services** | auth_service.py, ibe_service.py | Business logic |
| **Crypto** | ibe_module/ibe_core.py | IBE operations |
| **Frontend** | index.html | Web UI |
| **Dependencies** | requirements.txt | Python packages |

