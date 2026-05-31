"""RAG检索服务 — LangChain + ChromaDB + 通义千问Embedding（OpenAI兼容接口）"""

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings

# ChromaDB持久化客户端
_chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

# Embedding模型 — 通过DashScope的OpenAI兼容接口调用通义千问Embedding
_embeddings = OpenAIEmbeddings(
    model=settings.EMBEDDING_MODEL,
    openai_api_key=settings.LLM_API_KEY,
    openai_api_base=f"{settings.LLM_BASE_URL}",
)

# 文本切片器
_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
)


def _get_collection_name(user_id: int, document_id: int) -> str:
    return f"user_{user_id}_doc_{document_id}"


def index_document(user_id: int, document_id: int, content: str) -> int:
    """将文档内容切片后存入向量库，返回切片数量"""
    chunks = _text_splitter.split_text(content)
    if not chunks:
        return 0

    collection_name = _get_collection_name(user_id, document_id)

    # 删除旧的（如果存在）
    try:
        _chroma_client.delete_collection(collection_name)
    except Exception:
        pass

    # 存入ChromaDB
    Chroma.from_texts(
        texts=chunks,
        embedding=_embeddings,
        collection_name=collection_name,
        persist_directory=settings.CHROMA_DIR,
    )

    return len(chunks)


def search_document(user_id: int, document_id: int, query: str, top_k: int = 4) -> str:
    """从向量库中检索与query最相关的文档片段"""
    collection_name = _get_collection_name(user_id, document_id)

    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=_embeddings,
            persist_directory=settings.CHROMA_DIR,
        )
        docs = vectorstore.similarity_search(query, k=top_k)
        return "\n\n".join(doc.page_content for doc in docs)
    except Exception:
        return ""


def delete_document_index(user_id: int, document_id: int):
    """删除文档的向量索引"""
    collection_name = _get_collection_name(user_id, document_id)
    try:
        _chroma_client.delete_collection(collection_name)
    except Exception:
        pass
