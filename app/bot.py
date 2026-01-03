"""Telegram Bot Handler"""
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.core.config import settings
from app.core.logging import get_logger
from app.gemini_client import gemini_client
from app.services.mindmap.mindmap_service import mindmap_service

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🗺️ **Chào mừng đến với Mindmap Bot!**

Bot chuyên tạo sơ đồ tư duy (mindmap) từ bất kỳ chủ đề nào bạn muốn.

**Cách sử dụng:**
Gửi tin nhắn: "Tạo mindmap về [chủ đề]"

**Ví dụ:**
- Tạo mindmap về lịch sử Việt Nam
- Tạo sơ đồ tư duy về lập trình Python
- Vẽ mindmap về marketing online

📄 **Format:** Excel (.xlsx), Markdown (.md), hoặc JSON

Hãy thử ngay! 🚀
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 **Hướng dẫn sử dụng Mindmap Bot**

**Câu lệnh:**
/start - Bắt đầu
/help - Xem hướng dẫn

**Tạo mindmap:**
Chỉ cần gửi tin nhắn yêu cầu tạo mindmap về chủ đề bạn muốn.

Bot sẽ tự động tổ chức kiến thức thành cấu trúc phân cấp và tạo file cho bạn!
AI sẽ tự động chọn format phù hợp (Excel dễ sửa nhất, Markdown cho EdrawMind).
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_message = update.message.text
    user_id = update.message.from_user.id

    logger.info(f"📨 Message from user {user_id}: {user_message}")

    # Send thinking message
    thinking_msg = await update.message.reply_text("🤔 Đang tạo mindmap...")

    try:
        # Generate mindmap using Gemini
        result = await gemini_client.generate_mindmap(user_message)

        if result["success"]:
            # Generate file
            buffer = await mindmap_service.generate_from_structure(
                structure=result["structure"],
                title=result["title"],
                format=result["format"]
            )

            # Determine file extension based on format
            format_extensions = {
                "markdown": ".md",
                "json": ".json",
                "excel": ".xlsx"
            }
            file_ext = format_extensions.get(result["format"], ".md")
            filename = f"{result['title']}{file_ext}"

            # Send file
            buffer.seek(0)
            await update.message.reply_document(
                document=buffer,
                filename=filename,
                caption=f"✅ Mind map **{result['title']}** đã được tạo thành công!\n\n📄 Format: {result['format'].upper()}",
                parse_mode="Markdown"
            )

            logger.info(f"✅ Mindmap sent to user {user_id}: {result['title']}")

        else:
            # Failed or text response
            if "text_response" in result:
                await update.message.reply_text(result["text_response"])
            else:
                error_msg = result.get("error", "Không thể tạo mindmap")
                await update.message.reply_text(f"❌ {error_msg}")

        # Delete thinking message
        await thinking_msg.delete()

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        await thinking_msg.delete()
        await update.message.reply_text(
            f"❌ Đã xảy ra lỗi: {str(e)}"
        )


def create_application() -> Application:
    """Create and configure bot application"""
    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Bot handlers registered")

    return application
