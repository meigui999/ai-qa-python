"""文档接口：上传 / 列表 / 删除"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user_id
from app.services import document as doc_service

router = APIRouter(prefix="/api/documents", tags=["文档"])


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        doc = await doc_service.upload_document(db, user_id, file)
        return {
            "code": 200,
            "message": "上传成功",
            "data": {
                "id": doc.id,
                "fileName": doc.file_name,
                "createTime": str(doc.create_time),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
def list_docs(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    docs = doc_service.list_documents(db, user_id)
    return {
        "code": 200,
        "data": [
            {
                "id": d.id,
                "fileName": d.file_name,
                "createTime": str(d.create_time),
            }
            for d in docs
        ],
    }


@router.delete("/{doc_id}")
def delete(
    doc_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        doc_service.delete_document(db, doc_id, user_id)
        return {"code": 200, "message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
