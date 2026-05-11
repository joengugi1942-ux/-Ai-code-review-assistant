import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CodeReviewConversation, CodeReviewMessage
from app.schemas.review import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReviewConversationService:
    """Service for managing code review conversations and messages."""

    async def create_conversation(
        self, db: AsyncSession, payload: ConversationCreate
    ) -> ConversationResponse:
        now = _utcnow()
        conversation = CodeReviewConversation(
            title=payload.title,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return ConversationResponse.model_validate(conversation)

    async def get_conversation(
        self, db: AsyncSession, conversation_id: uuid.UUID
    ) -> ConversationResponse | None:
        stmt = select(CodeReviewConversation).where(
            CodeReviewConversation.id == str(conversation_id)
        )
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        if conversation is None:
            return None
        return ConversationResponse.model_validate(conversation)

    async def list_conversations(
        self, db: AsyncSession, active_only: bool = True
    ) -> list[ConversationResponse]:
        stmt = select(CodeReviewConversation)
        if active_only:
            stmt = stmt.where(CodeReviewConversation.is_active == True)
        stmt = stmt.order_by(CodeReviewConversation.created_at.desc())
        result = await db.execute(stmt)
        return [ConversationResponse.model_validate(c) for c in result.scalars().all()]

    async def delete_conversation(
        self, db: AsyncSession, conversation_id: uuid.UUID
    ) -> bool:
        stmt = (
            update(CodeReviewConversation)
            .where(CodeReviewConversation.id == str(conversation_id))
            .values(is_active=False, updated_at=_utcnow())
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    async def add_message(
        self, db: AsyncSession, conversation_id: uuid.UUID, payload: MessageCreate
    ) -> MessageResponse:
        message = CodeReviewMessage(
            conversation_id=str(conversation_id),
            role=payload.role,
            content=payload.content,
            created_at=_utcnow(),
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return MessageResponse.model_validate(message)

    async def get_messages(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MessageResponse]:
        stmt = (
            select(CodeReviewMessage)
            .where(CodeReviewMessage.conversation_id == str(conversation_id))
            .order_by(CodeReviewMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return [MessageResponse.model_validate(m) for m in result.scalars().all()]


review_conversation_service = ReviewConversationService()
