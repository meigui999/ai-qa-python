import os
import uuid
from datetime import datetime
from pathlib import Path

import pdfplumber
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Document
from app.core.rag import index_document, delete_document_index


ALLOWED_EXTENSIONS = {".pdf", ".txt"}


async def upload_document(db: Session, user_id: int, file: UploadFile) -> Document:
    if not file.filename:
        raise ValueError("文件名不能为空")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("仅支持PDF和TXT格式的文件")

    # 按日期建目录
    date_dir = datetime.utcnow().strftime("%Y/%m/%d")
    upload_path = Path(settings.UPLOAD_DIR) / date_dir
    upload_path.mkdir(parents=True, exist_ok=True)

    new_filename = f"{uuid.uuid4()}{suffix}"
    file_path = upload_path / new_filename

    # 保存文件
    content = await file.read()
    file_path.write_bytes(content)

    # 解析文档内容
    text_content = parse_document(str(file_path), suffix)

    # 存入数据库
    doc = Document(
        user_id=user_id,
        file_name=file.filename,
        file_path=str(file_path),
        content=text_content,
        create_time=datetime.utcnow(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 建立向量索引（RAG核心）
    if text_content:
        try:
            chunk_count = index_document(user_id, doc.id, text_content)
        except Exception:
            chunk_count = 0

    return doc


def list_documents(db: Session, user_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.create_time.desc())
        .all()
    )


def get_document(db: Session, doc_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == doc_id).first()


def delete_document(db: Session, doc_id: int, user_id: int):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise ValueError("文档不存在")
    if doc.user_id != user_id:
        raise ValueError("无权删除该文档")

    # 删除物理文件
    try:
        os.remove(doc.file_path)
    except OSError:
        pass

    # 删除向量索引
    delete_document_index(user_id, doc_id)

    db.delete(doc)
    db.commit()


def parse_document(file_path: str, suffix: str) -> str:
    try:
        if suffix == ".pdf":
            return parse_pdf(file_path)
        elif suffix == ".txt":
            return parse_txt(file_path)
        return ""
    except Exception:
        return ""


def parse_pdf(file_path: str) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
