from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from database import Base

from models import CommentModel

from schemas import (
    CreateCommentBody,
    CommentDTO,
    CommentResponse,
    CommentsResponse
)

app = FastAPI(title="Blog Comments API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/comments", response_model=CommentsResponse)
def get_comments(
        slug: str,
        db: Session = Depends(get_db)
):
    comments = (
        db.query(CommentModel)
        .filter(CommentModel.pageSlug == slug)
        .order_by(CommentModel.createdAt.desc())
        .all()
    )

    return {"data": comments}


@app.post("/api/comments", response_model=CommentResponse)
def create_comment(
        body: CreateCommentBody,
        db: Session = Depends(get_db)
):
    try:

        new_comment = CommentModel(
            pageSlug=body.pageSlug,
            author=body.author,
            content=body.content
        )

        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        return {
            "data": CommentDTO.model_validate(new_comment)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al guardar comentario"
        )