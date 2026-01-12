from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from config.database import get_db
from schemas.message import MessageCreate, MessageResponse, MessageListResponse
from services.messaging_service import MessagingService
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/messages", tags=["Messaging"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a secure message"""
    message = MessagingService.send_message(
        db=db,
        sender_id=current_user.id,
        message_data=message_data
    )
    # Decrypt for response
    from utils.encryption import decrypt_data
    message.content = decrypt_data(message.encrypted_content)
    return message


@router.get("/inbox", response_model=MessageListResponse)
def get_inbox(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inbox messages"""
    messages, total, unread_count = MessagingService.get_inbox(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    return MessageListResponse(
        messages=messages,
        total=total,
        unread_count=unread_count,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/sent")
def get_sent_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sent messages"""
    messages, total = MessagingService.get_sent_messages(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return {
        "messages": messages,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific message (marks as read if recipient)"""
    message = MessagingService.get_message_by_id(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    return message


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a message"""
    result = MessagingService.delete_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    return result


@router.post("/{message_id}/mark-read", response_model=MessageResponse)
def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read"""
    message = MessagingService.mark_as_read(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    # Decrypt for response
    from utils.encryption import decrypt_data
    message.content = decrypt_data(message.encrypted_content)
    return message
