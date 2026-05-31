"""对话接口：普通问答 / SSE流式问答 / 对话历史"""

import json

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user_id
from app.models.models import Document, ChatHistory
from app.core.rag import search_document
from app.services.llm import chat_stream, chat_sync

router = APIRouter(prefix="/api/chat", tags=["对话"])


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(
    documentId: int = Query(None),
    question: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    answer = chat_sync("请回答以下问题：" + question)

    history = ChatHistory(user_id=user_id, question=question, answer=answer)
    db.add(history)
    db.commit()

    return {"code": 200, "data": {"question": question, "answer": answer}}


@router.get("/stream")
def stream(
    documentId: int = Query(...),
    question: str = Query(...),
    history: str = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # 查询文档
    doc = db.query(Document).filter(Document.id == documentId).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # RAG检索：从向量库中找最相关的片段
    relevant_content = search_document(user_id, documentId, question, top_k=4)

    # 如果向量库没检索到，回退到截断全文
    if not relevant_content and doc.content:
        relevant_content = doc.content[:4000]

    # 解析对话历史
    history_list = []
    if history:
        try:
            history_list = json.loads(history)
        except Exception:
            pass

    # 构建prompt
    prompt_parts = [
        f"你是一个智能文档助手。请基于以下文档内容回答用户问题。\n",
        f"【当前文档】{doc.file_name}",
        relevant_content,
    ]

    if history_list:
        prompt_parts.append("\n【对话历史】")
        for msg in history_list[-6:]:
            prompt_parts.append(f"用户: {msg.get('user', '')}")
            prompt_parts.append(f"助手: {msg.get('ai', '')}")

    prompt_parts.append(f"\n【当前问题】\n{question}")
    prompt_parts.append("\n请基于文档内容准确回答。如果文档中没有相关信息，请如实告知。")

    full_prompt = "\n".join(prompt_parts)

    def event_generator():
        full_answer = []
        for chunk in chat_stream(full_prompt, history_list):
            full_answer.append(chunk)
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

        # 保存对话历史
        try:
            answer_text = "".join(full_answer)
            h = ChatHistory(
                user_id=user_id,
                document_id=documentId,
                question=question,
                answer=answer_text,
            )
            db.add(h)
            db.commit()
        except Exception:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
def history(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.create_time.desc())
        .limit(50)
        .all()
    )
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "documentId": r.document_id,
                "question": r.question,
                "answer": r.answer,
                "createTime": str(r.create_time),
            }
            for r in records
        ],
    }


@router.delete("/history/{history_id}")
def delete_history(
    history_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    record = db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(record)
    db.commit()
    return {"code": 200, "msg": "删除成功"}
