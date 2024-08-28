import logging
import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def message_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(1)
    await context.bot.ban_chat_member(
        update.effective_chat.id,
        update.effective_user.id,
        datetime.datetime.now() + datetime.timedelta(minutes=1),
    )
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    start_handler = CommandHandler("start", start)
    message_handler = MessageHandler(filters.FORWARDED, message_processing)

    application.add_handlers([message_handler, start_handler])

    application.run_polling()
