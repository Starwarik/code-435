from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import os

# Настройки API - ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ КЛЮЧ!
OPENWEATHER_API_KEY = "a9490cc69b99d88eaa4d7507b356968f"  # ЗДЕСЬ ДОЛЖЕН БЫТЬ ВАШ КЛЮЧ OPENWEATHERMAP
TELEGRAM_BOT_TOKEN_normal = "8475963022:AAF6Cd_XZau_pBgmUuQVPUc9DnRAmCChfmw"
TELEGRAM_BOT_TOKEN = "5862928083:AAFjQ9YyeW3ohHtgNfBisW73-S87WB0QBSs"
CITY = "Saratov"
COUNTRY_CODE = "RU"

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query.data == "conditions":
        query = update.callback_query
        try:
            # Проверяем, установлен ли API ключ
            if OPENWEATHER_API_KEY in ["ваш_ключ_openweathermap_здесь", "your_openweather_api_key_here"]:
                await context.bot.send_message(chat_id=query.message.chat_id,
                    text="❌ API ключ OpenWeatherMap не настроен!\n\n"
                    "Пожалуйста, получите бесплатный ключ на:\n"
                    "https://home.openweathermap.org/api_keys\n\n"
                    "И замените значение OPENWEATHER_API_KEY в коде"
                )
                return
        
            # Формируем URL для запроса погоды
            url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        
            # Делаем запрос к API
            response = requests.get(url, timeout=10)
            data = response.json()
        
            # Проверяем успешность запроса
            if response.status_code == 200:
                # Извлекаем данные о погоде
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                pressure = data['main']['pressure']
                description = data['weather'][0]['description']
                wind_speed = data['wind'].get('speed', 'н/д')
            
                # Формируем сообщение
                weather_message = (
                    f"🌤 Погода в Саратове:\n"
                    f"• Температура: {temp}°C\n"
                    f"• Ощущается как: {feels_like}°C\n"
                    f"• Описание: {description.capitalize()}\n"
                    f"• Влажность: {humidity}%\n"
                    f"• Давление: {pressure} гПа\n"
                    f"• Скорость ветра: {wind_speed} м/с"
                )
                await update.callback_query.answer()
                await context.bot.send_message(chat_id=query.message.chat_id,
                text=weather_message)
        
            elif response.status_code == 401:
                await context.bot.send_message(chat_id=query.message.chat_id,
                    text="❌ Неверный API ключ OpenWeatherMap!\n\n"
                    "Пожалуйста, проверьте ваш ключ на:\n"
                    "https://home.openweathermap.org/api_keys\n\n"
                    "Убедитесь, что ключ активирован (это может занять несколько часов)"
                )
        
            else:
                error_msg = data.get('message', 'Неизвестная ошибка')
                await context.bot.send_message(chat_id=query.message.chat_id,
                text=f"❌ Ошибка API: {error_msg}")
            
        except requests.exceptions.Timeout:
            await context.bot.send_message(chat_id=query.message.chat_id,
            text="⏰ Таймаут соединения с сервером погоды")
        except requests.exceptions.ConnectionError:
            await context.bot.send_message(chat_id=query.message.chat_id,
            text="📡 Ошибка соединения с интернетом")
        except Exception as e:
            await context.bot.send_message(chat_id=query.message.chat_id,
            text=f"❌ Произошла непредвиденная ошибка: {str(e)}")

async def gorpark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "gorpark":
        keyboard = [
        [InlineKeyboardButton("Дальше", callback_data="nabka")]
        ]
        query = update.callback_query
        await update.callback_query.answer()
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=query.message.chat_id,
        text="Гид по городу Саратову позволит вам узнать о городе!")

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://pp.vk.me/c628225/v628225107/26cd5/wAqYn5ApXOQ.jpg")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="gorpark.mp4",
        caption="Горпарк это шикарное место",
				reply_markup=reply_markup)

