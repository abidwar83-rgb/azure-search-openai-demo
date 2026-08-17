"""Conversation service for NEXORA AI."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.conversation import Conversation
from models.message import ConversationMessage


class ConversationService:
    """Service for conversation-related operations."""

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        user_id: UUID,
        title: str = "",
        mode: str = "ASK",
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Conversation {mode}",
            mode=mode,
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation_by_id(session: AsyncSession, conv_id: UUID) -> Conversation | None:
        """Get conversation by ID."""
        return await session.get(Conversation, conv_id)

    @staticmethod
    async def list_user_conversations(session: AsyncSession, user_id: UUID) -> list[Conversation]:
        """List all conversations for a user."""
        result = await session.execute(
            select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def add_message(
        session: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str,
        sources: dict | None = None,
    ) -> ConversationMessage:
        """Add a message to a conversation."""
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources,
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def get_conversation_messages(session: AsyncSession, conversation_id: UUID) -> list[ConversationMessage]:
        """Get all messages in a conversation."""
        result = await session.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_conversation(session: AsyncSession, conv_id: UUID) -> bool:
        """Delete a conversation."""
        conversation = await session.get(Conversation, conv_id)
        if not conversation:
            return False
        await session.delete(conversation)
        await session.commit()
        return True
