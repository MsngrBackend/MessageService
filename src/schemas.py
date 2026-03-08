from pydantic import BaseModel

class CreateChatRequest(BaseModel):
    name: str


class RenameChatRequest(BaseModel):
    name: str


class AddMemberRequest(BaseModel):
    user_id: int

class ChatResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MemberResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int

    model_config = {"from_attributes": True}