async def nabka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "nabka":
        keyboard = [
        [InlineKeyboardButton("Назад", callback_data="gorpark"), InlineKeyboardButton("Дальше", callback_data="lipki")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://saratov.travel/upload/resize_cache/iblock/727/800_800_1/6kexsl38l39dqiqo8xvcyzhlk5oh3qit.jpg")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="nabka.mp4",
        caption="А набережная это вообще отпад!",
        reply_markup=reply_markup)

async def lipki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "lipki":
        keyboard = [
        [InlineKeyboardButton("Назад", callback_data="nabka"), InlineKeyboardButton("Дальше", callback_data="utoli")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://img.tourister.ru/files/3/3/9/1/7/5/1/0/2/original.jpg")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="lipki.mp4",
        caption="А липки это вообще отпад!",
        reply_markup=reply_markup)

async def utoli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "utoli":
        keyboard = [
        [InlineKeyboardButton("Назад", callback_data="lipki"), InlineKeyboardButton("Дальше", callback_data="conserva")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://cdn-imgproxy.mamado.su/7u7PXEMY0t4nQlCVI-XgWcDomrKi-dObs_pLLDpPVBA/rs:fit:2000:2000:1/g:ce/q:90/czM6Ly9tYW1hZG8t/YXBpLXByb2R1Y3Rp/b24vc3RvcmFnZS8x/Mjc3MTczL1NjcmVl/bnNob3RfMy5wbmc.webp")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="utoli.mp4",
        caption="А утоли это вообще отпад!",
        reply_markup=reply_markup)

async def conserva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "conserva":
        keyboard = [
        [InlineKeyboardButton("Назад", callback_data="utoli"), InlineKeyboardButton("Дальше", callback_data="avenue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://static.gorodzovet.ru/uploads/venue/venuelogo-2903106.jpg?v=")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="conserva.mp4",
        caption="А консерватория это вообще отпад!",
        reply_markup=reply_markup)

async def avenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "avenue":
        keyboard = [
        [InlineKeyboardButton("Назад", callback_data="conserva"), InlineKeyboardButton("Дальше", callback_data="circus")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://www.tursar.ru/uploads/img361_5.jpg",
        reply_markup=reply_markup)
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="avenue.mp4",
        caption="А проспект это вообще отпад!")

async def circus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "circus":
        keyboard = [
        [InlineKeyboardButton("Назад", callback_data="avenue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://upload.wikimedia.org/wikipedia/commons/6/66/%D0%A6%D0%B8%D1%80%D0%BA_%D0%B2_%D0%A1%D0%B0%D1%80%D0%B0%D1%82%D0%BE%D0%B2%D0%B5.jpg",
        reply_markup=reply_markup)
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="circus.mp4",
        caption="А цирк это вообще отпад!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
      [InlineKeyboardButton("Погода в Саратове", callback_data="conditions")],
      [InlineKeyboardButton("Гид по городу", callback_data="gorpark")]
      ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "👋 Добро пожаловать в Саратовский Гулливер!\n\n"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

def main():
    print("Запуск бота...")
    print(f"Токен бота: {'установлен' if len(TELEGRAM_BOT_TOKEN) > 20 else 'не установлен'}")
    print(f"OpenWeather ключ: {'установлен' if OPENWEATHER_API_KEY not in ['ваш_ключ_openweathermap_здесь', 'your_openweather_api_key_here'] else 'НЕ УСТАНОВЛЕН!'}")
    
    # Создаем приложение
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(weather, pattern="^conditions$"))
    app.add_handler(CallbackQueryHandler(gorpark, pattern="^gorpark$"))
    app.add_handler(CallbackQueryHandler(nabka, pattern="^nabka$"))
    app.add_handler(CallbackQueryHandler(lipki, pattern="^lipki$"))
    app.add_handler(CallbackQueryHandler(utoli, pattern="^utoli$"))
    app.add_handler(CallbackQueryHandler(conserva, pattern="^conserva$"))
    app.add_handler(CallbackQueryHandler(avenue, pattern="^avenue$"))
    app.add_handler(CallbackQueryHandler(circus, pattern="^circus$"))

    print("Бот запущен! Используйте /start для начала")
    app.run_polling()

if __name__ == "__main__":
    main()
