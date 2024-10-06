import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from db import create_bd, is_ban_new_member
from sup_func import ban_user, forbid_send_message, is_user_admin

load_dotenv()

SILENSE_MODE = False if os.getenv("SILENSE_MODE") == "False" else True

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id > 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="ИНСТРУКЦИЯ"
        )


async def forward_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_user_admin(update):
        return
    await forbid_send_message(update, context, "в этот чат нельзя пересылать сообщения")


async def message_processing_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_user_admin(update):
        return
    if context.user_data.get("last_message") == update.effective_message.text:
        """Спам много сообщений"""
        await forbid_send_message(update, context, "в этом чате нельзя спамить")
    context.user_data["last_message"] = update.effective_message.text

    ban = False
    ban_1week = False
    for word in stop_words:
        if word.lower() in update.message.text.lower():
            ban_1week = True
    for link in stop_links_words:
        if link.lower() in update.message.text.lower():
            ban = True

    if ban:
        await ban_user(update, context)

    elif ban_1week:
        await forbid_send_message(
            update, context, "в этом чате нельзя писать такие сообщения"
        )


async def joing_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_is_ban = await is_ban_new_member(update.effective_user.id)
    if user_is_ban:
        await ban_user(update, context)
    else:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.effective_message.id
        )


async def kick_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )


def main():
    global stop_words, stop_links_words
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    start_handler = CommandHandler("start", start)
    message_handler = MessageHandler(filters.FORWARDED, forward_processing)
    joing_handler = MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, joing_processing
    )
    kick_handler = MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER, kick_processing
    )
    message_handler_text = MessageHandler(
        filters.TEXT & ~filters.FORWARDED, message_processing_text
    )

    application.add_handlers(
        [
            message_handler,
            start_handler,
            message_handler_text,
            joing_handler,
            kick_handler,
        ]
    )

    with open("stop.txt") as f:
        stop_words = f.read().split()
    with open("stop_links.txt") as f2:
        stop_links_words = f2.read().split()

    application.run_polling()


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(create_bd())
    main()
