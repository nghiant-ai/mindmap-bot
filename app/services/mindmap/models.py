"""
Mind Map Models - Pydantic schemas for mind map structure
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class MindMapTheme(BaseModel):
    """Color theme for mind map"""
    colors: List[str]
    background: str = "#ffffff"
    text: str = "#000000"


class MindMapNode(BaseModel):
    """Node in mind map tree"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    note: Optional[str] = None
    colors: Dict[str, str] = Field(default_factory=lambda: {
        "name": "#000000",
        "background": "#ffffff",
        "branch": "#1f77b4"
    })
    font: Dict[str, Any] = Field(default_factory=lambda: {
        "size": 14,
        "style": "normal",
        "weight": "normal"
    })
    children: List["MindMapNode"] = Field(default_factory=list)

    def add_child(self, child: "MindMapNode"):
        """Add child node to this node"""
        self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return {
            "id": self.id,
            "name": self.name,
            "note": self.note,
            "colors": self.colors,
            "font": self.font,
            "children": [child.to_dict() for child in self.children]
        }
