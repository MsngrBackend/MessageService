from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from ..models import Message


async def add_message(
        session: AsyncSession,
        chat_id: int,
        content: str,
        sender_id: str
) -> Message:
    new_message = Message(
        chat_id=chat_id,
        content=content,
        sender_id=sender_id,
        created_at=func.now()
    )
    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)  # обновляет ID и timestamps
    return new_message


async def get_messages_by_chat(
        session: AsyncSession,
        chat_id: int,
        limit: int = 100,
        offset: int = 0
) -> List[Message]:
    stmt = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(desc(Message.created_at))
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())

async def update_message(
        session: AsyncSession,
        message_id: int,
        content: str
) -> Message | None:
    stmt = select(Message).where(Message.id == message_id)
    result = await session.execute(stmt)
    message = result.scalar_one_or_none()

    if message is None:
        return None

    message.content = content
    await session.commit()
    await session.refresh(message)
    return message


async def delete_message(
        session: AsyncSession,
        message_id: int
) -> bool:
    stmt = select(Message).where(Message.id == message_id)
    result = await session.execute(stmt)
    message = result.scalar_one_or_none()

    if message is None:
        return False

    await session.delete(message)
    await session.commit()
    return True