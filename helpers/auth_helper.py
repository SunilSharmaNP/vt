from config import Config
from database.db_handler import db_handler


class AuthHelper:
    """
    Authentication and Authorization Helper
    Handles user authorization, group access control, and admin privileges
    """
    
    @staticmethod
    def is_owner(user_id: int) -> bool:
        """Check if user is the owner"""
        return user_id == Config.OWNER_ID
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Check if user is an admin/sudo user"""
        return user_id in Config.ADMIN_USERS or AuthHelper.is_owner(user_id)
    
    @staticmethod
    def is_authorized_group(chat_id: int) -> bool:
        """Check if chat is an authorized group"""
        return chat_id in Config.AUTHORIZED_GROUPS
    
    @staticmethod
    async def is_user_active(user_id: int, chat_id: int) -> bool:
        """Check if user is active in the chat"""
        return await db_handler.is_user_active(user_id, chat_id)
    
    @staticmethod
    async def can_use_bot(user_id: int, chat_id: int, is_private_chat: bool) -> tuple[bool, str]:
        """
        Check if user can use the bot based on authorization rules
        Returns: (can_use, reason_message)
        """
        # Owner and admins can use bot everywhere
        if AuthHelper.is_admin(user_id):
            return True, ""
        
        # In private chats, only admins can perform tasks
        if is_private_chat:
            return False, (
                "⚠️ <b>Private Chat Not Authorized</b>\n\n"
                "This bot only works in authorized groups for regular users.\n"
                "You can view menus and settings here, but cannot start tasks.\n\n"
                f"👤 Contact bot owner: @{Config.OWNER_USERNAME}\n"
                f"🆔 Owner ID: <code>{Config.OWNER_ID}</code>"
            )
        
        # In groups, check if it's authorized
        if not AuthHelper.is_authorized_group(chat_id):
            return False, (
                "⚠️ <b>Unauthorized Group</b>\n\n"
                "This group is not authorized to use this bot.\n\n"
                f"👤 Contact bot owner: @{Config.OWNER_USERNAME}\n"
                f"🆔 Owner ID: <code>{Config.OWNER_ID}</code>"
            )
        
        # In authorized groups, check if user is active
        is_active = await AuthHelper.is_user_active(user_id, chat_id)
        if not is_active:
            return False, (
                "⚠️ <b>Bot is in Hold Mode</b>\n\n"
                "You need to activate the bot first by sending /start command.\n"
                "The bot will then be active only for you in this group."
            )
        
        return True, ""
    
    @staticmethod
    async def activate_user(user_id: int, chat_id: int):
        """Activate user for a chat"""
        await db_handler.activate_user(user_id, chat_id)
    
    @staticmethod
    async def deactivate_user(user_id: int, chat_id: int):
        """Deactivate user for a chat"""
        await db_handler.deactivate_user(user_id, chat_id)
    
    @staticmethod
    def get_unauthorized_message() -> str:
        """Get message for unauthorized access"""
        return (
            "🚫 <b>Unauthorized Access</b>\n\n"
            "You are not authorized to use this bot.\n\n"
            f"👤 Contact bot owner: @{Config.OWNER_USERNAME}\n"
            f"🆔 Owner ID: <code>{Config.OWNER_ID}</code>"
        )
    
    @staticmethod
    def get_owner_contact_info() -> str:
        """Get owner contact information"""
        return (
            f"👤 <b>Bot Owner:</b> @{Config.OWNER_USERNAME}\n"
            f"🆔 <b>Owner ID:</b> <code>{Config.OWNER_ID}</code>"
        )
