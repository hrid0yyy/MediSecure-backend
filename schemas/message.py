from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    recipient_id: int
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1, max_length=5000)
    is_emergency: bool = False
    parent_message_id: Optional[int] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    subject: Optional[str]
    content: str  # Decrypted content
    is_read: bool
    read_at: Optional[datetime]
    is_emergency: bool
    parent_message_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
    unread_count: int
    page: int
    page_size: int

    class Config:
        from_attributes = True
