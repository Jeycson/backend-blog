from datetime import datetime

from pydantic import BaseModel


class CreateCommentBody(BaseModel):
    pageSlug: str
    author: str
    content: str


class CommentDTO(BaseModel):
    id: int
    pageSlug: str
    author: str
    content: str
    createdAt: datetime

    model_config = {
        "from_attributes": True
    }


class CommentResponse(BaseModel):
    data: CommentDTO


class CommentsResponse(BaseModel):
    data: list[CommentDTO]