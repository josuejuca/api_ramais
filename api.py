#!/usr/bin/env python3

import sqlite3
import os
from fastapi import FastAPI

app = FastAPI()

# Caminho do banco SQLite (mesmo que no event_listener.py)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logins.db")

@app.get("/")
def root():
    return {"message": "API de Logins do FreeSWITCH está no ar!"}

@app.get("/logins")
def get_logins():
    """
    Retorna todos os registros de login salvos no SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_name, user, domain, timestamp FROM freeswitch_logins ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # Transforma cada linha em um dicionário para o JSON
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "event_name": r[1],
            "user": r[2],
            "domain": r[3],
            "timestamp": r[4],
        })

    return result
