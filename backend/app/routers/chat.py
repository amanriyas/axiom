# app/routers/chat.py
"""Policy chatbot routes — conversational interface for policy questions."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import User
from app.schemas import (
    ChatConversationResponse,
    ChatMessageCreate,
    ChatMessageResponse,
)
from app.services.auth import get_current_user
from app.services.chat import (
    create_conversation,
    get_conversation,
    get_all_conversations,
    get_conversation_messages,
    delete_conversation,
    delete_all_conversations,
    answer_question,
    answer_question_stream,
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ConversationCreate(BaseModel):
    title: Optional[str] = None


@router.post("/conversations", response_model=ChatConversationResponse)
async def start_conversation(
    payload: ConversationCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new chat conversation."""
    title = (payload.title if payload and payload.title else "New Conversation")
    conversation = create_conversation(db, user_id=current_user.id, title=title)
    return conversation


@router.get("/conversations", response_model=list[ChatConversationResponse])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all conversations for the current user (including shared/seeded ones)."""
    return get_all_conversations(db, current_user.id)


@router.get("/conversations/{conversation_id}", response_model=ChatConversationResponse)
async def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a conversation with all messages."""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations")
async def clear_all_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all conversations for the current user."""
    count = delete_all_conversations(db, current_user.id)
    return {"message": f"Deleted {count} conversations", "deleted": count}


@router.delete("/conversations/{conversation_id}")
async def remove_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a single conversation."""
    success = delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all messages in a conversation."""
    return get_conversation_messages(db, conversation_id)


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    conversation_id: int,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message and get an AI response (non-streaming)."""
    try:
        response = await answer_question(
            db=db,
            conversation_id=conversation_id,
            question=payload.content,
            user_id=current_user.id,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/conversations/{conversation_id}/stream")
async def stream_message(
    conversation_id: int,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message and stream the AI response via SSE."""
    # Use a separate session for streaming
    stream_db = SessionLocal()

    async def event_generator():
        try:
            async for event in answer_question_stream(
                db=stream_db,
                conversation_id=conversation_id,
                question=payload.content,
                user_id=current_user.id,
            ):
                yield f"data: {event}\n\n"
        finally:
            stream_db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
