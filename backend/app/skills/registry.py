"""
技能注册中心

管理所有已注册的 Skills，提供查询、启用/禁用等功能
"""
from typing import Dict, List, Optional
from .base import Skill, SkillMetadata
from datetime import datetime


class SkillRegistry:
    """技能注册中心"""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._metadata: Dict[str, SkillMetadata] = {}

    def register(self, skill: Skill) -> None:
        """
        注册一个技能

        Args:
            skill: Skill 实例
        """
        self._skills[skill.name] = skill
        self._metadata[skill.name] = SkillMetadata(
            name=skill.name,
            version=skill.version,
            tags=skill.tags,
            enabled=True,
            created_at=datetime.now()
        )
        print(f"✓ 已注册技能: {skill.name} (v{skill.version})")

    def unregister(self, skill_name: str) -> bool:
        """
        注销一个技能

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否成功
        """
        if skill_name in self._skills:
            del self._skills[skill_name]
            del self._metadata[skill_name]
            return True
        return False

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        获取指定技能

        Args:
            skill_name: 技能名称

        Returns:
            Skill 实例或 None
        """
        return self._skills.get(skill_name)

    def get_enabled_skills(self) -> List[Skill]:
        """
        获取所有已启用的技能

        Returns:
            List[Skill]: 技能列表
        """
        return [
            skill for name, skill in self._skills.items()
            if self._metadata[name].enabled
        ]

    def enable_skill(self, skill_name: str) -> bool:
        """启用技能"""
        if skill_name in self._metadata:
            self._metadata[skill_name].enabled = True
            return True
        return False

    def disable_skill(self, skill_name: str) -> bool:
        """禁用技能"""
        if skill_name in self._metadata:
            self._metadata[skill_name].enabled = False
            return True
        return False

    def list_all(self) -> List[Dict[str, any]]:
        """
        列出所有技能及其元数据

        Returns:
            List[dict]: 技能信息列表
        """
        return [
            {
                "name": meta.name,
                "version": meta.version,
                "tags": meta.tags,
                "enabled": meta.enabled,
                "description": self._skills[meta.name].description
            }
            for meta in self._metadata.values()
        ]

    def to_openai_tools(self) -> List[Dict[str, any]]:
        """
        将所有已启用的技能转换为 OpenAI function calling 格式

        Returns:
            List[dict]: OpenAI tools 定义
        """
        return [
            skill.to_openai_function()
            for skill in self.get_enabled_skills()
        ]

    def get_by_tags(self, tags: List[str]) -> List[Skill]:
        """
        根据标签筛选技能

        Args:
            tags: 标签列表

        Returns:
            List[Skill]: 匹配的技能
        """
        return [
            skill for name, skill in self._skills.items()
            if any(tag in skill.tags for tag in tags) and self._metadata[name].enabled
        ]
