import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

QUESTIONS = [
    "1/5: Требования зафиксированы?",
    "2/5: Постановщик меняет мнение?",
    "3/5: Задача на две системы?",
    "4/5: Сроки уже назначены?",
    "5/5: Задача уже провалилась?"
]

def get_res(s):
    if s == 0: return "КТЗ=0: Чисто. Задача управляема!"
    if s <= 2: return f"КТЗ={s}: Риск. Есть тревожные сигналы."
    return f"КТЗ={s}: ТРЕВОГА. Задача токсична!"

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Начать расчет КТЗ", callback_data="s")]]
    await u.message.reply_text(
        "Токсикомер задач (КТЗ-калькулятор)\n\nУзнай уровень токсичности своей задачи за 5 вопросов.\n\nКанал: @async_mind_it",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def bh(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    d = q.data

    if d == "s":
        c.user_data["s"] = 0
        c.user_data["i"] = 0
    elif d == "y":
        c.user_data["s"] = c.user_data.get("s", 0) + 1
        c.user_data["i"] = c.user_data.get("i", 0) + 1
    elif d == "n":
        c.user_data["i"] = c.user_data.get("i", 0) + 1

    i = c.user_data.get("i", 0)

    if i < len(QUESTIONS):
        kb = [[InlineKeyboardButton("Да", callback_data="y"), InlineKeyboardButton("Нет", callback_data="n")]]
        await q.edit_message_text(QUESTIONS[i], reply_markup=InlineKeyboardMarkup(kb))
    else:
        s = c.user_data.get("s", 0)
        res = get_res(s)
        await q.edit_message_text(
            f"Результат: {res}\n\nПодпишись на @async_mind_it — там про управление задачами без токсичности!"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(bh))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
