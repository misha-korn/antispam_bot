import datetime
import os

import pytz
from dotenv import load_dotenv
from telegram import ChatPermissions, Update
from telegram.constants import ParseMode

from db import add_penalty, add_user

load_dotenv()

SILENSE_MODE = False if os.getenv("SILENSE_MODE") == "False" else True


async def is_user_admin(update: Update):
    administrators = await update.effective_chat.get_administrators()
    administrators_id = [admin.user.id for admin in administrators]
    if update.effective_user.id in administrators_id:
        return True
    else:
        return False


def time_ban(days=0, hours=0, minutes=0):
    return datetime.datetime.now(
        tz=pytz.timezone("Europe/Moscow")
    ) + datetime.timedelta(days=days, hours=hours, minutes=minutes)


def parse_message(text):
    symbols = ",.-+!"
    for symbol in symbols:
        text = text.replace(symbol, f"\{symbol}")
    return text


async def forbid_send_message(update: Update, context, text):
    user_has_penalty = await add_penalty(update.effective_user.id)
    penalty = await add_penalty(update.effective_user.id) + 1
    # Ограничение на время штраф + 1 * час
    if user_has_penalty:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            update.effective_user.id,
            ChatPermissions(can_send_messages=False),
            time_ban(hours=penalty),
        )
    print(SILENSE_MODE, type((SILENSE_MODE)))
    if not SILENSE_MODE:
        await update.message.reply_text(
            parse_message(
                f"[{update.effective_user.first_name}](tg://user?id={update.effective_user.id}), {text}...\n_Сообщение удалено_ 🛡"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )


async def ban_user(update: Update, context):
    await context.bot.ban_chat_member(
        update.effective_chat.id,
        update.effective_user.id,
        time_ban(days=500),
    )
    await add_user(update.effective_user.id)
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )
