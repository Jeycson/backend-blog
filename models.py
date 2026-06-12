from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from database import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    pageSlug = Column(String(255), nullable=False, index=True)
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)