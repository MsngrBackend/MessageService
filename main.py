from src.db import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.handler.message_handler import router as messages_router
from src.manager import router as websocket_router
from src.handler.chatHandler import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Tables before:", Base.metadata.tables.keys())
    yield
    await engine.dispose()

app = FastAPI(title="Messanger Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages_router)
app.include_router(websocket_router)

app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
