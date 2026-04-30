# Member 2 Backend Implementation - IBE Flask Application

## Overview

Member 2 developed the complete Flask backend infrastructure for the Boneh-Franklin Identity-Based Encryption (IBE) system. This backend integrates Member 1's cryptographic core into a production-ready REST API with request validation, database persistence, and standardized response handling.

## Responsibilities & Deliverables

### 1. Flask Application Factory (`app.py`)
- **Purpose:** Bootstrap and configure the Flask application
- **Key Components:**
  - Application factory pattern for extensibility
  - CORS (Cross-Origin Resource Sharing) configuration for frontend integration
  - Blueprint registration for auth and IBE routes
  - Global middleware for request timestamp validation
  - Centralized error handlers (400, 404, 405 responses)
  - Database initialization and cleanup hooks
  - Flask context management

### 2. Database Layer (`database.py`)
- **Purpose:** Manage SQLite persistence and user data
- **Key Features:**
  - Connection pooling and thread-safe database access using Flask's `g` context
  - Automatic schema creation with migration support
  - **Schema:** Users table with `id`, `identity` (unique), and `private_key` columns
  - **Core Operations:**
  - `get_db()` - Thread-safe database connection retrieval
  - `init_db()` - Initialize database and handle schema migrations
  - `create_user(identity)` - Register new user identity (409 on duplicate)
  - `get_user(identity)` - Retrieve full user record including private key
  - `get_user_public(identity)` - Retrieve public user info only
  - `save_private_key(identity, key)` - Store extracted private key
  - `close_db()` - Graceful connection cleanup

### 3. Data Models (`models.py`)
- **User Dataclass:** Represents a user in the system
  - `id` (int) - Database primary key
  - `identity` (str) - User's identity string (e.g., email)
  - `private_key` (str, optional) - Extracted IBE private key
  - `public_dict()` - Returns sanitized public representation

### 4. API Routes (`routes/`)

#### Auth Routes (`routes/auth_routes.py`)
- **Endpoint:** `POST /register`
- **Purpose:** Register a new user identity
- **Input:** `{"identity": "user@example.com"}`
- **Output:** `{"status": "success", "data": {"id": 1, "identity": "user@example.com"}, "message": "..."}`
- **Status Codes:** 201 (created), 400 (invalid), 409 (conflict - identity already exists)

#### IBE Routes (`routes/ibe_routes.py`)
- **Endpoint:** `GET /ibe/status`
  - Returns readiness status of IBE module
  
- **Endpoint:** `GET /public-params`
  - Returns Master Public Parameters (MPK) for encryption
  
- **Endpoint:** `POST /extract-key`
  - Input: `{"identity": "user@example.com"}`
  - Output: Extracted private key for the identity
  - Requires: User must be registered first
  
- **Endpoint:** `POST /encrypt`
  - Input: `{"receiver_id": "user@example.com", "message": "plaintext"}`
  - Output: Ciphertext bundle ready for transmission
  
- **Endpoint:** `POST /decrypt`
  - Input: `{"ciphertext": "...", "private_key": "..."}`
  - Output: Recovered plaintext message

**Note:** All routes except CORS preflight require `X-Request-Timestamp` header

### 5. Service Layer (`services/`)

#### Auth Service (`services/auth_service.py`)
- **`register_user(payload)`**
  - Validates required fields (identity)
  - Checks for duplicate identities
  - Creates new user record
  - Returns standardized response with HTTP status codes
  - Error handling for malformed requests

#### IBE Service (`services/ibe_service.py`)
- **`get_ibe_status()`** - Returns IBE module readiness
- **`get_public_params()`** - Retrieves and returns MPK (Master Public Parameters)
- **`extract_private_key(payload)`**
  - Validates identity string
  - Checks identity is registered
  - Calls Member 1's `extract()` function
  - Persists extracted key to database
  - Returns key to client
  
- **`encrypt_message(payload)`**
  - Validates receiver_id and message
  - Checks receiver is registered
  - Retrieves public parameters
  - Calls Member 1's `encrypt()` function
  - Returns ciphertext bundle
  
- **`decrypt_message(payload)`**
  - Validates ciphertext and private_key
  - Calls Member 1's `decrypt()` function
  - Returns plaintext (never logs private key)

### 6. Request Security Layer (`request_security.py`)

#### Timestamp Validation
- **`validate_request_timestamp(raw_timestamp)`**
  - Enforces `X-Request-Timestamp` header requirement
  - Verifies Unix timestamp is within ±300 second window
  - Mitigates replay attacks without requiring full nonce store
  - Tolerates reasonable clock skew for distributed clients

#### JSON Payload Validation
- **`validate_json_payload(payload, required_fields)`**
  - Ensures request body is valid JSON
  - Validates presence of required fields
  - Trims whitespace from string inputs
  - Returns tuple: (cleaned_payload, error_message)

### 7. Standardized Response Handler (`api_response.py`)

