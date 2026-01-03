"""Simplified Gemini AI Client for Mindmap Generation"""
import json
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Function declaration for mindmap generation
MINDMAP_FUNCTION = types.FunctionDeclaration(
    name="generate_mindmap",
    description="""
    **BẮT BUỘC gọi function này khi user yêu cầu tạo sơ đồ tư duy/mindmap.**

    Triggers (PHẢI gọi function):
    - "Tạo sơ đồ tư duy về X"
    - "Tạo mindmap về X"
    - "Vẽ sơ đồ tư duy X"
    - "Generate mindmap about X"

    Tạo sơ đồ tư duy (mind map) từ bất kỳ chủ đề nào user cung cấp.
    Tự tổ chức kiến thức thành cấu trúc phân cấp hợp lý.

    Cấu trúc PHẢI là JSON string: {"name": "Root", "children": [...], "note": "..."}

    Ví dụ:
    {
      "name": "Python Programming",
      "children": [
        {
          "name": "Basics",
          "children": [
            {"name": "Variables", "note": "Store data values"},
            {"name": "Data Types", "note": "int, str, list, dict"}
          ]
        }
      ]
    }
    """,
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "title": types.Schema(
                type=types.Type.STRING,
                description="Tiêu đề của mind map"
            ),
            "structure": types.Schema(
                type=types.Type.STRING,
                description="""
                Cấu trúc mind map dạng JSON string.
                Mỗi node có: name (bắt buộc), note (tùy chọn), children (tùy chọn là mảng các node con).
                """
            ),
            "format": types.Schema(
                type=types.Type.STRING,
                description="""Định dạng xuất:
                - 'markdown' (MẶC ĐỊNH): Markdown outline (.md) - dễ đọc, tương thích EdrawMind, Obsidian
                - 'json': JSON format - cho web viewers
                """,
                enum=["markdown", "json"]
            )
        },
        required=["title", "structure"]
    )
)


class GeminiClient:
    """Simplified Gemini client for mindmap generation"""

    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        logger.info(f"✅ Gemini Client initialized with model: {self.model_name}")

    async def generate_mindmap(self, user_message: str) -> dict:
        """
        Generate mindmap from user message

        Returns:
            dict with:
                - success: bool
                - title: str
                - structure: dict
                - format: str
                - text_response: str (optional)
                - error: str (optional)
        """
        try:
            # Call Gemini with function declaration
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(function_declarations=[MINDMAP_FUNCTION])],
                    temperature=0.7,
                    response_modalities=["TEXT"]
                )
            )

            # Check if function was called
            if response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]

                # Check for function call
                if part.function_call:
                    func_call = part.function_call
                    if func_call.name == "generate_mindmap":
                        args = func_call.args

                        # Parse structure JSON
                        structure_str = args.get("structure", "{}")
                        try:
                            structure = json.loads(structure_str)
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON structure: {e}")
                            return {
                                "success": False,
                                "error": f"Cấu trúc JSON không hợp lệ: {str(e)}"
                            }

                        return {
                            "success": True,
                            "title": args.get("title", "Mindmap"),
                            "structure": structure,
                            "format": args.get("format", "markdown")
                        }

                # Text response only (no function call)
                if part.text:
                    return {
                        "success": False,
                        "text_response": part.text
                    }

            # No response
            return {
                "success": False,
                "error": "Không nhận được phản hồi từ AI"
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Lỗi kết nối AI: {str(e)}"
            }


# Global client instance
gemini_client = GeminiClient()
