from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, KeyboardButton, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests
import random
import os
from datetime import datetime

# Настройки API - ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ КЛЮЧ!
OPENWEATHER_API_KEY = "a9490cc69b99d88eaa4d7507b356968f"  # ЗДЕСЬ ДОЛЖЕН БЫТЬ ВАШ КЛЮЧ OPENWEATHERMAP
GEOAPIFY_API_KEY = "f92ae83e459f4e329a1bc1e2ba69ed39"
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

async def geo_permission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query.data == "geopermission":
        query = update.callback_query

        keyboard = [[KeyboardButton("Моё местоположение", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await query.answer()
        await context.bot.send_message(chat_id=query.message.chat_id,
        text="Я могу найти для тебя много интересных мест, но для этого ты должен предоставить мне своё текущее местоположение",
        reply_markup=reply_markup)

def get_nearest_good_places(location, update, context):
    params = {
        "apiKey": GEOAPIFY_API_KEY,
        "filter": f"circle:{location.longitude},{location.latitude},2000",
        "categories": "tourism,entertainment,catering,religion,leisure,natural,office.travel_agent, office.coworking",
        "lang": "ru",
        "limit": 30
    }
    response = requests.get("https://api.geoapify.com/v2/places", params=params)
    return response.json()

def get_place_information(places):
    print(places)
    places_fin = []
    for place in places["features"]:
        properties = place["properties"]
        try:
            name = properties["name"]
            district = properties["district"]
            suburb = properties["suburb"]
            street = properties["street"]
            housenumber = properties["housenumber"]
            contact = properties["contact"]
        except:
            continue

        address_string = ", ".join([district, suburb, street, housenumber])
        place_string = "\n\t".join([name, address_string])
        places_fin.append(place_string)
    return places_fin

def check_repetition(places):
    tmp = None
    places_fin = []
    for place in places:
        if tmp == None:
            tmp = place
            places_fin.append(tmp)
            continue
        if place["name"] == tmp["name"]:
            continue
        places_fin.append(place)
        tmp = place

async def near_to_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    if location:
        await context.bot.send_message(chat_id=update.effective_chat.id,
        text="Спасибо за твоё доверие ко мне! Держи шикарный список близких к тебе мест:",
        reply_markup=ReplyKeyboardRemove())
        places = get_nearest_good_places(location, update, context)
        places = get_place_information(places)
        for i in range(len(places)+1):
            await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"Место {i+1}:\n\t{places[i-1]}")


async def gorpark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "gorpark":
        keyboard = [
            [InlineKeyboardButton("Меню", callback_data="start")],
            [InlineKeyboardButton("Дальше", callback_data="nabka")]
        ]
        query = update.callback_query
        await update.callback_query.answer()
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=query.message.chat_id,
        text="Гид по городу Саратову позволит вам узнать о городе!")

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://pp.vk.me/c628225/v628225107/26cd5/wAqYn5ApXOQ.jpg",
        caption="Подождите немного, видео загружается...")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="gorpark.mp4",
        caption="Горпарк это шикарное место",
		reply_markup=reply_markup)

async def nabka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "nabka":
        keyboard = [
            [InlineKeyboardButton("Меню", callback_data="start")],
            [InlineKeyboardButton("Назад", callback_data="gorpark"), InlineKeyboardButton("Дальше", callback_data="lipki")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://saratov.travel/upload/resize_cache/iblock/727/800_800_1/6kexsl38l39dqiqo8xvcyzhlk5oh3qit.jpg",
        caption="Подождите немного, видео загружается...")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="nabka.mp4",
        caption="А набережная это вообще отпад!",
        reply_markup=reply_markup)

async def lipki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "lipki":
        keyboard = [
            [InlineKeyboardButton("Меню", callback_data="start")],
            [InlineKeyboardButton("Назад", callback_data="nabka"), InlineKeyboardButton("Дальше", callback_data="utoli")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://img.tourister.ru/files/3/3/9/1/7/5/1/0/2/original.jpg",
        caption="Подождите немного, видео загружается...")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="lipki.mp4",
        caption="А липки это вообще отпад!",
        reply_markup=reply_markup)

