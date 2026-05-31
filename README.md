# AI智能文档问答系统

基于 **FastAPI + LangChain + ChromaDB + 通义千问** 的 RAG 智能问答系统。

## 技术栈

- **后端**：Python 3.11 / FastAPI / SQLAlchemy
- **RAG**：LangChain + ChromaDB（向量检索）+ 通义千问 Embedding
- **大模型**：通义千问（DashScope OpenAI兼容接口）/ SSE流式输出
- **前端**：Vue 3 + Vite + Element Plus
- **部署**：Docker Compose（MySQL + FastAPI + Nginx）

## 功能

- 用户注册/登录（JWT认证）
- 文档上传（PDF/TXT）与管理
- 基于 RAG 的智能文档问答（向量检索 + 大模型生成）
- SSE 流式输出
- 对话历史管理

## Docker部署

```bash
docker-compose up -d --build
```

- 前端：http://localhost:82
- 后端API：http://localhost:8000
- 测试账号：test / 123456

## 本地开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
