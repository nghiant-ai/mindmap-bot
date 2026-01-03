"""
OPML Mind Map Generator
Compatible with EdrawMind, XMind, OmniOutliner, and other outliner apps
OPML (Outline Processor Markup Language) is widely supported format
"""
from io import BytesIO
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from app.core.logging import get_logger
from app.utils.date_utils import get_vietnam_time
from app.services.mindmap.models import MindMapNode, MindMapTheme

logger = get_logger(__name__)


class OPMLGenerator:
    """
    Generate mind map in OPML format

    OPML is excellent for EdrawMind because:
    - Auto-formats properly on import
    - Preserves hierarchy structure
    - Supports notes/descriptions
    - Widely compatible with many apps
    """

    async def generate(
        self,
        root: MindMapNode,
        title: str,
        theme: MindMapTheme
    ) -> BytesIO:
        """
        Generate OPML mind map

        Args:
            root: Root node of the mind map
            title: Mind map title
            theme: Color theme (not used in OPML but kept for interface consistency)

        Returns:
            BytesIO buffer with OPML XML content
        """
        # Create OPML root element
        opml = Element("opml", version="2.0")

        # Create head section
        head = SubElement(opml, "head")
        title_elem = SubElement(head, "title")
        title_elem.text = title

        # Add metadata
        date_created = SubElement(head, "dateCreated")
        date_created.text = get_vietnam_time().strftime("%a, %d %b %Y %H:%M:%S +0700")

        owner = SubElement(head, "ownerName")
        owner.text = "MILO Chatbot"

        # Create body section
        body = SubElement(opml, "body")

        # Build outline structure recursively
        self._build_outline(body, root)

        # Convert to pretty XML string
        xml_str = self._prettify_xml(opml)

        # Create BytesIO buffer
        buffer = BytesIO(xml_str.encode('utf-8'))
        buffer.seek(0)

        logger.info(f"OPML generated: {title} ({len(xml_str)} bytes)")
        return buffer

    def _build_outline(self, parent_elem: Element, node: MindMapNode):
        """
        Recursively build OPML outline structure

        Args:
            parent_elem: Parent XML element
            node: Current MindMapNode
        """
        # Create outline element with text attribute
        outline_attribs = {
            "text": node.name
        }

        # Add note as _note attribute if present
        # EdrawMind reads this as node description
        if node.note:
            outline_attribs["_note"] = node.note

        outline = SubElement(parent_elem, "outline", **outline_attribs)

        # Recursively add children
        for child in node.children:
            self._build_outline(outline, child)

    def _prettify_xml(self, elem: Element) -> str:
        """Convert XML element to pretty-printed string with XML declaration"""
        # Convert to string
        rough_string = tostring(elem, encoding='unicode')

        # Parse and prettify
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding=None)

        # Remove extra blank lines but keep XML declaration
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)


# Global instance
opml_generator = OPMLGenerator()
