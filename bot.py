from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import os

# Настройки API - ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ КЛЮЧ!
OPENWEATHER_API_KEY = "a9490cc69b99d88eaa4d7507b356968f"  # ЗДЕСЬ ДОЛЖЕН БЫТЬ ВАШ КЛЮЧ OPENWEATHERMAP
TELEGRAM_BOT_TOKEN = "8475963022:AAF6Cd_XZau_pBgmUuQVPUc9DnRAmCChfmw"
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Погода в Саратове", callback_data="conditions")]]
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
    app.add_handler(CallbackQueryHandler(weather))
    
    print("Бот запущен! Используйте /start для начала")
    app.run_polling()

if __name__ == "__main__":
    main()
