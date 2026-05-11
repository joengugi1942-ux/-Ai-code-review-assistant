"""
Conversation API endpoints for code review.

Provides REST endpoints for:
- POST /: Create a new conversation
- GET /{conversation_id}: Get conversation details
- DELETE /{conversation_id}: Delete (soft) a conversation
- POST /{conversation_id}/messages: Add a message to a conversation
- GET /{conversation_id}/messages: List messages for a conversation
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_api_key
from app.db.database import get_db
from app.schemas.review import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.review_conversation_service import review_conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    _: str = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """
    Create a new code review conversation.

    Optionally accepts a title for the conversation.
    """
    return await review_conversation_service.create_conversation(db, payload)


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    active_only: bool = True,
    _: str = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> List[ConversationResponse]:
    """
    List all code review conversations.

    By default returns only active conversations. Set active_only=false to get all.
    """
    return await review_conversation_service.list_conversations(db, active_only=active_only)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    _: str = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """Get conversation details by ID."""
    conversation = await review_conversation_service.get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    _: str = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Soft-delete a conversation by marking it as inactive.

    Messages are preserved for potential future reactivation.
    """
    success = await review_conversation_service.delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    conversation_id: UUID,
    payload: MessageCreate,
    _: str = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Add a message to a conversation.

    Accepts a role ("user" or "assistant") and content.
    """
    # Verify conversation exists
    conversation = await review_conversation_service.get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return await review_conversation_service.add_message(db, conversation_id, payload)


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    conversation_id: UUID,
    limit: int = 100,
    offset: int = 0,
    _: str = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
) -> List[MessageResponse]:
    """
    List messages for a conversation.

    Supports pagination via limit and offset parameters.
    """
    # Verify conversation exists
    conversation = await review_conversation_service.get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return await review_conversation_service.get_messages(
        db, conversation_id, limit=limit, offset=offset
    )