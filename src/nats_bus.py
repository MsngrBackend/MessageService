"""
NATS: fan-out событий чата между инстансами MessageService и публикация статуса пользователя.
Если NATS_URL не задан, события обрабатываются только локально (как до внедрения NATS).
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from nats.aio.client import Client as NATS

logger = logging.getLogger(__name__)

_nc: NATS | None = None


def is_connected() -> bool:
    return _nc is not None and _nc.is_connected


async def start_nats() -> None:
    global _nc
    url = os.getenv("NATS_URL", "").strip()
    if not url:
        logger.info("NATS_URL не задан — fan-out чата только внутри процесса")
        return

    try:
        _nc = NATS()
        await _nc.connect(servers=[url])
    except Exception as e:
        logger.warning(
            "NATS: подключение не удалось (%s) — работа только локальный fan-out",
            e,
        )
        _nc = None
        return

    async def on_chat_event(msg) -> None:
        try:
            from src.manager import dispatch_chat_event

            data = json.loads(msg.data.decode())
            await dispatch_chat_event(data)
        except Exception:
            logger.exception("NATS: ошибка обработки события чата")

    await _nc.subscribe("msngr.chat.*.event", cb=on_chat_event)
    logger.info("NATS: подключено, подписка msngr.chat.*.event")


async def stop_nats() -> None:
    global _nc
    if _nc is not None:
        try:
            await _nc.drain()
        except Exception:
            logger.exception("NATS: ошибка при drain")
        _nc = None


async def notify_chat_event(chat_id: int, event: dict[str, Any]) -> None:
    """Рассылка события чата: через NATS (все инстансы) или только локально."""
    payload = {"chat_id": chat_id, **event}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    if _nc is not None and _nc.is_connected:
        subject = f"msngr.chat.{chat_id}.event"
        await _nc.publish(subject, body)
        return

    from src.manager import dispatch_chat_event

    await dispatch_chat_event(payload)


async def publish_user_status(user_id: str, status: str) -> None:
    """Событие онлайн/оффлайн (подписчики — другие сервисы, например Profile)."""
    if _nc is None or not _nc.is_connected:
        return
    payload = json.dumps(
        {"user_id": user_id, "status": status}, ensure_ascii=False
    ).encode("utf-8")
    await _nc.publish("msngr.user.status", payload)
