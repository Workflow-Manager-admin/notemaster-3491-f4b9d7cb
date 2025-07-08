from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models
from .db import get_db, create_tables, User, Note
from .auth import (
    get_current_user, 
    get_password_hash, 
    verify_password, 
    create_access_token
)

app = FastAPI(
    title="Notes Backend API",
    description="Handles notes, authentication, and user operations for the Notes app.",
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "User authentication"},
        {"name": "users", "description": "User management"},
        {"name": "notes", "description": "Notes management"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Create database tables at app startup."""
    create_tables()

@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Returns API health and readiness."""
    return {"message": "Healthy"}

# ----------------- AUTH ROUTES ------------------------

@app.post("/auth/signup", response_model=models.UserRead, tags=["auth"], summary="Register a new user")
def signup(payload: models.UserSignup, db: Session = Depends(get_db)):
    """
    Register as a new user if username does not already exist.
    """
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken.")
    hashed_pw = get_password_hash(payload.password)
    user = User(username=payload.username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return models.UserRead(id=user.id, username=user.username)

@app.post("/auth/login", response_model=models.Token, tags=["auth"], summary="Authenticate a user and get JWT token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT bearer token. Token is valid for 1 day.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token(data={"sub": user.username})
    return models.Token(access_token=token, token_type="bearer")

# (Add logout as "frontend only" since JWT is stateless; no backend change necessary.)

# ----------------- NOTES ROUTES ------------------------

@app.get("/notes", response_model=List[models.NoteRead], tags=["notes"], summary="Get all notes for the user")
def list_notes(
    query: Optional[str] = Query(None, description="Search notes by title/content"),
    skip: int = 0,
    limit: int = 20,
    current_user: models.UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all notes for the authenticated user, optionally filtered by query in title or content.
    """
    q = db.query(Note).filter(Note.user_id == current_user.id)
    if query:
        like_expr = f"%{query}%"
        q = q.filter((Note.title.ilike(like_expr)) | (Note.content.ilike(like_expr)))
    notes = q.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    return [
        models.NoteRead(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            content=n.content,
            created_at=n.created_at,
            updated_at=n.updated_at
        )
        for n in notes
    ]

@app.post("/notes", response_model=models.NoteRead, tags=["notes"], summary="Create a new note")
def create_note(
    payload: models.NoteCreate,
    current_user: models.UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a note for the authenticated user.
    """
    note = Note(
        user_id=current_user.id,
        title=payload.title,
        content=payload.content
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return models.NoteRead(
        id=note.id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.get("/notes/{note_id}", response_model=models.NoteRead, tags=["notes"], summary="Get a single note by ID")
def get_note(
    note_id: int,
    current_user: models.UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single note by ID for the current user.
    """
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return models.NoteRead(
        id=note.id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.put("/notes/{note_id}", response_model=models.NoteRead, tags=["notes"], summary="Update a note")
def update_note(
    note_id: int,
    payload: models.NoteUpdate,
    current_user: models.UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit a note (title/content) for the authenticated user.
    """
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.commit()
    db.refresh(note)
    return models.NoteRead(
        id=note.id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.delete("/notes/{note_id}", status_code=204, tags=["notes"], summary="Delete a note")
def delete_note(
    note_id: int,
    current_user: models.UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a note by ID for the current user.
    """
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    db.delete(note)
    db.commit()
    return None


