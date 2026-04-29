import logging

import discord

import controller
from models import DiscordUser

logger: logging.Logger = logging.getLogger(__name__)


def get_user_info(member: discord.User | discord.Member) -> DiscordUser:
    from datetime import datetime

    from models import DiscordUser

    user_name: str = str(member)
    user_id: int = member.id
    display_name: str = member.display_name
    avatar_url: str = member.avatar.url if member.avatar else ""
    account_created: datetime = member.created_at
    joined_server: datetime = member.joined_at  # type:ignore
    roles: list[str] = [role.name for role in member.roles if role.name != "@everyone"]  # type:ignore

    return DiscordUser(
        user_id,
        user_name,
        display_name,
        avatar_url,
        account_created,
        joined_server,
        roles,
    )


def save_content_to_db(user: DiscordUser, message: discord.Message):
    controller.insert_discord_user(
        user.user_id,
        user.user_name,
        user.display_names,
        user.avatar_url,
        user.account_created.isoformat(),
        user.joined_server.isoformat(),
        user.roles,
    )

    controller.insert_message(
        message.id,
        user.user_id,
        message.content,
        message.created_at.isoformat(),
    )


def on_message(message: discord.Message):
    if message.author == message.guild.me:  # type:ignore
        return

    logger.info(f"{message.author}: {message.content}")

    user: DiscordUser = get_user_info(message.author)
    save_content_to_db(user, message)

    from utils import patterns

    detected = patterns.get_detected_types(message.content)
    if detected:
        logger.info(f" >> [{message.id}] Content detected:")
        for key, values in detected.items():
            logger.info(f"    {key}: {values}")

    for item in patterns.extract_all(message.content):
        controller.insert_filtered_content(message.id, item.content_type, item.value)

    return True


def on_member_join(member: discord.Member):
    logger.info(f" # Nuevo usuario: {member} (ID: {member.id})")

    user: DiscordUser = get_user_info(member)
    controller.insert_discord_user(
        user.user_id,
        user.user_name,
        user.display_names,
        user.avatar_url,
        user.account_created.isoformat(),
        user.joined_server.isoformat(),
        user.roles,
    )
    return True
