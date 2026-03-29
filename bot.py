import os, logging, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
QUESTIONS = ["Q1", "Q2", "Q3", "Q4", "Q5"]

async def start(u, c):
    kb = [[InlineKeyboardButton("Start", callback_data="s")]]
    await u.message.reply_text("Hello", reply_markup=InlineKeyboardMarkup(kb))

async def bh(u, c):
    q = u.callback_query; await q.answer(); d = q.data
    if d == "s": c.user_data["s"] = 0; c.user_data["i"] = 0
    elif d == "y": c.user_data["s"] = c.user_data.get("s", 0) + 1; c.user_data["i"] = c.user_data.get("i", 0) + 1
    elif d == "n": c.user_data["i"] = c.user_data.get("i", 0) + 1
    idx = c.user_data.get("i", 0)
    if idx < len(QUESTIONS):
        kb = [[InlineKeyboardButton("Yes", callback_data="y"), InlineKeyboardButton("No", callback_data="n")]]
        await q.edit_message_text(QUESTIONS[idx], reply_markup=InlineKeyboardMarkup(kb))
    else:
        await q.edit_message_text(f"Done score {c.user_data.get('s')}")

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

def main():
    p = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: HTTPServer(('', p), H).serve_forever(), daemon=True).start()
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(bh))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__': main()
