import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = "https://ktz-toksikomer-bot.onrender.com"

# Вопросы и логика: True = ответ "да" увеличивает КТЗ, False = ответ "нет" увеличивает КТЗ
QUESTIONS = [
    ("1/5: Критерий приемки чётко определён?", False),
    ("2/5: Есть один человек, чьё «ок» закрывает задачу?", False),
    ("3/5: Есть внешние зависимости вне нашего контроля?", True),
    ("4/5: Задача уже возвращалась без изменений требований?", True),
    ("5/5: Дедлайн поставлен до старта анализа?", True),
]

def get_res(s):
    if s == 0:
        return (
            "КТЗ=0 ✅\n\n"
            "Задача чистая. Критерии есть, владелец есть, зависимостей нет.\n\n"
            "Берите в работу — это редкость, цените."
        )
    if s == 1:
        return (
            "КТЗ=1 🟡\n\n"
            "Почти чисто. Один сигнал — не критично, но не игнорируйте.\n\n"
            "Найдите слабое место до старта.\n"
            "Один уточняющий вопрос владельцу закроет риск."
        )
    if s == 2:
        return (
            "КТЗ=2 🟠\n\n"
            "Риск есть. Задача может вернуться.\n\n"
            "До старта — два вопроса:\n"
            "— Кто именно говорит «принято»?\n"
            "— Что именно считается результатом?\n\n"
            "Без ответов на оба — не стартуйте."
        )
    if s == 3:
        return (
            "КТЗ=3 🔴\n\n"
            "Высокий риск. Вероятность переделок — выше среднего.\n\n"
            "Три варианта действий:\n"
            "— Декомпозируйте и возьмите только управляемую часть\n"
            "— Снимите внешние зависимости до старта\n"
            "— Согласуйте промежуточный чекпоинт на 30–40% объёма\n\n"
            "Иначе — потеряете время дважды."
        )
    if s == 4:
        return (
            "КТЗ=4 🚨\n\n"
            "Задача токсична. Почти все сигналы красные.\n\n"
            "Не берите в работу без синхронизации с владельцем.\n"
            "Повторный запуск без изменения условий — "
            "это не оптимизм, это потеря ресурса.\n\n"
            "Сначала разговор. Потом старт."
        )
    return (
        "КТЗ=5 ☠️\n\n"
        "Максимум. Все пять сигналов активны одновременно.\n\n"
        "Задача не готова к исполнению — она готова к обсуждению.\n"
        "Критерии, владелец, зависимости, дедлайн — "
        "всё нужно переопределить до первого действия."
    )

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Начать расчёт КТЗ", callback_data="s")]]
    await u.message.reply_text(
        "Токсикомер задач (КТЗ-калькулятор)\n\n"
        "Узнай уровень токсичности своей задачи за 5 вопросов.\n\n"
        "Канал: @async_mind_it",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def bh(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    d = q.data

    if d == "s":
        c.user_data["s"] = 0
        c.user_data["i"] = 0
    elif d in ("y", "n"):
        i = c.user_data.get("i", 0)
        _, yes_is_bad = QUESTIONS[i]
        if (d == "y" and yes_is_bad) or (d == "n" and not yes_is_bad):
            c.user_data["s"] = c.user_data.get("s", 0) + 1
        c.user_data["i"] = i + 1

    i = c.user_data.get("i", 0)
    if i < len(QUESTIONS):
        question_text, _ = QUESTIONS[i]
        kb = [[
            InlineKeyboardButton("Да", callback_data="y"),
            InlineKeyboardButton("Нет", callback_data="n")
        ]]
        await q.edit_message_text(question_text, reply_markup=InlineKeyboardMarkup(kb))
    else:
        s = c.user_data.get("s", 0)
        res = get_res(s)
        await q.edit_message_text(
            f"{res}\n\nБольше про управление задачами — @async_mind_it"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(bh))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
