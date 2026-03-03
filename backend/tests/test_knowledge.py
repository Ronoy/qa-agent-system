"""知识库接口测试"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE = "/api/knowledge"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def kb(client):
    """创建一个测试知识库，用后删除"""
    r = await client.post(f"{BASE}/bases", json={"name": "测试库", "description": "test", "tags": []})
    data = r.json()
    yield data
    await client.delete(f"{BASE}/bases/{data['id']}")


# ── tag-categories ────────────────────────────────────────

@pytest.mark.asyncio
async def test_tag_categories(client):
    r = await client.get(f"{BASE}/tag-categories")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert "行业" in body


# ── 知识库 CRUD ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_list_base(client):
    r = await client.post(f"{BASE}/bases", json={
        "name": "单元测试库", "description": "desc",
        "tags": [{"category": "行业", "value": "教育"}]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "单元测试库"
    assert data["tags"][0]["value"] == "教育"

    kb_id = data["id"]
    r2 = await client.get(f"{BASE}/bases")
    assert r2.status_code == 200
    ids = [b["id"] for b in r2.json()]
    assert kb_id in ids

    await client.delete(f"{BASE}/bases/{kb_id}")


@pytest.mark.asyncio
async def test_update_base(client, kb):
    r = await client.put(f"{BASE}/bases/{kb['id']}", json={
        "name": "改名后", "description": "new", "tags": []
    })
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_update_base_not_found(client):
    r = await client.put(f"{BASE}/bases/nonexistent", json={
        "name": "x", "description": "", "tags": []
    })
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_base_not_found(client):
    r = await client.delete(f"{BASE}/bases/nonexistent")
    assert r.status_code == 404


# ── 文档管理 ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_documents_empty(client, kb):
    r = await client.get(f"{BASE}/bases/{kb['id']}/documents")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_upload_unsupported_type(client, kb):
    r = await client.post(
        f"{BASE}/bases/{kb['id']}/upload",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_to_nonexistent_kb(client):
    r = await client.post(
        f"{BASE}/bases/nonexistent/upload",
        files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")}
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_not_found(client, kb):
    r = await client.delete(f"{BASE}/bases/{kb['id']}/documents/nonexistent")
    assert r.status_code == 404


# ── chunks / preview ─────────────────────────────────────

@pytest.mark.asyncio
async def test_chunks_not_found(client):
    r = await client.get(f"{BASE}/documents/nonexistent/chunks")
    # 文档不存在时返回空列表（无 404）
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_preview_not_found(client):
    r = await client.get(f"{BASE}/documents/nonexistent/preview")
    assert r.status_code == 404


# ── 语义搜索 ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_empty_kb(client, kb):
    r = await client.post(f"{BASE}/bases/{kb['id']}/search", json={"query": "测试", "top_k": 3})
    assert r.status_code == 200
    assert r.json() == []
