import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Configuración de Base de Datos (SQLite)
# En Render usaremos una ruta dentro del volumen persistente, localmente se creará en la raíz.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./comments.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modelo de la Tabla
class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    pageSlug = Column(String(255), index=True, nullable=False)
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

# Crear la tabla si no existe
Base.metadata.create_all(bind=engine)

# 3. Esquemas de Pydantic (Validación de Datos)
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

    class Config:
        from_attributes = True

# 4. Inicializar FastAPI
app = FastAPI(title="Blog Comments API")

# IMPORTANTE: Configura CORS para que tu Frontend pueda comunicarse con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambia esto por la URL de tu frontend en Vercel/Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Endpoints de la API

@app.get("/api/comments", response_model=dict)
def get_comments(slug: str, db: Session = Depends(get_db)):
    # Tu hook busca los comentarios filtrados por el query param 'slug'
    comments = db.query(CommentModel).filter(CommentModel.pageSlug == slug).order_by(CommentModel.createdAt.desc()).all()
    return {"data": comments}

@app.post("/api/comments", response_model=dict)
def create_comment(body: CreateCommentBody, db: Session = Depends(get_db)):
    try:
        new_comment = CommentModel(
            pageSlug=body.pageSlug,
            author=body.author,
            content=body.content
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        # Retorna el formato {"data": {id, author, ...}} que tu frontend añade optimistamente
        return {"data": CommentDTO.from_attrib(new_comment)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "Error al guardar el comentario"})