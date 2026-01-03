"""
Mindmap Image Generator - Generate PNG preview of mindmaps
Uses PIL (Pillow) for rendering
"""
from io import BytesIO
from typing import Dict, List, Tuple, Optional
import math

from PIL import Image, ImageDraw, ImageFont

from app.core.logging import get_logger
from app.services.mindmap.models import MindMapNode, MindMapTheme

logger = get_logger(__name__)


class ImageMindMapGenerator:
    """
    Generate PNG image preview of mindmaps

    Features:
    - Radial layout for balanced appearance
    - Color-coded branches
    - Automatic sizing based on content
    - Vietnamese font support
    """

    # Layout constants
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    PADDING = 100
    NODE_PADDING = 20
    LEVEL_SPACING = 180
    SIBLING_ANGLE_SPACING = 0.4  # radians

    # Font paths (try multiple options)
    FONT_PATHS = [
        "f:/MILO_CHATBOT/app/data/fonts/DejaVuSans.ttf",
        "f:/MILO_CHATBOT/app/data/fonts/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    def __init__(self):
        self.font_cache = {}

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with caching"""
        key = (size, bold)
        if key not in self.font_cache:
            font = None
            for path in self.FONT_PATHS:
                try:
                    font = ImageFont.truetype(path, size)
                    break
                except (IOError, OSError) as e:
                    logger.debug(f"Font not found at {path}: {e}")
                    continue

            if font is None:
                font = ImageFont.load_default()

            self.font_cache[key] = font

        return self.font_cache[key]

    async def generate(
        self,
        root_node: MindMapNode,
        title: str,
        theme: MindMapTheme
    ) -> BytesIO:
        """
        Generate PNG image from mindmap

        Args:
            root_node: Root node of the mindmap
            title: Title of the mindmap
            theme: Color theme

        Returns:
            BytesIO containing PNG image
        """
        logger.info(f"🖼️ Generating mindmap image: {title}")

        # Calculate layout
        positions = self._calculate_layout(root_node)

        # Calculate image size
        width, height = self._calculate_size(positions)

        # Create image
        bg_color = self._parse_color(theme.background)
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        # Draw connections first (behind nodes)
        self._draw_connections(draw, root_node, positions)

        # Draw nodes
        self._draw_nodes(draw, root_node, positions)

        # Add title
        self._draw_title(draw, title, width, theme)

        # Add watermark
        self._draw_watermark(draw, width, height)

        # Save to buffer
        buffer = BytesIO()
        image.save(buffer, format='PNG', quality=95)
        buffer.seek(0)

        logger.info(f"🖼️ Generated mindmap image: {width}x{height}")
        return buffer

    def _calculate_layout(self, root: MindMapNode) -> Dict[int, Tuple[float, float]]:
        """
        Calculate positions for all nodes using radial layout

        Returns:
            Dict mapping node id to (x, y) position
        """
        positions = {}

        # Root at center
        root_id = id(root)
        center_x = self.MIN_WIDTH // 2
        center_y = self.MIN_HEIGHT // 2
        positions[root_id] = (center_x, center_y)

        # Layout children recursively
        if root.children:
            self._layout_children(
                root.children,
                center_x, center_y,
                0, 2 * math.pi,  # Full circle for first level
                1,  # Level 1
                positions
            )

        return positions

    def _layout_children(
        self,
        children: List[MindMapNode],
        parent_x: float,
        parent_y: float,
        start_angle: float,
        end_angle: float,
        level: int,
        positions: Dict[int, Tuple[float, float]]
    ):
        """Recursively layout children in a radial pattern"""
        if not children:
            return

        n = len(children)
        angle_range = end_angle - start_angle
        angle_step = angle_range / max(n, 1)

        radius = self.LEVEL_SPACING * level

        for i, child in enumerate(children):
            # Calculate angle for this child
            angle = start_angle + angle_step * (i + 0.5)

            # Calculate position
            x = parent_x + radius * math.cos(angle)
            y = parent_y + radius * math.sin(angle)

            positions[id(child)] = (x, y)

            # Layout grandchildren
            if child.children:
                # Narrow the angle range for children
                child_angle_range = min(angle_step * 0.8, math.pi / 2)
                child_start = angle - child_angle_range / 2
                child_end = angle + child_angle_range / 2

                self._layout_children(
                    child.children,
                    x, y,
                    child_start, child_end,
                    level + 1,
                    positions
                )

    def _calculate_size(self, positions: Dict[int, Tuple[float, float]]) -> Tuple[int, int]:
        """Calculate required image size based on node positions"""
        if not positions:
            return self.MIN_WIDTH, self.MIN_HEIGHT

        xs = [p[0] for p in positions.values()]
        ys = [p[1] for p in positions.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = int(max_x - min_x + self.PADDING * 2)
        height = int(max_y - min_y + self.PADDING * 2)

        # Ensure minimum size
        width = max(width, self.MIN_WIDTH)
        height = max(height, self.MIN_HEIGHT)

        return width, height

    def _draw_connections(
        self,
        draw: ImageDraw.Draw,
        node: MindMapNode,
        positions: Dict[int, Tuple[float, float]]
    ):
        """Draw curved connections between nodes"""
        node_pos = positions.get(id(node))
        if not node_pos:
            return

        for child in node.children:
            child_pos = positions.get(id(child))
            if not child_pos:
                continue

            # Get branch color
            branch_color = child.colors.get('branch', '#666666')
            color = self._parse_color(branch_color)

            # Draw curved line (bezier-like)
            self._draw_curved_line(draw, node_pos, child_pos, color, width=2)

            # Recursively draw children connections
            self._draw_connections(draw, child, positions)

    def _draw_curved_line(
        self,
        draw: ImageDraw.Draw,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: Tuple[int, int, int],
        width: int = 2
    ):
        """Draw a curved line between two points"""
        x1, y1 = start
        x2, y2 = end

        # Calculate control points for bezier curve
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Simple curved effect
        dx = x2 - x1
        dy = y2 - y1

        # Draw as series of line segments (approximation)
        points = []
        for t in [i / 20 for i in range(21)]:
            # Quadratic bezier approximation
            px = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
            py = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
            points.append((px, py))

        # Draw the line
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=width)

    def _draw_nodes(
        self,
        draw: ImageDraw.Draw,
        node: MindMapNode,
        positions: Dict[int, Tuple[float, float]],
        level: int = 0
    ):
        """Draw node boxes with text"""
        pos = positions.get(id(node))
        if not pos:
            return

        x, y = pos

        # Get colors
        bg_color = self._parse_color(node.colors.get('background', '#ffffff'))
        text_color = self._parse_color(node.colors.get('name', '#000000'))
        border_color = self._parse_color(node.colors.get('branch', '#666666'))

        # Get font size
        font_size = node.font.get('size', 14)
        font_size = max(min(font_size, 24), 10)  # Clamp to reasonable range
        font = self._get_font(font_size)

        # Calculate text size
        text = node.name[:50]  # Limit text length
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Node box dimensions
        box_width = text_width + self.NODE_PADDING * 2
        box_height = text_height + self.NODE_PADDING

        # Draw rounded rectangle
        left = x - box_width / 2
        top = y - box_height / 2
        right = x + box_width / 2
        bottom = y + box_height / 2

        # Draw box
        radius = 8
        self._draw_rounded_rect(draw, left, top, right, bottom, radius, bg_color, border_color)

        # Draw text centered
        text_x = x - text_width / 2
        text_y = y - text_height / 2
        draw.text((text_x, text_y), text, fill=text_color, font=font)

        # Recursively draw children
        for child in node.children:
            self._draw_nodes(draw, child, positions, level + 1)

    def _draw_rounded_rect(
        self,
        draw: ImageDraw.Draw,
        x1: float, y1: float,
        x2: float, y2: float,
        radius: int,
        fill: Tuple[int, int, int],
        outline: Tuple[int, int, int]
    ):
        """Draw a rounded rectangle"""
        # Draw main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

        # Draw corners
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

        # Draw border
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=2)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=2)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=2)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=2)

        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=2)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=2)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=2)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=2)

    def _draw_title(
        self,
        draw: ImageDraw.Draw,
        title: str,
        width: int,
        theme: MindMapTheme
    ):
        """Draw title at top of image"""
        font = self._get_font(20, bold=True)
        text_color = self._parse_color('#333333')

        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]

        x = (width - text_width) / 2
        y = 20

        draw.text((x, y), title, fill=text_color, font=font)

    def _draw_watermark(self, draw: ImageDraw.Draw, width: int, height: int):
        """Draw MILO watermark"""
        font = self._get_font(12)
        text = "Generated by MILO"
        text_color = (180, 180, 180)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        x = width - text_width - 20
        y = height - 30

        draw.text((x, y), text, fill=text_color, font=font)

    def _parse_color(self, hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color to RGB tuple"""
        if not hex_color:
            return (255, 255, 255)

        hex_color = hex_color.lstrip('#')

        # Handle different formats
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)
        elif len(hex_color) == 8:
            hex_color = hex_color[:6]  # Remove alpha

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except (ValueError, IndexError) as e:
            logger.debug(f"Invalid hex color '{hex_color}': {e}")
            return (255, 255, 255)


# Global instance
image_generator = ImageMindMapGenerator()
