"""
Skills 管理 API

提供技能列表、启用/禁用等管理功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agent.agent import skill_registry

router = APIRouter()


class SkillInfo(BaseModel):
    """技能信息"""
    name: str
    description: str
    version: str
    tags: List[str]
    enabled: bool


class SkillToggleRequest(BaseModel):
    """技能启用/禁用请求"""
    skill_name: str
    enabled: bool


@router.get("/list", response_model=List[SkillInfo])
async def list_skills():
    """
    获取所有技能列表
    """
    skills_data = skill_registry.list_all()
    return [
        SkillInfo(
            name=s["name"],
            description=s["description"],
            version=s["version"],
            tags=s["tags"],
            enabled=s["enabled"]
        )
        for s in skills_data
    ]


@router.post("/toggle")
async def toggle_skill(req: SkillToggleRequest):
    """
    启用或禁用技能
    """
    if req.enabled:
        success = skill_registry.enable_skill(req.skill_name)
    else:
        success = skill_registry.disable_skill(req.skill_name)

    if not success:
        raise HTTPException(status_code=404, detail=f"技能不存在: {req.skill_name}")

    return {
        "success": True,
        "message": f"技能 {req.skill_name} 已{'启用' if req.enabled else '禁用'}"
    }


@router.get("/tags")
async def get_skill_tags():
    """
    获取所有技能标签
    """
    skills = skill_registry.list_all()
    tags = set()
    for skill in skills:
        tags.update(skill["tags"])
    return {"tags": sorted(list(tags))}


@router.get("/by-tag/{tag}")
async def get_skills_by_tag(tag: str):
    """
    根据标签筛选技能
    """
    skills = skill_registry.get_by_tags([tag])
    return {
        "tag": tag,
        "count": len(skills),
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "version": s.version
            }
            for s in skills
        ]
    }
