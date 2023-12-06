import telebot
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = 'BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

cities = {"Дрогобич": "дрогобич", "Львів": "львів", "Стрий": "стрий"}
weather_options = ["Today", "Tomorrow", "After tomorrow"]

user_data = {}  # To store user context

@bot.message_handler(commands=['start'])
def start(message):
    markup = build_cities_keyboard()
    bot.send_message(message.chat.id, "Welcome! Choose a city:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data in cities:
        user_data[user_id] = {"city": cities[call.data]}
        city = call.data
        markup = build_weather_keyboard()
        bot.edit_message_text(f"You selected {city}. Choose an option for the weather:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data in weather_options:
        option = call.data
        user_city = user_data.get(user_id, {}).get("city", "")
        if user_city:
            weather_info = get_weather_info(user_city, option)
            bot.send_message(chat_id, weather_info)
        else:
            bot.send_message(chat_id, "Error: City not found in user data.")

def build_cities_keyboard():
    markup = InlineKeyboardMarkup()
    for city in cities:
        markup.add(InlineKeyboardButton(city, callback_data=city))
    return markup

def build_weather_keyboard():
    markup = InlineKeyboardMarkup()
    for option in weather_options:
        markup.add(InlineKeyboardButton(option, callback_data=option))
    return markup

def get_weather_info(city, option):
    try:
        url = f'https://ua.sinoptik.ua/погода-{city}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        temperature = soup.find("p", class_="today-temp").text.strip()

        min_temperature = max_temperature = "N/A"

        if option == 'Today':
            main_div = soup.find('div', class_='main loaded')
        elif option == 'Tomorrow':
            main_div = soup.find('div', class_='bd2')
        elif option == 'After tomorrow':
            main_div = soup.find('div', class_='bd3')

        if main_div:
            # Extract min/max temperature information
            min_temperature = main_div.find('div', class_='temperature').find('div', class_='min').span.text.strip()
            max_temperature = main_div.find('div', class_='temperature').find('div', class_='max').span.text.strip()

        return f"Weather in {city} on {option}:\n" \
               f"Temperature (This day): {temperature}\n" \
               f"Min Temperature per day {option}: {min_temperature}\n" \
               f"Max Temperature per day {option}: {max_temperature}\n"
    except Exception as e:
        return f"Error fetching weather information: {str(e)}"

if __name__ == "__main__":
    bot.polling(none_stop=True)


