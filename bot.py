from os import environ
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest
import logging

logging.basicConfig(level=logging.INFO)

pr0fess0r_99 = Client(
    "Auto Approved Bot",
    bot_token=environ["BOT_TOKEN"],
    api_id=int(environ["API_ID"]),
    api_hash=environ["API_HASH"]
)

# Safe parsing of CHAT_ID
chat_id_env = environ.get("CHAT_ID")
CHAT_ID = [int(x) for x in chat_id_env.split()] if chat_id_env else []

TEXT = environ.get(
    "APPROVED_WELCOME_TEXT",
    "Hello {mention}\nWelcome To {title}\n\nYou are auto approved!"
)
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()


@pr0fess0r_99.on_message(filters.private & filters.command(["start"]))
async def start(client: Client, message: Message):
    approvedbot = await client.get_me()
    mention = message.from_user.mention if message.from_user else "there"
    button = [
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
        text=f"**Hello {mention}! I am Auto Approver Bot. Add me to your group: [Click Here](http://t.me/{approvedbot.username}?startgroup=botstart)**",
        reply_markup=InlineKeyboardMarkup(button),
        disable_web_page_preview=True
    )


@pr0fess0r_99.on_chat_join_request(
    (filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel)
)
async def autoapprove(client: Client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    logging.info(f"{user.first_name} Joined {chat.title} 🤝")
    
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    
    if APPROVED == "on":
        await client.send_message(
            chat_id=chat.id,
            text=TEXT.format(mention=user.mention, title=chat.title)
        )


logging.info("Auto Approved Bot is running...")
pr0fess0r_99.run()
