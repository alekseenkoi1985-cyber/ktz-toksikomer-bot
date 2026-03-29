import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
URL = os.environ.get("RENDER_EXTERNAL_URL")

QUESTIONS = [
    "1/5: Требования зафиксированы?",
    "2/5: Постановщик меняет мнение?",
    "3/5: Задача на две системы?",
    "4/5: Сроки уже назначены?",
    "5/5: Задача уже провалилась?"
]

def get_res(s):
    if s == 0: return "КТЗ=0: Чисто."
    if s <= 2: return f"КТЗ={s}: Риск."
    return f"КТЗ={s}: ТРЕВОГА."

async def start(u, c):
    kb = [[InlineKeyboardButton("Начать", callback_data="s")]]
    await u.message.reply_text("КТЗ Бот @async_mind_it", reply_markup=InlineKeyboardMarkup(kb))

async def bh(u, c):
    q = u.callback_query; await q.answer(); d = q.data
    if d == "s": c.user_data["s"] = 0; c.user_data["i"] = 0
    elif d == "y": c.user_data["s"] = c.user_data.get("s", 0) + 1; c.user_data["i"] = c.user_data.get("i", 0) + 1
    elif d == "n": c.user_data["i"] = c.user_data.get("i", 0) + 1
    
    i = c.user_data.get("i", 0)
    if i < len(QUESTIONS):
        kb = [[InlineKeyboardButton("Да", callback_data="y"), InlineKeyboardButton("Нет", callback_data="n")]]
        await q.edit_message_text(QUESTIONS[i], reply_markup=InlineKeyboardMarkup(kb))
    else:
        await q.edit_message_text(f"{get_res(c.user_data.get('s'))}
@async_mind_it")

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(bh))
    if URL:
        logger.info(f"Webhook on {PORT}")
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"{URL}/{TOKEN}")
    else:
        logger.info("Polling")
        app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
