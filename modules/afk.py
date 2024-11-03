#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


import asyncio
from datetime import datetime

import humanize
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import ReplyCheck

# Variables
AFK = False
AFK_REASON = ""
AFK_TIME = ""
USERS = {}
GROUPS = {}


def GetChatID(message: Message):
    """Get the group id of the incoming message"""
    return message.chat.id


def subtract_time(start, end):
    """Get humanized time"""
    subtracted = humanize.naturaltime(start - end)
    return str(subtracted)


# Main


@Client.on_message(
    ((filters.group & filters.mentioned) | filters.private)
    & ~filters.me
    & ~filters.service,
    group=3,
)
async def collect_afk_messages(bot: Client, message: Message):
    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME)
        is_group = message.chat.type in ["supergroup", "group"]
        CHAT_TYPE = GROUPS if is_group else USERS

        if GetChatID(message) not in CHAT_TYPE:
            text = (
                f"<b>Hey there! Currently offline, probably saving a smile or two 🦷😄\n"
                f"I am not available right now.\n"
                f"Last seen: {last_seen}\n"
                f"Reason: <code>{AFK_REASON.upper()}</code>\n"
                f"Leave a message, and I’ll get back to you faster than you can say 'no cavities!' 😁✨</b>"
            )
            await bot.send_message(
                chat_id=GetChatID(message),
                text=text,
                reply_to_message_id=ReplyCheck(message),
            )
            CHAT_TYPE[GetChatID(message)] = 1
            return
        if GetChatID(message) in CHAT_TYPE:
            if CHAT_TYPE[GetChatID(message)] == 50:
                text = (
                    f"<b>This is an automated message\n"
                    f"Last seen: {last_seen}\n"
                    f"This is the 10th time I've told you I'm AFK right now...\n"
                    f"I'll get to you when I get to you.\n"
                    f"No more auto messages for you</b>"
                )
                await bot.send_message(
                    chat_id=GetChatID(message),
                    text=text,
                    reply_to_message_id=ReplyCheck(message),
                )
            elif CHAT_TYPE[GetChatID(message)] > 50:
                return
            elif CHAT_TYPE[GetChatID(message)] % 5 == 0:
                text = (
                    f"<b>Hey I'm still not back yet.\n"
                    f"Last seen: {last_seen}\n"
                    f"Still busy: <code>{AFK_REASON.upper()}</code>\n"
                    f"Try pinging a bit later.</b>"
                )
                await bot.send_message(
                    chat_id=GetChatID(message),
                    text=text,
                    reply_to_message_id=ReplyCheck(message),
                )

        CHAT_TYPE[GetChatID(message)] += 1


@Client.on_message(filters.command("afk", prefix) & filters.me, group=3)
async def afk_set(_, message: Message):
    global AFK_REASON, AFK, AFK_TIME

    cmd = message.command
    afk_text = ""

    if len(cmd) > 1:
        afk_text = " ".join(cmd[1:])

    if isinstance(afk_text, str):
        AFK_REASON = afk_text

    AFK = True
    AFK_TIME = datetime.now()

    await message.delete()


@Client.on_message(filters.command("afk", "!") & filters.me, group=3)
async def afk_unset(_, message: Message):
    global AFK, AFK_TIME, AFK_REASON, USERS, GROUPS

    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME).replace("ago", "").strip()
        await message.edit(
            f"<code>While you were away (for {last_seen}), you received {sum(USERS.values()) + sum(GROUPS.values())} "
            f"messages from {len(USERS) + len(GROUPS)} chats</code>",
        )
        AFK = False
        AFK_TIME = ""
        AFK_REASON = ""
        USERS = {}
        GROUPS = {}
        await asyncio.sleep(5)

    await message.delete()


@Client.on_message(filters.me, group=3)
async def auto_afk_unset(_, message: Message):
    global AFK, AFK_TIME, AFK_REASON, USERS, GROUPS

    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME).replace("ago", "").strip()
        reply = await message.reply(
            f"<code>While you were away (for {last_seen}), you received {sum(USERS.values()) + sum(GROUPS.values())} "
            f"messages from {len(USERS) + len(GROUPS)} chats</code>"
        )
        AFK = False
        AFK_TIME = ""
        AFK_REASON = ""
        USERS = {}
        GROUPS = {}
        await asyncio.sleep(5)
        await reply.delete()


modules_help["afk"] = {
    "afk [reason]": "Go to AFK mode with reason as anything after .afk\nUsage: <code>.afk <reason></code>",
    "unafk": "Get out of AFK",
}
