#!/usr/bin/env python3
"""
Advanced Professional Video Tools Telegram Bot
Main entry point for the bot application
"""

import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait
from config import Config
from database.db_handler import db_handler
from plugins.commands import register_command_handlers
from plugins.callbacks import register_callback_handlers
from plugins.video_handlers import register_video_handlers
from plugins.merge_callbacks import register_merge_callbacks
from plugins.encoding_callbacks import register_encoding_callbacks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class VideoToolsBot:
    """Main bot class"""
    
    def __init__(self):
        """Initialize the bot"""
        self.app = None
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting Advanced Video Tools Bot...")
            
            # Initialize database
            logger.info("📊 Initializing database...")
            await db_handler.init_pool()
            
            # Create Pyrogram client
            logger.info("🔧 Creating Pyrogram client...")
            self.app = Client(
                name="video_tools_bot",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN,
                workers=10
            )
            
            # Register handlers
            logger.info("📝 Registering command handlers...")
            register_command_handlers(self.app)
            
            logger.info("📝 Registering callback handlers...")
            register_callback_handlers(self.app)
            
            logger.info("📝 Registering video handlers...")
            register_video_handlers(self.app)
            
            logger.info("📝 Registering merge callbacks...")
            register_merge_callbacks(self.app)
            
            logger.info("📝 Registering encoding callbacks...")
            register_encoding_callbacks(self.app)
            
            # Start the client
            logger.info("▶️ Starting Pyrogram client...")
            await self.app.start()
            
            # Get bot information
            me = await self.app.get_me()
            logger.info(f"✅ Bot started successfully!")
            logger.info(f"📱 Bot Username: @{me.username}")
            logger.info(f"🆔 Bot ID: {me.id}")
            logger.info(f"👤 Owner: @{Config.OWNER_USERNAME} (ID: {Config.OWNER_ID})")
            logger.info(f"🔐 Authorized Groups: {len(Config.AUTHORIZED_GROUPS)}")
            logger.info(f"👥 Admin Users: {len(Config.ADMIN_USERS)}")
            
            # Send startup notification to owner if log channel is configured
            if Config.LOG_CHANNEL:
                try:
                    await self.app.send_message(
                        Config.LOG_CHANNEL,
                        f"🤖 <b>Bot Started Successfully!</b>\n\n"
                        f"🆔 Bot: @{me.username}\n"
                        f"📊 Database: Connected\n"
                        f"🔐 Authorized Groups: {len(Config.AUTHORIZED_GROUPS)}\n"
                        f"⏰ Started at: {asyncio.get_event_loop().time()}"
                    )
                except Exception as e:
                    logger.warning(f"Could not send startup message to log channel: {e}")
            
            logger.info("🎬 Bot is now running and ready to accept commands!")
            logger.info("Press Ctrl+C to stop the bot")
            
            # Keep the bot running
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            logger.info("⚠️ Received keyboard interrupt signal")
        except FloodWait as e:
            logger.warning(f"FloodWait error: Sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}", exc_info=True)
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot gracefully"""
        try:
            logger.info("⏸️ Stopping bot...")
            
            if self.app and self.app.is_connected:
                await self.app.stop()
                logger.info("✅ Pyrogram client stopped")
            
            if db_handler.pool:
                await db_handler.close_pool()
                logger.info("✅ Database connection closed")
            
            logger.info("👋 Bot stopped successfully!")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)


async def main():
    """Main function"""
    bot = VideoToolsBot()
    await bot.start()


if __name__ == "__main__":
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
