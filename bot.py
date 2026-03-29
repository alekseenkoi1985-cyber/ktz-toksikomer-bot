import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

QUESTIONS = [
    "Вопрос 1/5
Требования к задаче нигде не зафиксированы письменно?",
    "Вопрос 2/5
Постановщик задачи недоступен или меняет мнение на ходу?",
    "Вопрос 3/5
Задача затрагивает более двух команд или систем?",
    "Вопрос 4/5
Сроки уже назначены до начала декомпозиции?",
    "Вопрос 5/5
Подобная задача уже провалилась или затянулась в прошлом?",
]

def get_result_text(score: int) -> str:
    if score == 0:
        return (
            "*КТЗ = 0 — Задача \"чистая\"*

"
            "Берите в спринт без опасений. Всё прозрачно и управляемо.

"
        )
    elif score <= 2:
        return (
            f"*КТЗ = {score} — Умеренный риск*

"
            "Зафиксируйте требования письменно до старта.
"
            "Согласуйте критерии приёмки с постановщиком.

"
        )
    elif score <= 4:
        return (
            f"*КТЗ = {score} — Высокий риск*

"
            "Декомпозируйте на более мелкие куски.
"
            "Договоритесь о регулярных синках с командами.
"
            "Оставьте в плане 30% времени на непредвиденное.

"
        )
    else:
        return (
            f"*КТЗ = {score} — Критический риск (\"Задача-зомби\")*

"
            "Не берите такую задачу без полной переоценки.
"
            "Возможно, она не стоит потраченного времени вообще.
"
            "Проведите встречу с заказчиком и всеми сторонами.

"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")
    keyboard = [[InlineKeyboardButton("Начать тест КТЗ", callback_data="start_test")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я помогу оценить *Коэффициент Токсичности Задачи* (КТЗ).
"
        "Ответь на 5 вопросов и узнай, стоит ли браться за эту задачу.

"
        "🔗 Подписывайся на канал @async_mind_it",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Button pressed: {query.data}")

    if query.data == "start_test":
        context.user_data["score"] = 0
        context.user_data["question_index"] = 0
        await ask_question(query, context)
    elif query.data == "yes":
        context.user_data["score"] = context.user_data.get("score", 0) + 1
        context.user_data["question_index"] = context.user_data.get("question_index", 0) + 1
        await ask_question(query, context)
    elif query.data == "no":
        context.user_data["question_index"] = context.user_data.get("question_index", 0) + 1
        await ask_question(query, context)
    elif query.data == "restart":
        context.user_data["score"] = 0
        context.user_data["question_index"] = 0
        await ask_question(query, context)

async def ask_question(query, context):
    index = context.user_data.get("question_index", 0)
    
    if index < len(QUESTIONS):
        keyboard = [
            [InlineKeyboardButton("Да", callback_data="yes"), 
             InlineKeyboardButton("Нет", callback_data="no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            QUESTIONS[index],
            reply_markup=reply_markup
        )
    else:
        score = context.user_data.get("score", 0)
        result_text = get_result_text(score)
        keyboard = [
            [InlineKeyboardButton("Оценить другую задачу", callback_data="restart")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            result_text + "🔗 Больше про управление задачами на @async_mind_it",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# Health Check Server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('', port), HealthHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()

def main():
    # Start health check in thread
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()

    # Start Bot
    if not BOT_TOKEN:
        logger.error("No BOT_TOKEN provided!")
        return

    logger.info("Building application...")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot starting polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
