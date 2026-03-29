import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

QUESTIONS = [
    "*Вопрос 1/5*\nТребования к задаче нигде не зафиксированы письменно?",
    "*Вопрос 2/5*\nПостановщик задачи недоступен или меняет мнение на ходу?",
    "*Вопрос 3/5*\nЗадача затрагивает более двух команд или систем?",
    "*Вопрос 4/5*\nСроки уже назначены до начала декомпозиции?",
    "*Вопрос 5/5*\nПодобная задача уже провалилась или затянулась в прошлом?",
]

def get_result_text(score: int) -> str:
    if score == 0:
        return (
            "*КТЗ = 0 — Задача чистая*\n\n"
            "Берите в спринт без опасений. Всё прозрачно и управляемо.\n\n"
        )
    elif score <= 2:
        return (
            f"*КТЗ = {score} — Умеренный риск*\n\n"
            "Зафиксируйте требования письменно до старта.\n"
            "Согласуйте критерии приёмки с постановщиком.\n\n"
        )
    elif score <= 4:
        return (
            f"*КТЗ = {score} — Задача токсична*\n\n"
            "Декомпозируйте на подзадачи или верните с вопросами.\n"
            "Не берите в спринт без письменного ТЗ.\n\n"
        )
    else:
        return (
            "*КТЗ = 5 — КРИТИЧНО*\n\n"
            "Немедленный возврат задачи!\n"
            "Запросите письменные требования, доступ к стейкхолдерам\n"
            "и реалистичные сроки до любого обсуждения оценки.\n\n"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    text = (
        "*Токсикомер задач* — инструмент BA/PM\n\n"
        "Метод КТЗ помогает быстро оценить, стоит ли брать задачу в спринт.\n\n"
        "5 вопросов — число от 0 до 5 — чёткий вывод."
    )
    keyboard = [[InlineKeyboardButton("Начать оценку", callback_data="start_quiz")]]
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start_quiz":
        context.user_data["score"] = 0
        context.user_data["q_index"] = 0
        await ask_question(query, context)
    elif data in ("yes", "no"):
        if data == "yes":
            context.user_data["score"] = context.user_data.get("score", 0) + 1
        context.user_data["q_index"] = context.user_data.get("q_index", 0) + 1
        q_index = context.user_data["q_index"]
        if q_index < len(QUESTIONS):
            await ask_question(query, context)
        else:
            await show_result(query, context)
    elif data == "restart":
        context.user_data.clear()
        context.user_data["score"] = 0
        context.user_data["q_index"] = 0
        await ask_question(query, context)

async def ask_question(query, context):
    q_index = context.user_data.get("q_index", 0)
    text = QUESTIONS[q_index]
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="yes"),
            InlineKeyboardButton("Нет", callback_data="no"),
        ]
    ]
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_result(query, context):
    score = context.user_data.get("score", 0)
    result_text = get_result_text(score)
    result_text += (
        "Методика и промпты для BA/PM — в канале *@async_mind_it*"
    )
    keyboard = [
        [InlineKeyboardButton("Читать @async_mind_it", url="https://t.me/async_mind_it")],
        [InlineKeyboardButton("Оценить другую задачу", callback_data="restart")],
    ]
    await query.edit_message_text(
        result_text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
