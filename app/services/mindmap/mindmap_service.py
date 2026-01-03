"""
Mind Map Service - Orchestrate mind map generation from notes
"""
from typing import Dict, Any
from io import BytesIO

from app.core.logging import get_logger
from app.services.mindmap.generators.json_generator import JSONMindMapGenerator
from app.services.mindmap.generators.markdown_generator import MarkdownGenerator
from app.services.mindmap.models import MindMapNode

logger = get_logger(__name__)


class MindMapService:
    """Service for generating mind maps from notes"""

    def __init__(self):
        self.json_generator = JSONMindMapGenerator()
        self.markdown_generator = MarkdownGenerator()

    async def generate_from_structure(
        self,
        structure: Dict[str, Any],
        title: str,
        format: str = "markdown"
    ) -> BytesIO:
        """
        Generate mind map from a structured data dictionary

        Args:
            structure: Mind map structure (from Gemini AI)
                      Format: {"name": "Root", "children": [...], "note": "..."}
            title: Mind map title
            format: Output format - "markdown" (default) or "json"

        Returns:
            BytesIO buffer containing the mind map file
        """
        logger.info(f"Generating {format} mind map: {title}")

        # Build simplified node tree (no theme needed)
        root_node = self._build_simple_node_tree(structure)

        # Generate output based on format
        if format == "markdown":
            return await self.markdown_generator.generate(root_node, title, None)
        else:  # json
            return await self.json_generator.generate(root_node, title, None)


    def _build_simple_node_tree(
        self,
        structure: Dict[str, Any]
    ) -> MindMapNode:
        """
        Recursively build simple node tree from structure (no styling)

        Args:
            structure: Dict with "name", "children", "note" keys

        Returns:
            MindMapNode
        """
        # Create simple node
        node = MindMapNode(
            name=structure.get("name", ""),
            note=structure.get("note")
        )

        # Recursively build children
        children_data = structure.get("children", [])
        for child_data in children_data:
            child_node = self._build_simple_node_tree(child_data)
            node.add_child(child_node)

        return node


# Global instance
mindmap_service = MindMapService()
