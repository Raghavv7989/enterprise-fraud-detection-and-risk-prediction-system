from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
from sqlalchemy.exc import OperationalError

from database import engine, SessionLocal, Base
from models import Transaction
from stream import transaction_stream
from alerts import check_alert

app = FastAPI(title="Enterprise Fraud Detection")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB WAIT LOGIC ----------
def wait_for_db():
    retries = 10
    while retries > 0:
        try:
            engine.connect()
            print("✅ Database connected")
            return
        except OperationalError:
            retries -= 1
            print("⏳ Waiting for database...")
            time.sleep(2)
    raise RuntimeError("❌ Database not available")

# ---------- STARTUP ----------
@app.on_event("startup")
async def startup():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(transaction_stream())
    print("🚀 Fraud stream started")

# ---------- WEBSOCKET ----------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        await asyncio.sleep(2)

        db = SessionLocal()
        rows = (
            db.query(Transaction)
            .order_by(Transaction.id.desc())
            .limit(50)
            .all()
        )
        db.close()

        stats = {"High": 0, "Medium": 0, "Low": 0}
        txs = []

        for r in rows:
            stats[r.risk] += 1
            txs.append({
                "id": r.id,
                "fraud_probability": r.fraud_probability,
                "risk_score": r.risk_score,
                "risk": r.risk
            })

        latest = txs[0] if txs else None

        await ws.send_json({
            "total": len(txs),
            "stats": stats,
            "transactions": txs,
            "alert": check_alert(latest["risk_score"]) if latest else False
        })