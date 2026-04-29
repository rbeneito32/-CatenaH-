from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from datetime import datetime
import sqlite3
import urllib.parse
import asyncio

router = APIRouter()
DB_PATH = "analytics.db"

def init_click_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS clicks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT,
        tipo TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_click(request_id: str, tipo: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO clicks (request_id, tipo, timestamp) VALUES (?, ?, ?)", 
              (request_id, tipo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

@router.get("/out/{tipo}")
async def track_and_redirect(tipo: str, rid: str, target: str):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, log_click, rid, tipo)
    destino = urllib.parse.unquote(target)
    return RedirectResponse(destino)

# Generadores de Links (Affiliates)
def generar_link_tren(origen, destino, fecha):
    origen_fmt = origen.replace(" ", "%20")
    destino_fmt = destino.replace(" ", "%20")
    return f"https://www.thetrainline.com/search?origin={origen_fmt}&destination={destino_fmt}&outwardDate={fecha}"

def wrap_tracking_link(base_url, request_id, tipo):
    encoded = urllib.parse.quote(base_url, safe='')
    return f"/out/{tipo}?rid={request_id}&target={encoded}"
