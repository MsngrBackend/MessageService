from sqlalchemy import String, BigInteger, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class ChatMembers(Base):
    __tablename__ = "chat_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[int] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True)
