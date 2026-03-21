from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Chat, ChatMembers
from src.repository.chatRepo import ChatRepository


class ChatService:
    def __init__(self, session: AsyncSession):
        self.repo = ChatRepository(session)
        self.session = session

    async def get_user_chats(self, user_id: str) -> list[Chat]:
        return await self.repo.get_chats_by_user(user_id)

    async def get_chat(self, chat_id: int, user_id: str) -> Chat:
        chat = await self.repo.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError("Чат не найден")

        member = await self.repo.get_member(chat_id, user_id)
        if not member:
            raise PermissionError("Вы не являетесь участником этого чата")

        return chat
    
    
    
    async def create_chat(self, name: str, creator_id: str) -> Chat:
        chat = await self.repo.create_chat(name)
        await self.repo.add_member(chat.id, creator_id)
        await self.session.commit()
        return chat
        
    async def get_members(self, chat_id: int) -> list[ChatMembers]:
        return await self.repo.get_members(chat_id)
    
    async def add_member(self, chat_id: int, user_id: str) -> ChatMembers:
        member = await self.repo.get_member(chat_id, user_id)
        if member:
            raise ValueError("Пользователь уже является участником этого чата")
        
        new_member = await self.repo.add_member(chat_id, user_id)
        await self.session.commit()
        return new_member
        
    async def remove_member(self, chat_id: int, user_id: str, requesting_user_id: str) -> None:
        member = await self.repo.get_member(chat_id, user_id)
        if not member:
            raise ValueError("Пользователь не является участником этого чата")
        
        requester = await self.repo.get_member(chat_id, requesting_user_id)
        if not requester:
            raise PermissionError("Вы не являетесь участником этого чата")
        
        await self.repo.remove_member(chat_id, user_id)
        await self.session.commit()

    async def delete_chat(self, chat_id: int, user_id: str) -> None:
        chat = await self.repo.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError("Чат не найден")
        
        member = await self.repo.get_member(chat_id, user_id)
        if not member:
            raise PermissionError("Вы не являетесь участником этого чата")
        
        await self.repo.delete_chat(chat_id)
        await self.session.commit()