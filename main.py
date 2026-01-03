"""Main entry point for Mindmap Bot"""
import asyncio
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.bot import create_application

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("🗺️  Mindmap Bot - Starting...")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Model: {settings.gemini_model}")

    # Create application
    app = create_application()

    # Start polling
    logger.info("🚀 Starting bot in polling mode...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    logger.info("=" * 60)
    logger.info("✅ Bot is running!")
    logger.info("💡 Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping bot...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        logger.info("👋 Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
