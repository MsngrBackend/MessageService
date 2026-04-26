from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.schemas import (
    ChatResponse,
    CreateChatRequest,
    AddMemberRequest,
    MemberResponse,
)
from src.service.chatService import ChatService


def get_current_user_id(x_user_id: str = Header(...)) -> str:
    return x_user_id


def get_service(session: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(session)


class ChatHandler:
    def __init__(self):
        self.router = APIRouter(prefix="/chats", tags=["Chats"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/", response_model=list[ChatResponse])
        async def get_chats_by_user(
            user_id: str = Depends(get_current_user_id),
            service: ChatService = Depends(get_service),
        ):
            return await service.get_user_chats(user_id)

        @self.router.get("/{chat_id}", response_model=ChatResponse)
        async def get_chat_by_id(
            chat_id: int,
            user_id: str = Depends(get_current_user_id),
            service: ChatService = Depends(get_service),
        ):
            try:
                return await service.get_chat(chat_id, user_id)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionError as e:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        @self.router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
        async def create_chat(
            chat: CreateChatRequest,
            user_id: str = Depends(get_current_user_id),
            service: ChatService = Depends(get_service),
        ):
            return await service.create_chat(chat.name, user_id)

        @self.router.get("/{chat_id}/members", response_model=list[MemberResponse])
        async def get_chat_members(
            chat_id: int,
            service: ChatService = Depends(get_service),
        ):
            return await service.get_members(chat_id)

        @self.router.post("/{chat_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
        async def add_chat_member(
            chat_id: int,
            member: AddMemberRequest,
            service: ChatService = Depends(get_service),
        ):
            try:
                return await service.add_member(chat_id, member.user_id)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        @self.router.delete("/{chat_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def remove_chat_member(
            chat_id: int,
            deleted_user_id: str,
            user_id: str = Depends(get_current_user_id),
            service: ChatService = Depends(get_service),
        ):
            try:
                return await service.remove_member(chat_id, deleted_user_id, user_id)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionError as e:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

        @self.router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_chat(
            chat_id: int,
            user_id: str = Depends(get_current_user_id),
            service: ChatService = Depends(get_service),
        ):
            try:
                return await service.delete_chat(chat_id, user_id)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionError as e:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


router = ChatHandler().router
