# app/services/chat.py
"""Policy chatbot service — answers HR questions using RAG + LLM."""

import json
from datetime import datetime
from typing import Optional, AsyncGenerator

from sqlalchemy.orm import Session

from app.models import ChatConversation, ChatMessage
from app.services import llm, rag


CHAT_SYSTEM_PROMPT = """You are an AI HR Policy Assistant for the company. Your role is to answer employee questions about company policies, benefits, procedures, and guidelines.

Rules:
- Answer ONLY based on the provided policy context
- If the context doesn't contain enough information, say: "I'm not certain about this based on our current policies. Please contact HR directly for clarification."
- Be concise, friendly, and helpful
- Reference specific policy sections when possible
- Format responses with bullet points and headers for readability
- Never make up policies or benefits that aren't in the context
- If asked about something clearly outside HR policies (e.g., technical questions), politely redirect"""


def create_conversation(db: Session, user_id: Optional[int] = None, title: str = "New Conversation") -> ChatConversation:
    """Create a new chat conversation."""
    conversation = ChatConversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: int) -> Optional[ChatConversation]:
    """Get a conversation with its messages."""
    return db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()


def get_user_conversations(db: Session, user_id: int) -> list[ChatConversation]:
    """Get all conversations for a user."""
    return (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.last_message_at.desc())
        .all()
    )


def get_all_conversations(db: Session, user_id: int) -> list[ChatConversation]:
    """Get conversations for a user + any shared/seeded ones (user_id is None)."""
    from sqlalchemy import or_
    return (
        db.query(ChatConversation)
        .filter(or_(ChatConversation.user_id == user_id, ChatConversation.user_id.is_(None)))
        .order_by(ChatConversation.last_message_at.desc())
        .all()
    )


def get_conversation_messages(db: Session, conversation_id: int) -> list[ChatMessage]:
    """Get all messages in a conversation."""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def delete_conversation(db: Session, conversation_id: int) -> bool:
    """Delete a conversation and all its messages."""
    conversation = db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()
    if not conversation:
        return False
    db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).delete()
    db.delete(conversation)
    db.commit()
    return True


def delete_all_conversations(db: Session, user_id: int) -> int:
    """Delete all conversations for a user (including shared/seeded ones). Returns count deleted."""
    from sqlalchemy import or_
    convos = (
        db.query(ChatConversation)
        .filter(or_(ChatConversation.user_id == user_id, ChatConversation.user_id.is_(None)))
        .all()
    )
    count = len(convos)
    for conv in convos:
        db.query(ChatMessage).filter(ChatMessage.conversation_id == conv.id).delete()
        db.delete(conv)
    db.commit()
    return count


async def answer_question(
    db: Session,
    conversation_id: int,
    question: str,
    user_id: Optional[int] = None,
) -> ChatMessage:
    """Process a user question and generate an AI response using RAG."""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise ValueError("Conversation not found")

    # Save user message
    user_msg = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=question,
    )
    db.add(user_msg)
    db.commit()

    # Query RAG for relevant policy chunks (top 5)
    context_results = rag.query_policies(question, n_results=5)
    context = "\n\n---\n\n".join([r["text"] for r in context_results])
    sources_json = json.dumps([
        {"text": r["text"][:200], "source": r.get("source", "Policy Document")}
        for r in context_results
    ])

    # Build conversation history for context (last 6 messages)
    history = get_conversation_messages(db, conversation_id)
    history_text = ""
    for msg in history[-6:]:
        role_label = "User" if msg.role == "user" else "Assistant"
        history_text += f"{role_label}: {msg.content}\n\n"

    # Build prompt
    prompt = f"""Based on the following company policy documents, answer the user's question.

**Policy Context:**
{context if context else "No relevant policies found in the knowledge base."}

**Conversation History:**
{history_text}

**Current Question:**
{question}

Provide a helpful, accurate answer based on the policy context above."""

    # Generate response
    response_content = await llm.generate_text(
        prompt=prompt,
        system_prompt=CHAT_SYSTEM_PROMPT,
        context="",  # Context already in prompt
    )

    # Save assistant message
    assistant_msg = ChatMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=response_content,
        sources=sources_json,
    )
    db.add(assistant_msg)

    # Update conversation timestamp and title
    conversation.last_message_at = datetime.utcnow()
    if conversation.title == "New Conversation" and len(question) > 0:
        conversation.title = question[:80] + ("…" if len(question) > 80 else "")

    db.commit()
    db.refresh(assistant_msg)
    return assistant_msg


async def answer_question_stream(
    db: Session,
    conversation_id: int,
    question: str,
    user_id: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """Stream the AI response token by token via SSE."""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        yield json.dumps({"type": "error", "content": "Conversation not found"})
        return

    # Save user message
    user_msg = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=question,
    )
    db.add(user_msg)
    db.commit()

    # Query RAG
    context_results = rag.query_policies(question, n_results=5)
    context = "\n\n---\n\n".join([r["text"] for r in context_results])
    sources_json = json.dumps([
        {"text": r["text"][:200], "source": r.get("source", "Policy Document")}
        for r in context_results
    ])

    # Emit sources first
    yield json.dumps({"type": "sources", "content": sources_json})

    # Build conversation history
    history = get_conversation_messages(db, conversation_id)
    history_text = ""
    for msg in history[-6:]:
        role_label = "User" if msg.role == "user" else "Assistant"
        history_text += f"{role_label}: {msg.content}\n\n"

    prompt = f"""Based on the following company policy documents, answer the user's question.

**Policy Context:**
{context if context else "No relevant policies found in the knowledge base."}

**Conversation History:**
{history_text}

**Current Question:**
{question}

Provide a helpful, accurate answer based on the policy context above."""

    # Stream LLM response
    full_response = ""
    async for chunk in llm.generate_text_stream(
        prompt=prompt,
        system_prompt=CHAT_SYSTEM_PROMPT,
        context="",
    ):
        full_response += chunk
        yield json.dumps({"type": "token", "content": chunk})

    # Save complete response
    assistant_msg = ChatMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=full_response,
        sources=sources_json,
    )
    db.add(assistant_msg)
    conversation.last_message_at = datetime.utcnow()
    if conversation.title == "New Conversation" and len(question) > 0:
        conversation.title = question[:80] + ("…" if len(question) > 80 else "")
    db.commit()

    yield json.dumps({"type": "done", "content": ""})
