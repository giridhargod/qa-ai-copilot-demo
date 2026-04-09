import sqlite3
import json
from datetime import datetime

DB_NAME = "copilot.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input TEXT,
        context TEXT,
        ui_analysis TEXT,
        testcases TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_run(input_text, context, ui_analysis, testcases):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO knowledge (input, context, ui_analysis, testcases, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        input_text,
        context,
        ui_analysis,
        json.dumps(testcases),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def fetch_similar_knowledge():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT input, ui_analysis, testcases
    FROM knowledge
    ORDER BY id DESC
    LIMIT 3
    """)

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "input": row[0],
            "ui_analysis": row[1],
            "testcases": json.loads(row[2])
        })

    return results