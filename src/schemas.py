from enum import Enum
from typing import Literal

from pydantic import BaseModel


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


class EventTypes(str, Enum):
    SYSTEM = "system"
    MESSAGE = "message"
    TYPING = "typing"


class MessageEvent(BaseModel):
    type: Literal[EventTypes.MESSAGE]
    text: str


class TypingEvent(BaseModel):
    type: Literal[EventTypes.TYPING]


IncomingEvent = MessageEvent | TypingEvent
