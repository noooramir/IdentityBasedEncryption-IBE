from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g
from models import User


def get_db() -> sqlite3.Connection:
    database_path = current_app.config["DATABASE"]
    connection = g.get("db")

    if connection is None:
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        g.db = connection

    return connection


def close_db(_: object | None = None) -> None:
    connection = g.pop("db", None)

    if connection is not None:
        connection.close()


def init_db() -> None:
    database_path = Path(current_app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identity TEXT NOT NULL UNIQUE,
                private_key TEXT
            )
            """
        )
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "private_key" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN private_key TEXT")
        connection.commit()
    finally:
        connection.close()


def create_user(identity: str) -> User:
    db = get_db()

    try:
        cursor = db.execute(
            "INSERT INTO users (identity) VALUES (?)",
            (identity,),
        )
        db.commit()
        return User(id=int(cursor.lastrowid), identity=identity)
    except sqlite3.IntegrityError as exc:
        raise ValueError("identity already exists") from exc


def get_user(identity: str):
    db = get_db()
    return db.execute(
        "SELECT id, identity, private_key FROM users WHERE identity = ?",
        (identity,),
    ).fetchone()


def get_user_public(identity: str):
    db = get_db()
    return db.execute(
        "SELECT id, identity FROM users WHERE identity = ?",
        (identity,),
    ).fetchone()


def save_private_key(identity: str, key: str) -> None:
    db = get_db()
    cursor = db.execute(
        "UPDATE users SET private_key = ? WHERE identity = ?",
        (key, identity),
    )
    db.commit()

    if cursor.rowcount == 0:
        raise ValueError("identity not found")
