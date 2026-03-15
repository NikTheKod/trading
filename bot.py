#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from datetime import datetime
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Простая конфигурация без сложных зависимостей для начала
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
APP_URL = os.getenv("APP_URL", "https://your-app.railway.app")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN не установлен!")
    sys.exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище (потом заменим на БД)
users = {}
gifts = {}
market_offers = [
    {"id": 1, "name": "Наушники", "price": 890, "profit": 15, "icon": "🎧"},
    {"id": 2, "name": "Камера Insta", "price": 3200, "profit": 22, "icon": "📸"},
    {"id": 3, "name": "Мишка Ltd", "price": 2750, "profit": 9, "icon": "🧸"},
    {"id": 4, "name": "Watch Pro", "price": 6100, "profit": 31, "icon": "⌚"},
    {"id": 5, "name": "Игровая приставка", "price": 15300, "profit": 18, "icon": "🎮"}
]

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    users[user.id] = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "stars": 10000,  # Стартовый баланс
        "gifts": []
    }
    
    # Добавляем тестовые подарки
    users[user.id]["gifts"] = [
        {"id": 1, "name": "Плюшевый мишка", "price": 1200, "icon": "🧸"},
        {"id": 2, "name": "Элитные часы", "price": 4900, "icon": "⌚"},
        {"id": 3, "name": "Смартфон X", "price": 8200, "icon": "📱"}
    ]
    
    logger.info(f"Новый пользователь: {user.id} - {user.username}")
    
    # Клавиатура с WebApp
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть биржу",
                web_app=WebAppInfo(url=f"{APP_URL}")
            )],
            [InlineKeyboardButton(
                text="📊 Мои подарки",
                callback_data="my_gifts"
            )],
            [InlineKeyboardButton(
                text="💰 Баланс",
                callback_data="balance"
            )]
        ]
    )
    
    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        f"🎁 Добро пожаловать в Glass Trade!\n"
        f"💎 Твой баланс: {users[user.id]['stars']} ⭐\n\n"
        f"📱 Нажми кнопку ниже, чтобы открыть торговый терминал.",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "my_gifts")
async def show_my_gifts(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer("Сначала нажми /start")
        return
    
    user_gifts = users[user_id]["gifts"]
    
    if not user_gifts:
        await callback.message.edit_text(
            "🎁 У тебя пока нет подарков.\n"
            "Зайди в биржу и купи что-нибудь!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
                ]]
            )
        )
        return
    
    text = "🎁 <b>Твои подарки:</b>\n\n"
    for gift in user_gifts:
        text += f"{gift['icon']} {gift['name']} — {gift['price']} ⭐\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
            ]]
        ),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data == "balance")
async def show_balance(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer("Сначала нажми /start")
        return
    
    user = users[user_id]
    
    text = f"💰 <b>Твой баланс</b>\n\n"
    text += f"💎 Звёзды: {user['stars']} ⭐\n"
    text += f"🎁 Подарков: {len(user['gifts'])}\n"
    
    total_value = sum(g['price'] for g in user['gifts'])
    text += f"📦 Стоимость подарков: {total_value} ⭐\n"
    text += f"💵 Общий капитал: {user['stars'] + total_value} ⭐"
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
            ]]
        ),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer("Сначала нажми /start")
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть биржу",
                web_app=WebAppInfo(url=f"{APP_URL}")
            )],
            [InlineKeyboardButton(
                text="📊 Мои подарки",
                callback_data="my_gifts"
            )],
            [InlineKeyboardButton(
                text="💰 Баланс",
                callback_data="balance"
            )]
        ]
    )
    
    await callback.message.edit_text(
        f"👋 С возвращением!\n\n"
        f"💎 Твой баланс: {users[user_id]['stars']} ⭐\n"
        f"🎁 Подарков: {len(users[user_id]['gifts'])}\n\n"
        f"Выбери действие:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.web_app_data)
async def web_app_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        user_id = message.from_user.id
        
        logger.info(f"WebApp data from {user_id}: {data}")
        
        if user_id not in users:
            users[user_id] = {
                "id": user_id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "stars": 10000,
                "gifts": []
            }
        
        if action == 'sell_gift':
            gift_id = data.get('gift_id')
            # Находим подарок
            gift = next((g for g in users[user_id]['gifts'] if g['id'] == gift_id), None)
            
            if gift:
                users[user_id]['stars'] += gift['price']
                users[user_id]['gifts'] = [g for g in users[user_id]['gifts'] if g['id'] != gift_id]
                await message.answer(f"✅ Подарок {gift['name']} продан за {gift['price']} ⭐")
            else:
                await message.answer("❌ Подарок не найден")
                
        elif action == 'buy_gift':
            offer_id = data.get('offer_id')
            offer = next((o for o in market_offers if o['id'] == offer_id), None)
            
            if offer:
                if users[user_id]['stars'] >= offer['price']:
                    users[user_id]['stars'] -= offer['price']
                    new_gift = {
                        "id": len(users[user_id]['gifts']) + 1,
                        "name": offer['name'],
                        "price": offer['price'] + (offer['price'] * offer['profit'] // 100),
                        "icon": offer['icon']
                    }
                    users[user_id]['gifts'].append(new_gift)
                    await message.answer(f"✅ Подарок {offer['name']} куплен за {offer['price']} ⭐")
                else:
                    await message.answer(f"❌ Недостаточно звёзд! Нужно {offer['price']} ⭐")
            else:
                await message.answer("❌ Предложение не найдено")
                
        elif action == 'get_data':
            # Отправляем данные пользователя в мини-апп
            user_data = {
                "stars": users[user_id]['stars'],
                "gifts": users[user_id]['gifts'],
                "offers": market_offers
            }
            await message.answer(json.dumps(user_data))
            
    except Exception as e:
        logger.error(f"Error in web_app_handler: {e}")
        await message.answer("❌ Произошла ошибка")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
<b>🤖 Glass Trade — Помощь</b>

<b>Команды:</b>
/start - Запустить бота
/help - Показать это сообщение
/balance - Проверить баланс
/gifts - Мои подарки
/market - Рыночные предложения

<b>Как торговать:</b>
1️⃣ Нажми "Открыть биржу"
2️⃣ Выбирай подарки для покупки/продажи
3️⃣ Следи за прибылью

<b>🎯 Советы:</b>
• Покупай дешево, продавай дорого
• Следи за трендами
• Используй анализ рынка
    """
    
    await message.answer(help_text, parse_mode=ParseMode.HTML)

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала нажми /start")
        return
    
    user = users[user_id]
    await message.answer(
        f"💰 <b>Твой баланс</b>\n\n"
        f"💎 Звёзды: {user['stars']} ⭐\n"
        f"🎁 Подарков: {len(user['gifts'])}",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("gifts"))
async def cmd_gifts(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала нажми /start")
        return
    
    gifts_list = users[user_id]['gifts']
    if not gifts_list:
        await message.answer("🎁 У тебя пока нет подарков")
        return
    
    text = "🎁 <b>Твои подарки:</b>\n\n"
    for gift in gifts_list:
        text += f"{gift['icon']} {gift['name']} — {gift['price']} ⭐\n"
    
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(Command("market"))
async def cmd_market(message: Message):
    text = "🏪 <b>Рыночные предложения:</b>\n\n"
    for offer in market_offers[:5]:
        text += f"{offer['icon']} {offer['name']}\n"
        text += f"   💰 Цена: {offer['price']} ⭐\n"
        text += f"   📈 Профит: +{offer['profit']}%\n\n"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🚀 Открыть биржу",
                web_app=WebAppInfo(url=f"{APP_URL}")
            )
        ]]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
