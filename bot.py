# bot.py
import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, InlineQueryHandler
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise RuntimeError("Ошибка: TELEGRAM_TOKEN не найден в .env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

SERVICES = {
    "Подбор персонала": "Подбор руководителей и специалистов, оценка кандидатов, сопровождение найма.",
    "Аутсорсинг бизнес-функций": "Аутсорсинг HR, административных и IT-функций.",
    "Консалтинг": "Бизнес-консалтинг: стратегия, управление, финансовый консалтинг.",
    "Контакты / Сайт": "🌐 Сайт: https://www.ascr.ru\n📞 Телефон: +7 (495) 123-45-67\n✉️ info@ascr.ru"
}

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().lower()
    results = []

    if not query:
        # Подсказки (примерные запросы)
        suggestions = [
            ("Подбор персонала", "Подбор руководителей и специалистов."),
            ("Аутсорсинг", "Аутсорсинг бизнес-функций."),
            ("Консалтинг", "Стратегия, управление, финансы.")
        ]
        for title, desc in suggestions:
            results.append(
                InlineQueryResultArticle(
                    id=title,
                    title=f"🔹 {title}",
                    description=desc,
                    input_message_content=InputTextMessageContent(
                        f"**{title}**\n\n{desc}",
                        parse_mode="Markdown"
                    )
                )
            )
    else:
        # Обычный поиск по услугам
        for title, desc in SERVICES.items():
            if query in title.lower() or query in desc.lower():
                results.append(
                    InlineQueryResultArticle(
                        id=title,
                        title=f"📋 {title}",
                        description=desc[:80] + "...",
                        input_message_content=InputTextMessageContent(
                            f"**{title}**\n\n{desc}",
                            parse_mode="Markdown"
                        )
                    )
                )

    if not results:
        results.append(
            InlineQueryResultArticle(
                id="no_results",
                title="😕 Ничего не найдено",
                input_message_content=InputTextMessageContent(
                    "По вашему запросу ничего не найдено. Попробуйте: подбор, аутсорсинг, консалтинг."
                )
            )
        )

    await update.inline_query.answer(results, cache_time=1)


def make_keyboard():
    return ReplyKeyboardMarkup(
        [[s] for s in SERVICES.keys()],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user else "гость"

    # Приветственное сообщение
    welcome_text = (
        f"👋 Привет, {name}!\n\n"
        "Я бот компании **ASCR**.\n"
        "Мы предлагаем профессиональные услуги в области:\n\n"
        "💼 Подбор персонала\n"
        "🧾 Аутсорсинг бизнес-функций\n"
        "📊 Консалтинг\n\n"
        "Чтобы узнать подробнее — нажми кнопку ниже 👇"
    )

    # 1️⃣ Отправляем приветствие
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown"
    )

    # 2️⃣ Небольшая задержка (чтобы сообщение выглядело естественно)
    await context.application.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # 3️⃣ Отправляем клавиатуру с кнопками
    await update.message.reply_text(
        "Выбери интересующий раздел:",
        reply_markup=make_keyboard()
    )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите /start, чтобы увидеть список услуг.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in SERVICES:
        await update.message.reply_text(SERVICES[text])
    else:
        await update.message.reply_text("Выберите услугу из меню или введите /help.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(InlineQueryHandler(inline_query))

    logging.info("✅ Бот запущен и работает через polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
