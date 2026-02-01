import asyncio
import random
from database import SessionLocal
from models import Transaction

async def transaction_stream():
    while True:
        db = SessionLocal()

        prob = round(random.uniform(0, 100), 2)
        score = int(prob)

        if score > 70:
            risk = "High"
        elif score > 30:
            risk = "Medium"
        else:
            risk = "Low"

        tx = Transaction(
            fraud_probability=prob,
            risk_score=score,
            risk=risk
        )

        db.add(tx)
        db.commit()
        db.close()

        await asyncio.sleep(2)