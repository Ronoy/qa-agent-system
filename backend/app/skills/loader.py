"""
技能动态加载器

从指定目录扫描并加载 Skill 类
"""
import importlib
import inspect
from pathlib import Path
from typing import Type
from .base import Skill
from .registry import SkillRegistry


class SkillLoader:
    """技能加载器"""

    @staticmethod
    async def load_from_directory(directory_path: str, registry: SkillRegistry) -> int:
        """
        从目录加载所有 Skills

        Args:
            directory_path: Skills 目录路径（相对于 app/）
            registry: 技能注册中心

        Returns:
            int: 加载的技能数量
        """
        count = 0
        base_path = Path(__file__).parent.parent  # app/
        skills_dir = base_path / directory_path.replace("app/", "")

        if not skills_dir.exists():
            print(f"⚠ Skills 目录不存在: {skills_dir}")
            return 0

        # 扫描所有 .py 文件
        for file_path in skills_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # 跳过 __init__.py 等

            try:
                # 构建模块路径
                module_name = f"{directory_path.replace('/', '.')}.{file_path.stem}"
                module = importlib.import_module(module_name)

                # 查找 Skill 子类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, Skill) and
                        obj is not Skill):
                        # 实例化并注册
                        skill_instance = obj()
                        registry.register(skill_instance)
                        count += 1

            except Exception as e:
                print(f"✗ 加载技能失败 {file_path.name}: {e}")

        return count

    @staticmethod
    def load_skill_class(skill_class: Type[Skill], registry: SkillRegistry) -> bool:
        """
        直接加载一个 Skill 类

        Args:
            skill_class: Skill 类
            registry: 技能注册中心

        Returns:
            bool: 是否成功
        """
        try:
            skill_instance = skill_class()
            registry.register(skill_instance)
            return True
        except Exception as e:
            print(f"✗ 加载技能失败 {skill_class.__name__}: {e}")
            return False