async def utoli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "utoli":
        keyboard = [
            [InlineKeyboardButton("Меню", callback_data="start")],
            [InlineKeyboardButton("Назад", callback_data="lipki"), InlineKeyboardButton("Дальше", callback_data="conserva")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://cdn-imgproxy.mamado.su/7u7PXEMY0t4nQlCVI-XgWcDomrKi-dObs_pLLDpPVBA/rs:fit:2000:2000:1/g:ce/q:90/czM6Ly9tYW1hZG8t/YXBpLXByb2R1Y3Rp/b24vc3RvcmFnZS8x/Mjc3MTczL1NjcmVl/bnNob3RfMy5wbmc.webp",
        caption="Подождите немного, видео загружается...")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="utoli.mp4",
        caption="А утоли это вообще отпад!",
        reply_markup=reply_markup)

async def conserva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "conserva":
        keyboard = [
            [InlineKeyboardButton("Меню", callback_data="start")],
            [InlineKeyboardButton("Назад", callback_data="utoli"), InlineKeyboardButton("Дальше", callback_data="avenue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        await update.callback_query.answer()

        await context.bot.send_photo(chat_id=query.message.chat_id,
        photo="https://static.gorodzovet.ru/uploads/venue/venuelogo-2903106.jpg?v=",
        caption="Подождите немного, видео загружается...")
        await context.bot.send_video(chat_id=query.message.chat_id,
        video="conserva.mp4",
        caption="А консерватория это вообще отпад!",
        reply_markup=reply_markup)

async def avenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "avenue":
        keyboard = [
            [InlineKeyboardButton("Меню", callback_data="start")],
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
            [InlineKeyboardButton("Меню", callback_data="start")],
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
      [
        InlineKeyboardButton("Погода в Саратове", callback_data="conditions"),
        InlineKeyboardButton("Случайное событие", callback_data="random_event")
      ],
      [
        InlineKeyboardButton("Гид по городу", callback_data="gorpark"),
        InlineKeyboardButton("Что рядом?", callback_data="geopermission")
      ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = "👋 Добро пожаловать в Саратовский Гулливер!\n\n"
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def start_return(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query.data == "start":
        query = update.callback_query
        keyboard = [
            [
                InlineKeyboardButton("Погода в Саратове", callback_data="conditions"),
                InlineKeyboardButton("Случайное событие", callback_data="random_event")
            ],
            [
                InlineKeyboardButton("Гид по городу", callback_data="gorpark"),
                InlineKeyboardButton("Что рядом?", callback_data="geopermission")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_text = "👋 Добро пожаловать в главное меню!\n\n"
        await query.answer()
        await query.message.reply_text(welcome_text, reply_markup=reply_markup)

def main():
    print("Запуск бота...")
    print(f"Токен бота: {'установлен' if len(TELEGRAM_BOT_TOKEN) > 20 else 'не установлен'}")
    print(f"OpenWeather ключ: {'установлен' if OPENWEATHER_API_KEY not in ['ваш_ключ_openweathermap_здесь', 'your_openweather_api_key_here'] else 'НЕ УСТАНОВЛЕН!'}")
    
    # Создаем приложение
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(start_return, pattern="^start$"))
    
    app.add_handler(CallbackQueryHandler(weather, pattern="^conditions$"))
    app.add_handler(CallbackQueryHandler(random_event, pattern="^random_event$"))

    app.add_handler(CallbackQueryHandler(geo_permission, pattern="^geopermission$"))

    # Краткий гид
    app.add_handler(CallbackQueryHandler(gorpark, pattern="^gorpark$"))
    app.add_handler(CallbackQueryHandler(nabka, pattern="^nabka$"))
    app.add_handler(CallbackQueryHandler(lipki, pattern="^lipki$"))
    app.add_handler(CallbackQueryHandler(utoli, pattern="^utoli$"))
    app.add_handler(CallbackQueryHandler(conserva, pattern="^conserva$"))
    app.add_handler(CallbackQueryHandler(avenue, pattern="^avenue$"))
    app.add_handler(CallbackQueryHandler(circus, pattern="^circus$"))
    app.add_handler(MessageHandler(filters.LOCATION, near_to_me))

    print("Бот запущен! Используйте /start для начала")
    app.run_polling()

if __name__ == "__main__":
    main()
