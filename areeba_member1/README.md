# IBE Flask Backend

This project provides a clean Flask backend scaffold for a Boneh-Franklin Identity-Based Encryption workflow. The current implementation uses mock cryptographic behavior, SQLite storage, structured JSON responses, request timestamp validation, and CORS support for frontend integration.

## Requirements

- Python 3.10+
- `pip`

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

The app starts on the default Flask development server.

## API Notes

- Every request must include the `X-Request-Timestamp` header.
- The timestamp is checked against a small clock-skew window to reduce replay risk.
- Responses use the shared format:

```json
{ "status": "success", "data": {} }
{ "status": "error", "message": "..." }
```

## Main Endpoints

- `POST /register`
- `GET /public-params`
- `POST /extract-key`
- `POST /encrypt`
- `POST /decrypt`

## Project Structure

- `app.py` - Flask app factory and global middleware
- `database.py` - SQLite connection and persistence helpers
- `models.py` - User schema
- `routes/` - HTTP route definitions only
- `services/` - Request orchestration and application logic
- `ibe_module/` - Mock Boneh-Franklin crypto helpers