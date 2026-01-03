"""
FreeMind XML Mind Map Generator
Compatible with EdrawMind, XMind, Freeplane
"""
from io import BytesIO
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from xml.dom import minidom

from app.core.logging import get_logger
from app.services.mindmap.models import MindMapNode, MindMapTheme

logger = get_logger(__name__)


class FreeMindGenerator:
    """Generate mind map in FreeMind XML format"""

    async def generate(
        self,
        root: MindMapNode,
        title: str,
        theme: MindMapTheme
    ) -> BytesIO:
        """
        Generate FreeMind XML mind map

        Args:
            root: Root node of the mind map
            title: Mind map title
            theme: Color theme

        Returns:
            BytesIO buffer with XML content
        """
        # Create root map element
        map_elem = Element("map", version="0.9.0")

        # Build node tree
        self._build_xml_node(map_elem, root, is_root=True)

        # Convert to pretty XML string
        xml_str = self._prettify_xml(map_elem)

        # Create BytesIO buffer
        buffer = BytesIO(xml_str.encode('utf-8'))
        buffer.seek(0)

        logger.info(f"✅ Generated FreeMind XML ({len(xml_str)} bytes)")
        return buffer

    def _build_xml_node(
        self,
        parent_elem: Element,
        node: MindMapNode,
        is_root: bool = False,
        position: str = "right"
    ):
        """Recursively build XML node structure"""
        # Create node element
        node_attribs = {
            "TEXT": node.name,
            "COLOR": node.colors.get("name", "#000000")
        }

        # Add background color if not white
        bg_color = node.colors.get("background", "#ffffff")
        if bg_color and bg_color.lower() != "#ffffff":
            node_attribs["BACKGROUND_COLOR"] = bg_color

        # Add position for non-root nodes
        if not is_root:
            node_attribs["POSITION"] = position
        else:
            # Root node: set layout style to proper mind map (not tree)
            node_attribs["STYLE"] = "bubble"  # or "fork" for traditional mind map layout

        node_elem = SubElement(parent_elem, "node", **node_attribs)

        # Add edge (branch line)
        edge_attribs = {
            "COLOR": node.colors.get("branch", "#1f77b4")
        }

        # Root has thicker edges
        if is_root:
            edge_attribs["WIDTH"] = "2"

        SubElement(node_elem, "edge", **edge_attribs)

        # Add font
        font_attribs = {
            "NAME": "Arial",
            "SIZE": str(node.font.get("size", 14))
        }

        if node.font.get("weight") == "bold":
            font_attribs["BOLD"] = "true"

        if node.font.get("style") == "italic":
            font_attribs["ITALIC"] = "true"

        SubElement(node_elem, "font", **font_attribs)

        # Add note if present
        if node.note:
            richcontent = SubElement(node_elem, "richcontent", TYPE="NOTE")
            html = SubElement(richcontent, "html")
            body = SubElement(html, "body")
            p = SubElement(body, "p")
            p.text = node.note

        # Recursively add children
        # All children extend in the same direction as parent (proper mind map layout)
        for idx, child in enumerate(node.children):
            if is_root:
                # Root children: alternate left/right for balanced layout
                child_position = "right" if idx % 2 == 0 else "left"
            else:
                # Non-root children: all extend in the same direction as parent
                # This creates proper branching instead of vertical tree
                child_position = position

            self._build_xml_node(node_elem, child, is_root=False, position=child_position)

    def _prettify_xml(self, elem: Element) -> str:
        """Convert XML element to pretty-printed string"""
        # Convert to string
        rough_string = tostring(elem, encoding='unicode')

        # Parse and prettify
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)
