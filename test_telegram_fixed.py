import logging
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# Fix the Updater class issue by monkey-patching
import telegram.ext._updater

# Monkey patch the __init__ method to handle the missing attribute
original_init = telegram.ext._updater.Updater.__init__

def patched_init(self, bot, update_queue):
    # Call the original __init__ method
    original_init(self, bot, update_queue)
    # Add the missing attribute with setattr to bypass __slots__ restriction
    object.__setattr__(self, '_Updater__polling_cleanup_cb', None)

telegram.ext._updater.Updater.__init__ = patched_init

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if update.message:
        await update.message.reply_text("Hello! I'm working!")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("8430652190:AAG_KoUuHQqqVT9ZwSlPUQ9iSMznK7kqs0w").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=[])

if __name__ == "__main__":
    main()