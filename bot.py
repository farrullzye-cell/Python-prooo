import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =====================
# KONFIGURASI
# =====================
BOT_TOKEN = "8417791783:AAFpWIfvq6Zw8Lsyx3FWHBla6spu4yvzmeI"
ADMIN_CHAT_ID = 7128038268  # WAJIB: admin harus chat bot dulu
ADMIN_PHONE = "+6285848651208"

LINK_FILE = "links.txt"
PENDING_FILE = "pending.txt"


# =====================
# UTILITAS FILE
# =====================
def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        return []


def append_file(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")


# =====================
# USER COMMAND
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BOT SHARE LINK RANDOM\n\n"
        "Perintah User:\n"
        "• next → link random\n"
        "• /request <link> → ajukan link\n\n"
        f"Admin: {ADMIN_PHONE}"
    )


async def next_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    links = read_file(LINK_FILE)
    if not links:
        await update.message.reply_text("Belum ada link.")
        return
    await update.message.reply_text(random.choice(links))


async def request_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /request https://contoh.com")
        return

    link = context.args[0]
    user = update.effective_user

    record = f"{user.id}|{user.username}|{link}"
    append_file(PENDING_FILE, record)

    # Kirim ke admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "📥 REQUEST LINK BARU\n\n"
            f"User ID: {user.id}\n"
            f"Username: @{user.username}\n"
            f"Link: {link}\n\n"
            "Gunakan:\n"
            f"/approve {link}\n"
            f"/reject {link}"
        )
    )

    await update.message.reply_text("✅ Request dikirim ke admin.")


# =====================
# ADMIN COMMAND
# =====================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if not context.args:
        return

    link = context.args[0]
    append_file(LINK_FILE, link)

    # hapus dari pending
    pendings = read_file(PENDING_FILE)
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        for p in pendings:
            if link not in p:
                f.write(p + "\n")

    await update.message.reply_text("✅ Link disetujui & ditambahkan.")


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if not context.args:
        return

    link = context.args[0]
    pendings = read_file(PENDING_FILE)
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        for p in pendings:
            if link not in p:
                f.write(p + "\n")

    await update.message.reply_text("❌ Link ditolak.")


# =====================
# ROUTER
# =====================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower().strip() == "next":
        await next_link(update, context)


# =====================
# MAIN
# =====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("request", request_link))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("Bot aktif...")
    app.run_polling()


if __name__ == "__main__":
    main()
