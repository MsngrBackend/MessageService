from typing import Literal

from pydantic import BaseModel

from src.manager import EventTypes


class CreateChatRequest(BaseModel):
    name: str


class RenameChatRequest(BaseModel):
    name: str


class AddMemberRequest(BaseModel):
    user_id: str


class ChatResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MemberResponse(BaseModel):
    id: int
    chat_id: int
    user_id: str

    model_config = {"from_attributes": True}


class MessageEvent(BaseModel):
    type: Literal[EventTypes.MESSAGE]
    text: str


class TypingEvent(BaseModel):
    type: Literal[EventTypes.TYPING]


IncomingEvent = MessageEvent | TypingEvent
