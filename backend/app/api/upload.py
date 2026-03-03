"""
文件上传 API - 支持图片和 PDF
"""
import uuid
import base64
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.db.database import AsyncSessionLocal, AttachmentORM

router = APIRouter()
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {
    "image/jpeg": "image", "image/png": "image", "image/gif": "image", "image/webp": "image",
    "application/pdf": "pdf",
}


def _extract_pdf_text(file_path: Path) -> str:
    """提取 PDF 文本"""
    try:
        import fitz  # pymupdf
        doc = fitz.open(str(file_path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text[:8000]  # 限制长度
    except Exception as e:
        return f"PDF 解析失败: {e}"


def _image_to_base64(file_path: Path) -> str:
    """图片转 base64"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件，返回 attachment_id 和提取的文本"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

    # 保存文件
    attachment_id = str(uuid.uuid4())
    suffix = Path(file.filename).suffix
    file_path = UPLOAD_DIR / f"{attachment_id}{suffix}"
    content = await file.read()
    file_path.write_bytes(content)

    # 提取文本
    file_type = ALLOWED_TYPES[file.content_type]
    extracted_text = None
    if file_type == "pdf":
        extracted_text = _extract_pdf_text(file_path)
    elif file_type == "image":
        # 图片存 base64，供 LLM 视觉理解
        extracted_text = f"[IMAGE_BASE64:{_image_to_base64(file_path)}]"

    # 存入数据库
    async with AsyncSessionLocal() as db:
        att = AttachmentORM(
            id=attachment_id,
            file_name=file.filename,
            file_type=file_type,
            file_path=str(file_path),
            extracted_text=extracted_text,
        )
        db.add(att)
        await db.commit()

    return {
        "attachment_id": attachment_id,
        "file_name": file.filename,
        "file_type": file_type,
    }
