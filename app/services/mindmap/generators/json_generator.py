"""
JSON Mind Map Generator
Generic JSON format compatible with web-based mind map viewers
"""
import json
from datetime import datetime
from io import BytesIO

from app.core.logging import get_logger
from app.utils.date_utils import get_vietnam_time
from app.services.mindmap.models import MindMapNode, MindMapTheme

logger = get_logger(__name__)


class JSONMindMapGenerator:
    """Generate mind map in generic JSON format"""

    async def generate(
        self,
        root: MindMapNode,
        title: str,
        theme: MindMapTheme
    ) -> BytesIO:
        """
        Generate JSON mind map

        Args:
            root: Root node of the mind map
            title: Mind map title
            theme: Color theme

        Returns:
            BytesIO buffer with JSON content
        """
        # Build complete structure
        mindmap_data = {
            "meta": {
                "name": title,
                "author": "Mindmap Bot",
                "created": get_vietnam_time().isoformat(),
                "version": "1.0"
            },
            "theme": {
                "name": "custom",
                "colorScheme": theme.colors,
                "background": theme.background,
                "text": theme.text
            },
            "root": root.to_dict()
        }

        # Convert to JSON with pretty formatting
        json_str = json.dumps(mindmap_data, ensure_ascii=False, indent=2)

        # Create BytesIO buffer
        buffer = BytesIO(json_str.encode('utf-8'))
        buffer.seek(0)

        logger.info(f"✅ Generated JSON mind map ({len(json_str)} bytes)")
        return buffer
