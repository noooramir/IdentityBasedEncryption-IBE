from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = "dev-secret-key-change-in-production"
    DATABASE = str(BASE_DIR / "ibe.sqlite3")
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False
