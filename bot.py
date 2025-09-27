import logging
import asyncio
from os import environ, path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest
from pyrogram.errors import BadMsgNotification, RPCError

# ----------------- Logging Setup -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------- Environment Variables -----------------
BOT_TOKEN = environ.get("BOT_TOKEN")
API_ID = environ.get("API_ID")
API_HASH = environ.get("API_HASH")
CHAT_ID_ENV = environ.get("CHAT_ID")  # Space-separated list of IDs
TEXT = environ.get(
    "APPROVED_WELCOME_TEXT",
    "Hello {mention}\nWelcome To {title}\n\nYou are auto approved!"
)
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()
SESSION_FILE = "AutoApprovedBot.session"  # Session filename

# Validate essential environment variables
if not all([BOT_TOKEN, API_ID, API_HASH]):
    logging.error("BOT_TOKEN, API_ID, or API_HASH is not set in environment variables!")
    exit(1)

# Convert CHAT_ID to list of integers
CHAT_ID = [int(x) for x in CHAT_ID_ENV.split()] if CHAT_ID_ENV else []

# ----------------- Initialize Pyrogram Client -----------------
bot = Client(
    "AutoApprovedBot",  # session filename
    bot_token=BOT_TOKEN,
    api_id=int(API_ID),
    api_hash=API_HASH,
)

# ----------------- /start Command -----------------
@bot.on_message(filters.private & filters.command(["start"]))
async def start(client: Client, message: Message):
    approvedbot = await client.get_me()
    mention = message.from_user.mention if message.from_user else "there"

    buttons = [
        [
            InlineKeyboardButton("Support", url="https://t.me/TheNameIs_Yashu"),
            InlineKeyboardButton("Updates 📢", url="https://t.me/+IiS5lW-OAUU1ZGRl")
        ],
        [
            InlineKeyboardButton(
                "➕ Add Me To Your Chat ➕",
                url=f"http://t.me/{approvedbot.username}?startgroup=botstart"
            )
        ]
    ]

    await client.send_message(
        chat_id=message.chat.id,
        text=(
            f"**Hello {mention}! I am Auto Approver Bot. "
            f"Add me to your group: [Click Here](http://t.me/{approvedbot.username}?startgroup=botstart)**"
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

# ----------------- Auto-approve Join Requests -----------------
@bot.on_chat_join_request(
    (filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel)
)
async def autoapprove(client: Client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    logging.info(f"{user.first_name} Joined {chat.title} 🤝")

    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        if APPROVED == "on":
            await client.send_message(
                chat_id=chat.id,
                text=TEXT.format(mention=user.mention, title=chat.title)
            )
    except RPCError as e:
        logging.error(f"Failed to approve/send message for {user.id} in {chat.id}: {e}")

# ----------------- Safe Bot Runner -----------------
async def safe_run():
    # Delete old session file to prevent BadMsgNotification
    if path.exists(SESSION_FILE):
        logging.warning("Deleting old session file to prevent BadMsgNotification...")
        try:
            path.unlink(SESSION_FILE)
        except Exception as e:
            logging.error(f"Failed to delete session file: {e}")

    while True:
        try:
            logging.info("Starting Auto Approved Bot...")
            await bot.start()
            logging.info("Bot is running...")
            await asyncio.Event().wait()  # Keep bot alive
        except BadMsgNotification:
            logging.warning("BadMsgNotification detected! Restarting bot...")
            await bot.stop()
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Unexpected error: {e}. Restarting in 5s...")
            await bot.stop()
            await asyncio.sleep(5)

# ----------------- Entry Point -----------------
if __name__ == "__main__":
    try:
        asyncio.run(safe_run())
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
