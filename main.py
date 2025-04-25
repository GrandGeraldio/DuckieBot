import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Выполнить", callback_data="execute")],
        [InlineKeyboardButton("Инфо", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбери действие:", reply_markup=reply_markup)

# === Получить уточку ===
async def get_random_duck_url():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://random-d.uk/api/random") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("url")
            return None

# === Обработчик кнопок ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    if query.data == "execute":
        duck_url = await get_random_duck_url()
        if duck_url:
            # Отправляем картинку уточки
            await context.bot.send_photo(chat_id=chat_id, photo=duck_url, caption="Вот тебе уточка 🦆")

            # Загружаем и отправляем как файл
            async with aiohttp.ClientSession() as session:
                async with session.get(duck_url) as duck_response:
                    if duck_response.status == 200:
                        file_bytes = await duck_response.read()
                        filename = duck_url.split("/")[-1]
                        await context.bot.send_document(chat_id=chat_id, document=file_bytes, filename=filename)
                    else:
                        await context.bot.send_message(chat_id=chat_id, text="⚠️ Не удалось загрузить файл уточки.")

            # Отправляем кнопку "Ещё уточку"
            again_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🦆 Ещё уточку!", callback_data="execute")]
            ])
            await context.bot.send_message(chat_id=chat_id, text="Хочешь ещё одну? 👇", reply_markup=again_markup)

        else:
            await context.bot.send_message(chat_id=chat_id, text="😢 Уточка куда-то уплыла. Попробуй ещё раз.")

    elif query.data == "info":
        await query.edit_message_text(
            "ℹ️ Этот бот показывает случайных уточек с сайта random-d.uk.\n"
            "Нажми кнопку, чтобы получить уточку в виде картинки и файла!"
        )

# === Запуск бота ===
async def main():
    bot_token = "8165993424:AAEZtBnopVdzNY1GgnXeE5enullhXBkm7Dk"
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())