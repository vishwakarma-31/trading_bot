import logging
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# Fix the Updater class issue by patching the __slots__ at the class level
import telegram.ext._updater

# Get the original __slots__
original_slots = telegram.ext._updater.Updater.__slots__

# Check if the missing attribute is already in __slots__
if "__polling_cleanup_cb" not in original_slots:
    # Create a new __slots__ with the missing attribute
    new_slots = original_slots + ("__polling_cleanup_cb",)
    
    # Create a new class with the correct __slots__
    class PatchedUpdater(telegram.ext._updater.Updater):
        __slots__ = new_slots
        
        def __init__(self, bot, update_queue):
            # Initialize all attributes that are in __slots__
            object.__setattr__(self, 'bot', bot)
            object.__setattr__(self, 'update_queue', update_queue)
            object.__setattr__(self, '_last_update_id', 0)
            object.__setattr__(self, '_running', False)
            object.__setattr__(self, '_initialized', False)
            object.__setattr__(self, '_httpd', None)
            object.__setattr__(self, '_Updater__lock', asyncio.Lock())
            object.__setattr__(self, '_Updater__polling_task', None)
            object.__setattr__(self, '_Updater__polling_cleanup_cb', None)
    
    # Replace the original Updater with our patched version
    telegram.ext._updater.Updater = PatchedUpdater

import asyncio

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