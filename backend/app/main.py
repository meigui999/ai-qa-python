from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import auth, documents, chat

app = FastAPI(title="AI智能文档问答系统", version="1.0.0")

# CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 统一异常格式（前端用 error.response.data?.message 读取错误信息）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail},
        )
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"},
    )


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
