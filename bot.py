import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOD_GROUP_ID = int(os.getenv("MOD_GROUP_ID", "0"))
ADMINS = {int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()}

# Adminga yuborilgan xabar message_id -> user_id
USER_MESSAGES = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ассалому алайкум!\n\n"
        "Бу бот орқали таклиф, мурожаат ва саволларингизни юборишингиз мумкин."
    )


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Group ID: {update.effective_chat.id}")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.message.from_user
    user_id = user.id
    full_name = user.full_name or "Foydalanuvchi"
    username = f"@{user.username}" if user.username else "yo‘q"

    text = update.message.text or ""
    caption = update.message.caption or ""

    info_text = (
        f"📩 Янги мурожаат\n\n"
        f"👤 Исм: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: {user_id}"
    )

    # Matn
    if update.message.text:
        sent_info = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=info_text)
        sent_msg = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=text)
        USER_MESSAGES[sent_info.message_id] = user_id
        USER_MESSAGES[sent_msg.message_id] = user_id

    # Foto
    elif update.message.photo:
        sent_info = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=info_text)
        sent_msg = await context.bot.send_photo(
            chat_id=MOD_GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption or "📷 Foto yuborildi",
        )
        USER_MESSAGES[sent_info.message_id] = user_id
        USER_MESSAGES[sent_msg.message_id] = user_id

    # Video
    elif update.message.video:
        sent_info = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=info_text)
        sent_msg = await context.bot.send_video(
            chat_id=MOD_GROUP_ID,
            video=update.message.video.file_id,
            caption=caption or "🎥 Video yuborildi",
        )
        USER_MESSAGES[sent_info.message_id] = user_id
        USER_MESSAGES[sent_msg.message_id] = user_id

    # Document
    elif update.message.document:
        sent_info = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=info_text)
        sent_msg = await context.bot.send_document(
            chat_id=MOD_GROUP_ID,
            document=update.message.document.file_id,
            caption=caption or "📄 Hujjat yuborildi",
        )
        USER_MESSAGES[sent_info.message_id] = user_id
        USER_MESSAGES[sent_msg.message_id] = user_id

    # Audio
    elif update.message.audio:
        sent_info = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=info_text)
        sent_msg = await context.bot.send_audio(
            chat_id=MOD_GROUP_ID,
            audio=update.message.audio.file_id,
            caption=caption or "🎵 Audio yuborildi",
        )
        USER_MESSAGES[sent_info.message_id] = user_id
        USER_MESSAGES[sent_msg.message_id] = user_id

    # Voice
    elif update.message.voice:
        sent_info = await context.bot.send_message(chat_id=MOD_GROUP_ID, text=info_text)
        sent_msg = await context.bot.send_voice(
            chat_id=MOD_GROUP_ID,
            voice=update.message.voice.file_id,
            caption=caption or "🎤 Ovozli хабар yuborildi",
        )
        USER_MESSAGES[sent_info.message_id] = user_id
        USER_MESSAGES[sent_msg.message_id] = user_id

    else:
        await update.message.reply_text(
            "Ҳозирча фақат матн, фото, видео, аудио ва ҳужжат қабул қилинади."
        )
        return

    await update.message.reply_text("Хабарингиз қабул қилинди ✅")


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    if MOD_GROUP_ID == 0:
        return

    if update.effective_chat.id != MOD_GROUP_ID:
        return

    if update.effective_user.id not in ADMINS:
        return

    if not update.message.reply_to_message:
        return

    replied_msg_id = update.message.reply_to_message.message_id
    if replied_msg_id not in USER_MESSAGES:
        return

    user_id = USER_MESSAGES[replied_msg_id]

    try:
        # Matnli javob
        if update.message.text:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📩 Жавоб:\n\n{update.message.text}"
            )

        # Foto bilan javob
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=update.message.photo[-1].file_id,
                caption=update.message.caption or ""
            )

        # Video bilan javob
        elif update.message.video:
            await context.bot.send_video(
                chat_id=user_id,
                video=update.message.video.file_id,
                caption=update.message.caption or ""
            )

        # Document bilan javob
        elif update.message.document:
            await context.bot.send_document(
                chat_id=user_id,
                document=update.message.document.file_id,
                caption=update.message.caption or ""
            )

        # Audio bilan javob
        elif update.message.audio:
            await context.bot.send_audio(
                chat_id=user_id,
                audio=update.message.audio.file_id,
                caption=update.message.caption or ""
            )

        # Voice bilan javob
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=user_id,
                voice=update.message.voice.file_id,
                caption=update.message.caption or ""
            )

        else:
            await update.message.reply_text("Бу турдаги жавоб ҳозирча қўлланмайди.")
            return

        await update.message.reply_text("Жавоб фойдаланувчига юборилди ✅")

    except Exception as e:
        await update.message.reply_text(f"Хатолик: {e}")


async def debug_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Guruhda oddiy xabar yozilganda ID ni chiqarish uchun.
    Faqat adminlar uchun ishlaydi.
    """
    if not update.message or not update.effective_user:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    if update.effective_user.id not in ADMINS:
        return

    # /id komandasi bo'lmasa ham, bot guruh ID sini ko'rsatadi
    if update.message.text and update.message.text.lower() in ["salom", "id", "/id", "/update_id"]:
        await update.message.reply_text(f"Group ID: {update.effective_chat.id}")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi")

    app = Application.builder().token(BOT_TOKEN).build()

    # Private chat
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_user_message))

    # Guruh ID olish
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, debug_group_id))

    # Admin reply
    app.add_handler(MessageHandler(filters.Chat(MOD_GROUP_ID) & ~filters.COMMAND, handle_admin_reply))

    print("Namangan2uygonish bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
