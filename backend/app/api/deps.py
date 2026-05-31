"""JWT认证依赖 — 支持Header和Query两种token传递方式"""

from fastapi import Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_token


def get_current_user_id(request: Request) -> int:
    # 优先从Authorization header取
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    else:
        # SSE场景：EventSource无法设header，token通过query参数传递
        token = request.query_params.get("token", "")

    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    try:
        payload = decode_token(token)
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")
