from src.manager import ConnectionManager
from src.db import engine, Base
import src.models
from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Tables before:", Base.metadata.tables.keys())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

manager = ConnectionManager()

app = FastAPI(title="Messanger Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