#### Response Format
All endpoints return consistent JSON structure:
```json
{
  "status": "success|error",
  "data": { ... },
  "message": "optional human-readable message"
}
```

- **`success_response(data, message, status_code)`**
  - Wraps response data in standard format
  - Supports optional message and custom status codes
  - Default: 200 OK
  - Common: 201 Created for new resources

- **`error_response(message, status_code)`**
  - Returns error object with message
  - Default: 400 Bad Request
  - Common: 404 Not Found, 409 Conflict

### 8. Configuration (`config.py`)
- **Flask Configuration Class**
  - `SECRET_KEY` - Session/CSRF token secret
  - `DATABASE` - SQLite file path (`ibe.sqlite3`)
  - `JSON_SORT_KEYS` - Disabled for custom ordering
  - `PROPAGATE_EXCEPTIONS` - Disabled for custom error handling

## Architecture & Design Patterns

### Separation of Concerns
- **Routes** - HTTP handling only (parameter extraction, middleware)
- **Services** - Business logic and orchestration
- **Database** - Persistence layer
- **Models** - Data representation
- **Utilities** - Cross-cutting concerns (security, response formatting)

### Security Considerations
1. **Request Timestamp Validation** - Prevents replay attacks
2. **Identity Canonicalization** - Consistent string handling (trim/lowercase recommended)
3. **Private Key Protection** - Never logged or echoed back in responses
4. **Input Validation** - Required fields checked before processing
5. **SQL Injection Prevention** - Parameterized queries
6. **CORS Support** - Allows frontend integration with proper origin control

### Error Handling
- Centralized error response formatting
- Proper HTTP status codes (201, 400, 404, 409)
- User-friendly error messages
- Application logging for debugging

## Installation & Running

### Requirements
```
Flask>=3.0.0
Flask-Cors>=4.0.0
charm-crypto
```

### Setup
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python app.py
```

The application starts on Flask's default development server (typically `http://localhost:5000`).

## Integration with Member 1's Cryptographic Core

Member 2's backend integrates Member 1's IBE implementation via the `ibe_module/` import:
- Calls `setup()` to retrieve public parameters
- Calls `extract(identity)` to generate private keys
- Calls `encrypt(public_params, receiver_id, message)` for encryption
- Calls `decrypt(ciphertext, private_key)` for decryption

The service layer handles:
- Input validation before crypto calls
- Database persistence of user identities and private keys
- Response serialization for transport
- Error handling and logging

## Data Flow

### Registration Flow
```
Client POST /register 
  → Routes validate headers/body
  → Service checks duplicate
  → Database creates user
  → Return 201 with user ID
```

### Encryption Flow
```
Client POST /encrypt 
  → Validate receiver_id and message
  → Check receiver exists in DB
  → Retrieve public parameters
  → Call Member 1's encrypt()
  → Return ciphertext bundle
```

### Key Extraction Flow
```
Client POST /extract-key 
  → Validate identity
  → Check identity registered
  → Call Member 1's extract()
  → Store private key in DB
  → Return private key to client
```

## Testing Endpoints

### Register a User
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -H "X-Request-Timestamp: $(date +%s)" \
  -d '{"identity": "alice@example.com"}'
```

### Get Public Parameters
```bash
curl -X GET http://localhost:5000/public-params \
  -H "X-Request-Timestamp: $(date +%s)"
```

### Extract Private Key
```bash
curl -X POST http://localhost:5000/extract-key \
  -H "Content-Type: application/json" \
  -H "X-Request-Timestamp: $(date +%s)" \
  -d '{"identity": "alice@example.com"}'
```

## Files Summary

| File | Purpose |
|------|---------|
| `app.py` | Flask application factory & middleware |
| `database.py` | SQLite connection & user persistence |
| `models.py` | User dataclass definition |
| `config.py` | Application configuration |
| `routes/auth_routes.py` | User registration endpoint |
| `routes/ibe_routes.py` | IBE crypto endpoints |
| `services/auth_service.py` | User registration logic |
| `services/ibe_service.py` | IBE orchestration logic |
| `request_security.py` | Timestamp & payload validation |
| `api_response.py` | Standardized response formatting |
| `requirements.txt` | Python dependencies |

## Key Achievements

✅ **Production-Ready Flask Backend** - Clean architecture with separation of concerns  
✅ **Secure Request Handling** - Timestamp validation, input sanitization, parameterized queries  
✅ **Database Persistence** - SQLite integration with automatic migrations  
✅ **Standardized API Responses** - Consistent JSON format across all endpoints  
✅ **Error Handling** - Comprehensive error responses with proper HTTP status codes  
✅ **Frontend Integration** - CORS support for client-side applications  
✅ **Logging & Debugging** - Application logging for security-sensitive operations  
✅ **Code Organization** - Maintainable structure following Flask best practices  

---

**Member 2 - Backend Implementation**  
Date: 2026  
Information Security Project
