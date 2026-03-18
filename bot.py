import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOD_GROUP_ID = int(os.getenv("MOD_GROUP_ID"))
ADMINS = {int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()}

USER_MESSAGES = {}


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Group ID: {update.effective_chat.id}")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ассалому алайкум!\n\n"
        "Taklif, murojaat va savollaringizni shu bot orqali yuborishingiz mumkin."
    )


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.message.from_user
    user_id = user.id
    full_name = user.full_name or "Foydalanuvchi"
    username = f"@{user.username}" if user.username else "yo‘q"
    text = update.message.text or ""

    sent = await context.bot.send_message(
        chat_id=MOD_GROUP_ID,
        text=(
            f"📩 Yangi murojaat\n\n"
            f"👤 Ism: {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: {user_id}\n\n"
            f"💬 Xabar:\n{text}"
        )
    )

    USER_MESSAGES[sent.message_id] = user_id

    await update.message.reply_text("Xabaringiz qabul qilindi ✅")


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    if update.effective_user.id not in ADMINS:
        return

    if update.effective_chat.id != MOD_GROUP_ID:
        return

    if not update.message.reply_to_message:
        return

    replied_msg_id = update.message.reply_to_message.message_id
    if replied_msg_id not in USER_MESSAGES:
        return

    user_id = USER_MESSAGES[replied_msg_id]
    reply_text = update.message.text or ""

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📩 Javob:\n\n{reply_text}"
        )
        await update.message.reply_text("Javob foydalanuvchiga yuborildi ✅")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, handle_user_message))
    app.add_handler(MessageHandler(filters.Chat(MOD_GROUP_ID) & filters.TEXT, handle_admin_reply))

    print("Namangan2uygonish bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
