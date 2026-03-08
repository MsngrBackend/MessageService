from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from src.service.message_service import add_message, get_messages_by_chat, update_message, delete_message

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)


@router.post("/")
async def create_message(
    chat_id: int,
    content: str,
    sender_id: int,
    db: AsyncSession = Depends(get_db)
):
    message = await add_message(db, chat_id, content, sender_id)
    return {"id": message.id, "content": message.content}


@router.get("/chats/{chat_id}/messages/")
async def read_messages(
    chat_id: int,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    messages = await get_messages_by_chat(db, chat_id, limit, offset)
    return messages

@router.patch("/{message_id}/")
async def update_message_endpoint(
    message_id: int,
    content: str,
    db: AsyncSession = Depends(get_db)
):
    message = await update_message(db, message_id, content)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"id": message.id, "content": message.content}


@router.delete("/{message_id}/")
async def delete_message_endpoint(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"detail": "Message deleted"}