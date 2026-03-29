import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = "https://ktz-toksikomer-bot.onrender.com"

QUESTIONS = [
    "1/5: Критерий приемки четко определен?",
    "2/5: Есть один человек, чье \u00abок\u00bb закрывает задачу?",
    "3/5: Есть внешние зависимости вне нашего контроля?",
    "4/5: Задача уже возвращалась без изменений требований?",
    "5/5: Дедлайн поставлен до старта анализа?"
]

def get_res(s):
    if s == 0:
        return (
            "КТЗ=0 \u2705\n\n"
            "Задача чистая. Критерии есть, владелец есть, зависимостей нет.\n\n"
            "Берите в работу \u2014 это редкость, цените."
        )
    if s == 1:
        return (
            "КТЗ=1 \U0001f7e1\n\n"
            "Почти чисто. Один сигнал \u2014 не критично, но не игнорируйте.\n\n"
            "Найдите слабое место до старта.\n"
            "Один уточняющий вопрос владельцу закроет риск."
        )
    if s == 2:
        return (
            "КТЗ=2 \U0001f7e0\n\n"
            "Риск есть. Задача может вернуться.\n\n"
            "До старта \u2014 два вопроса:\n"
            "\u2014 Кто именно говорит \u00abпринято\u00bb?\n"
            "\u2014 Что именно считается результатом?\n\n"
            "Без ответов на оба \u2014 не стартуйте."
        )
    if s == 3:
        return (
            "КТЗ=3 \U0001f534\n\n"
            "Высокий риск. Вероятность переделок \u2014 выше среднего.\n\n"
            "Три варианта действий:\n"
            "\u2014 Декомпозируйте и возьмите только управляемую часть\n"
            "\u2014 Снимите внешние зависимости до старта\n"
            "\u2014 Согласуйте промежуточный чекпоинт на 30\u201340% объема\n\n"
            "Иначе \u2014 потеряете время дважды."
        )
    if s == 4:
        return (
            "КТЗ=4 \U0001f6a8\n\n"
            "Задача токсична. Почти все сигналы красные.\n\n"
            "Не берите в работу без синхронизации с владельцем.\n"
            "Повторный запуск без изменения условий \u2014 "
            "это не оптимизм, это потеря ресурса.\n\n"
            "Сначала разговор. Потом старт."
        )
    return (
        "КТЗ=5 \u2620\ufe0f\n\n"
        "Максимум. Все пять сигналов активны одновременно.\n\n"
        "Задача не готова к исполнению \u2014 она готова к обсуждению.\n"
        "Критерии, владелец, зависимости, дедлайн \u2014 "
        "всё нужно переопределить до первого действия."
    )

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
            f"{res}\n\nБольше про управление задачами \u2014 @async_mind_it"
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
