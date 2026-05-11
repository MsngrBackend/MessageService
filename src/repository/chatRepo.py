from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Chat, ChatMembers


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_chats_by_user(self, user_id: str) -> list[Chat]:
        result = await self.session.execute(
            select(Chat)
            .join(ChatMembers, Chat.id == ChatMembers.chat_id)
            .where(ChatMembers.user_id == user_id)
        )
        return result.scalars().all()

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        result = await self.session.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()
    
    async def create_chat(self, name: str) -> Chat:
        chat = Chat(name=name)
        self.session.add(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat
    
    async def add_member(self, chat_id: int, user_id: str) -> ChatMembers:
        member = ChatMembers(chat_id=chat_id, user_id=user_id)
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member
    
    async def get_member(self, chat_id: int, user_id: str) -> ChatMembers | None:
        result = await self.session.execute(
            select(ChatMembers)
            .where(ChatMembers.chat_id == chat_id)
            .where(ChatMembers.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def remove_member(self, chat_id: int, user_id: str) -> None:
        await self.session.execute(
            delete(ChatMembers)
            .where(ChatMembers.chat_id == chat_id)
            .where(ChatMembers.user_id == user_id)
        )
        await self.session.flush()
        
    async def get_members(self, chat_id: int) -> list[ChatMembers]:
        result = await self.session.execute(
            select(ChatMembers).where(ChatMembers.chat_id == chat_id)
        )
        return result.scalars().all()
    
    async def delete_chat(self, chat_id: int) -> None:
        await self.session.execute(
            delete(Chat).where(Chat.id == chat_id)
        )
        await self.session.flush()
