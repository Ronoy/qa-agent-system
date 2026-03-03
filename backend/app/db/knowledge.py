import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class KnowledgeBaseORM(Base):
    __tablename__ = "knowledge_bases"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(Text, default="[]")  # JSON: [{"category": "行业", "value": "教育"}]
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("KnowledgeDocumentORM", back_populates="kb", cascade="all, delete-orphan")


class KnowledgeDocumentORM(Base):
    __tablename__ = "knowledge_documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kb_id = Column(String, ForeignKey("knowledge_bases.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf/image/excel
    file_path = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending/processing/done/error
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    kb = relationship("KnowledgeBaseORM", back_populates="documents")
    chunks = relationship("KnowledgeChunkORM", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunkORM(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(String, ForeignKey("knowledge_documents.id"), nullable=False)
    kb_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Text, nullable=True)  # JSON float array
    document = relationship("KnowledgeDocumentORM", back_populates="chunks")
