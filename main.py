from src.db import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.handler.message_handler import router as messages_router
from src.manager import router as websocket_router
from src.handler.chatHandler import router as chat_router
from src.nats_bus import start_nats, stop_nats


class Application:
    def __init__(self):
        self.app = FastAPI(
            title="Messanger Service",
            version="1.0.0",
            lifespan=self._lifespan
        )
        self._setup_middleware()
        self._setup_routes()

    @asynccontextmanager
    async def _lifespan(self, _: FastAPI):
        print("Tables before:", Base.metadata.tables.keys())
        await start_nats()
        yield
        await stop_nats()
        await engine.dispose()

    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        self.app.include_router(messages_router)
        self.app.include_router(websocket_router)
        self.app.include_router(chat_router)
        self.app.add_api_route("/health", self._health)

    async def _health():
        return {"status": "ok"}


app = Application().app
