from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# PUBLIC_INTERFACE
class UserSignup(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=128, description="Unique username")
    password: str = Field(..., min_length=6, max_length=128, description="User password")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Request model for user login."""
    username: str = Field(..., min_length=3, max_length=128, description="Unique username")
    password: str = Field(..., min_length=6, max_length=128, description="User password")

# PUBLIC_INTERFACE
class UserRead(BaseModel):
    """Response model for user info."""
    id: int
    username: str

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"

# PUBLIC_INTERFACE
class NoteCreate(BaseModel):
    """Request model for creating a note."""
    title: str = Field(..., max_length=256, description="Title of the note")
    content: str = Field(..., description="Content of the note")

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Request model for updating a note."""
    title: Optional[str] = Field(None, max_length=256)
    content: Optional[str]

# PUBLIC_INTERFACE
class NoteRead(BaseModel):
    """Response model for note."""
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

# PUBLIC_INTERFACE
class NoteSearchQuery(BaseModel):
    """Query model for searching/filtering notes."""
    query: Optional[str] = Field(None, description="Search term for note title or content")
    skip: int = 0
    limit: int = 20
