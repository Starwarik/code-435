from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import random
import os
from datetime import datetime

# Настройки API
OPENWEATHER_API_KEY = "a9490cc69b99d88eaa4d7507b356968f"
TELEGRAM_BOT_TOKEN = "8475963022:AAF6Cd_XZau_pBgmUuQVPUc9DnRAmCChfmw"
CITY = "Saratov"
COUNTRY_CODE = "RU"

# Новый API для событий - TimePad
TIMEPAD_API_URL = "https://api.timepad.ru/v1/events"

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

async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "guide":
        query = update.callback_query
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=query.message.chat_id,
        text="Гид по городу Саратову позволит вам узнать о городе!")
        
async def random_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "random_event":
        query = update.callback_query
        await update.callback_query.answer()
        try:
            params = {
                'limit': 20,
                'cities': 'Саратов',
                'fields': 'name,description_short,starts_at,location,poster_image,url',
                'sort': '+starts_at'
            }
            
            headers = {
                'Authorization': 'Bearer 1afd1183be12d044663e1c7d5634e0ffa563e0ff'
            }
            
            response = requests.get(TIMEPAD_API_URL, params=params, headers=headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and data.get('values'):
                event = random.choice(data['values'])
                
                event_message = f"🎭 {event['name']}\n\n"
                if event.get('description_short'):
                    event_message += f"{event['description_short'][:300]}...\n\n"
                if event.get('starts_at'):
                    event_date = datetime.fromisoformat(event['starts_at'].replace('Z', '+00:00'))
                    event_message += f"📅 {event_date.strftime('%d.%m.%Y %H:%M')}\n"
                if event.get('location', {}).get('city'):
                    event_message += f"📍 {event['location']['city']}"
                    if event.get('location', {}).get('address'):
                        event_message += f", {event['location']['address']}\n"
                    else:
                        event_message += "\n"
                if event.get('url'):
                    event_message += f"🔗 {event['url']}"
                
                if event.get('poster_image'):
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=event['poster_image']['default_url'],
                        caption=event_message
                    )
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=event_message
                    )
            else:
                await context.bot.send_message(chat_id=query.message.chat_id,
                                               text="❗ Не найдено событий в городе Саратов.")
        except Exception as e:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Произошла ошибка при получении событий: {str(e)}"
            )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Погода в Саратове", callback_data="conditions")],
        [InlineKeyboardButton("Гид по городу", callback_data="guide")],
        [InlineKeyboardButton("Случайное событие", callback_data="random_event")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = "👋 Добро пожаловать в Саратовский Гулливер!\n\n"
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
    app.add_handler(CallbackQueryHandler(guide, pattern="^guide$"))
    app.add_handler(CallbackQueryHandler(random_event, pattern="^random_event$"))
    
    print("Бот запущен! Используйте /start для начала")
    app.run_polling()

if __name__ == "__main__":
    main()
