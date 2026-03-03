"""
Skill 抽象基类和相关数据模型
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SkillResult:
    """工具执行结果"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """转换为 JSON 字符串供 LLM 使用"""
        import json
        return json.dumps({
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }, ensure_ascii=False)


@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    version: str
    tags: List[str]
    enabled: bool
    author: Optional[str] = None
    created_at: Optional[datetime] = None


class Skill(ABC):
    """Skill 抽象基类

    所有工具都需要继承此类并实现 execute 方法
    """

    # 子类需要定义这些属性
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    tags: List[str] = []
    parameters: Dict[str, Any] = {}  # JSON Schema 格式

    def __init__(self):
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define 'name'")
        if not self.description:
            raise ValueError(f"{self.__class__.__name__} must define 'description'")

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """
        执行工具逻辑

        Args:
            **kwargs: 工具参数（根据 parameters schema 定义）

        Returns:
            SkillResult: 执行结果
        """
        pass

    def to_openai_function(self) -> Dict[str, Any]:
        """
        转换为 OpenAI function calling 格式

        Returns:
            dict: OpenAI function 定义
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def validate_parameters(self, **kwargs) -> bool:
        """
        验证参数是否符合 schema（简单实现）

        Args:
            **kwargs: 待验证的参数

        Returns:
            bool: 是否有效
        """
        required = self.parameters.get("required", [])
        for param in required:
            if param not in kwargs:
                return False
        return True
