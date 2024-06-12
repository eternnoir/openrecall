import sqlite3
from collections import namedtuple
from typing import Any, List

from openrecall.config import db_path

Entry = namedtuple("Entry", ["id", "app", "title", "text", "timestamp", "embedding"])


def create_db() -> None:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS entries
               (id INTEGER PRIMARY KEY AUTOINCREMENT, app TEXT, title TEXT, text TEXT, timestamp INTEGER, embedding BLOB)"""
        )
        conn.commit()


def get_all_entries() -> List[Entry]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        results = c.execute("SELECT * FROM entries").fetchall()
        return [Entry(*result) for result in results]


def get_sampled_entries(start_time: int, end_time: int, num_samples: int) -> List[Entry]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = f"""
        WITH RankedData AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (ORDER BY timestamp) AS row_num,
                COUNT(*) OVER () AS total_rows
            FROM 
                entries
            WHERE 
                timestamp BETWEEN ? AND ?
        ),
        FilteredData AS (
            SELECT 
                *,
                (row_num - 1) / (total_rows / ?) AS bucket
            FROM 
                RankedData
        )
        SELECT 
            id, 
            app, 
            title, 
            text, 
            timestamp, 
            embedding
        FROM 
            FilteredData
        GROUP BY 
            bucket
        ORDER BY 
            bucket;
        """
        c.execute(query, (start_time, end_time, num_samples))
        results = c.fetchall()
        return [Entry(*result) for result in results]


def search_entries(query: str) -> List[Entry]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        results = c.execute(
            "SELECT * FROM entries WHERE text LIKE ? ORDER BY timestamp DESC",
            (f"%{query}%",),
        ).fetchall()
        return [Entry(*result) for result in results]


def get_timestamps() -> List[int]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        results = c.execute(
            "SELECT timestamp FROM entries ORDER BY timestamp DESC LIMIT 1000"
        ).fetchall()
        return [result[0] for result in results]


def insert_entry(
        text: str, timestamp: int, embedding: Any, app: str, title: str
) -> None:
    embedding_bytes = embedding.tobytes()
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO entries (text, timestamp, embedding, app, title) VALUES (?, ?, ?, ?, ?)",
            (text, timestamp, embedding_bytes, app, title),
        )
        conn.commit()
