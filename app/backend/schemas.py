"""Pydantic request/response schemas for NEXORA API."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# User Schemas
# ============================================================================


class UserRegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response."""

    id: UUID
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


# ============================================================================
# Document Schemas
# ============================================================================


class DocumentResponse(BaseModel):
    """Document response."""

    id: UUID
    filename: str
    file_type: str
    file_size: int
    indexed_at: Optional[datetime]
    summary: Optional[str]
    key_topics: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response."""

    documents: List[DocumentResponse]
    total: int


# ============================================================================
# Conversation Schemas
# ============================================================================


class MessageRequest(BaseModel):
    """Message in a conversation."""

    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ConversationResponse(BaseModel):
    """Conversation response."""

    id: UUID
    title: str
    mode: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Detailed conversation response with messages."""

    messages: List[MessageRequest]


# ============================================================================
# Error Schemas
# ============================================================================


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
    status_code: int
