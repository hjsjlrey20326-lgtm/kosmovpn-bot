# bot.py — Telegram бот для продажи подписок KosmoVPN
# Бесплатный хостинг: Railway / Render / PythonAnywhere

import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
import hashlib

# Конфигурация
TOKEN = "8756799246:AAFUKXPb-SFoycVdMbLc4E0hbOW_MdC9clE"  # Замени на токен от @BotFather
ADMIN_ID = 8688518887  # Твой Telegram ID (найти у @userinfobot)
SUBSCRIPTION_URL = "https://raspy-resonance-c3cf.hjsjlrey20326.workers.dev/sub"  # Твоя подписка
PRICE_DAY = 3      # Цена за день в рублях
PRICE_MONTH = 50   # Цена за месяц
PRICE_YEAR = 500   # Цена за год

bot = telebot.TeleBot(TOKEN)

# База данных (простой JSON файл)
DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, 'w') as f:
        json.dump(users, f)

def generate_subscription_link(user_id, duration_days):
    """Генерируем уникальную ссылку с привязкой к пользователю"""
    # Простой вариант: возвращаем общую подписку
    # Продвинутый: добавить параметр ?token=... и проверять на воркере
    return SUBSCRIPTION_URL

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    users = load_users()
    
    if str(user_id) not in users:
        users[str(user_id)] = {"expires": 0, "created": time.time()}
        save_users(users)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 День (3₽)", callback_data="buy_day"),
        InlineKeyboardButton("📱 Месяц (50₽)", callback_data="buy_month"),
        InlineKeyboardButton("📱 Год (500₽)", callback_data="buy_year"),
        InlineKeyboardButton("📋 Моя подписка", callback_data="my_sub"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    
    bot.send_message(
        user_id,
        "💎 **KosmoVPN**\n\n"
        "Меньше ms — лучше, n/a — не работает.\n\n"
        "Выбери тариф:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    users = load_users()
    
    if call.data == "buy_day":
        bot.answer_callback_query(call.id, "Оплата: 3₽") # Здесь нужна интеграция с платежами
        bot.send_message(user_id, "Для оплаты переведите 3₽ на карту 0000 0000 0000 0000\nПосле оплаты пришлите скриншот и команду /confirm")
    
    elif call.data == "buy_month":
        bot.answer_callback_query(call.id, "Оплата: 50₽")
        bot.send_message(user_id, "Для оплаты переведите 50₽ на карту 0000 0000 0000 0000\nПосле оплаты пришлите скриншот и команду /confirm")
    
    elif call.data == "buy_year":
        bot.answer_callback_query(call.id, "Оплата: 500₽")
        bot.send_message(user_id, "Для оплаты переведите 500₽ на карту 0000 0000 0000 0000\nПосле оплаты пришлите скриншот и команду /confirm")
    
    elif call.data == "my_sub":
        user_data = users.get(str(user_id), {})
        expires = user_data.get("expires", 0)
        if expires > time.time():
            days_left = int((expires - time.time()) / 86400)
            bot.send_message(
                user_id,
                f"📋 **Ваша подписка**\n"
                f"Ссылка: `{SUBSCRIPTION_URL}`\n"
                f"Дней осталось: {days_left}\n\n"
                f"Добавьте эту ссылку в приложение (Sing-Box, v2rayNG, NekoBox, happ) как подписку.",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(user_id, "❌ У вас нет активной подписки. Выберите тариф: /start")
    
    elif call.data == "help":
        bot.send_message(
            user_id,
            "❓ **Помощь**\n\n"
            "1. Выберите тариф\n"
            "2. Оплатите на карту\n"
            "3. Пришлите скриншот оплаты сюда\n"
            "4. Администратор подтвердит и выдаст доступ\n\n"
            "**Приложения:**\n"
            "- Android: v2rayNG, NekoBox\n"
            "- iOS: Sing-Box, Shadowrocket\n"
            "- Windows: v2rayN\n\n"
            "**Подписка:** `" + SUBSCRIPTION_URL + "`\n\n"
            "По всем вопросам: @godSof",
            parse_mode="Markdown"
        )

# Команда /confirm (для админа)
@bot.message_handler(commands=['confirm'])
def confirm_payment(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Нет доступа")
        return
    
    # Ожидает ответ с user_id и днями
    # Пример: /confirm 123456789 30
    try:
        _, user_id_str, days_str = message.text.split()
        user_id = int(user_id_str)
        days = int(days_str)
        
        users = load_users()
        if str(user_id) not in users:
            users[str(user_id)] = {}
        
        current_expires = users[str(user_id)].get("expires", 0)
        new_expires = max(current_expires, time.time()) + days * 86400
        users[str(user_id)]["expires"] = new_expires
        save_users(users)
        
        bot.send_message(user_id, f"✅ Подписка активирована на {days} дней!\nСсылка: {SUBSCRIPTION_URL}")
        bot.reply_to(message, f"✅ Пользователю {user_id} активировано {days} дней")
    except:
        bot.reply_to(message, "❌ Формат: /confirm user_id дни")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()