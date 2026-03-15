import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from datetime import datetime
import json

from config import Config
from database import Database
from ai_analyzer import GiftAnalyzer

logging.basicConfig(level=logging.INFO)

class GiftTraderBot:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(token=self.config.BOT_TOKEN)
        self.dp = Dispatcher()
        self.db = Database(self.config.DATABASE_URL)
        self.analyzer = GiftAnalyzer(self.config.OPENAI_API_KEY)
        
        # Регистрируем хендлеры
        self.setup_handlers()
        
    def setup_handlers(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            user = message.from_user
            await self.db.add_user(
                telegram_id=user.id,
                username=user.username
            )
            
            # Создаем клавиатуру с WebApp
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🚀 Открыть биржу",
                        web_app=WebAppInfo(url=f"{self.config.APP_URL}/app")
                    )],
                    [InlineKeyboardButton(
                        text="🤖 AI Анализ",
                        callback_data="ai_analysis"
                    )],
                    [InlineKeyboardButton(
                        text="📊 Моя статистика",
                        callback_data="stats"
                    )]
                ]
            )
            
            await message.answer(
                f"👋 Привет, {user.first_name}!\n\n"
                "🎁 Добро пожаловать в Glass Trade — умную биржу подарков Telegram.\n\n"
                "📱 Нажми кнопку ниже, чтобы открыть торговый терминал.\n"
                "🤖 ИИ поможет найти самые выгодные сделки!",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        @self.dp.callback_query(lambda c: c.data == "ai_analysis")
        async def ai_analysis(callback: CallbackQuery):
            await callback.answer("🤖 ИИ анализирует рынок...")
            
            # Получаем данные пользователя
            user = await self.db.get_user(callback.from_user.id)
            user_gifts = await self.db.get_user_gifts(user.id)
            
            # Получаем рыночные данные (заглушка)
            market_data = await self.db.get_active_offers()
            
            # ИИ анализирует
            recommendations = await self.analyzer.analyze_market_trends(market_data)
            
            if not recommendations:
                await callback.message.edit_text(
                    "😕 Пока нет данных для анализа. Попробуй позже.",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[
                            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
                        ]]
                    )
                )
                return
            
            # Формируем ответ
            text = "🤖 <b>AI Анализ рынка</b>\n\n"
            text += "📈 <b>Топ выгодных предложений:</b>\n\n"
            
            for i, rec in enumerate(recommendations[:5], 1):
                text += f"{i}. {rec.get('gift_name')}\n"
                text += f"   💰 Купить: {rec.get('buy_price')} ⭐\n"
                text += f"   💎 Продать: {rec.get('predicted_sell_price')} ⭐\n"
                text += f"   📊 Прибыль: +{rec.get('profit_percent')}%\n"
                text += f"   🤔 {rec.get('reasoning')}\n\n"
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Обновить анализ", callback_data="ai_analysis")],
                    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
                ]
            )
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        
        @self.dp.callback_query(lambda c: c.data == "stats")
        async def show_stats(callback: CallbackQuery):
            user = await self.db.get_user(callback.from_user.id)
            gifts = await self.db.get_user_gifts(user.id)
            transactions = await self.db.get_user_transactions(user.id)
            
            total_spent = sum(t.amount for t in transactions if t.type == 'buy')
            total_earned = sum(t.amount for t in transactions if t.type == 'sell')
            profit = total_earned - total_spent
            
            text = f"📊 <b>Ваша статистика</b>\n\n"
            text += f"👤 Пользователь: @{user.username}\n"
            text += f"💎 Баланс звёзд: {user.stars_balance} ⭐\n"
            text += f"🎁 Подарков: {len(gifts)}\n"
            text += f"💰 Всего потрачено: {total_spent} ⭐\n"
            text += f"💵 Всего заработано: {total_earned} ⭐\n"
            text += f"📈 Чистая прибыль: {profit} ⭐\n"
            
            if profit > 0:
                text += f"📊 ROI: +{round(profit/total_spent*100 if total_spent else 0)}%\n"
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
                ]]
            )
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        
        @self.dp.callback_query(lambda c: c.data == "back_to_menu")
        async def back_to_menu(callback: CallbackQuery):
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🚀 Открыть биржу",
                        web_app=WebAppInfo(url=f"{self.config.APP_URL}/app")
                    )],
                    [InlineKeyboardButton(
                        text="🤖 AI Анализ",
                        callback_data="ai_analysis"
                    )],
                    [InlineKeyboardButton(
                        text="📊 Моя статистика",
                        callback_data="stats"
                    )]
                ]
            )
            
            await callback.message.edit_text(
                "🎁 <b>Glass Trade</b> — умная биржа подарков\n\n"
                "Выбери действие:",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        # WebApp Data Handler
        @self.dp.message(lambda message: message.web_app_data)
        async def web_app_handler(message: Message):
            data = json.loads(message.web_app_data.data)
            action = data.get('action')
            
            if action == 'sell_gift':
                gift_id = data.get('gift_id')
                # Обрабатываем продажу
                result = await self.process_sale(message.from_user.id, gift_id)
                await message.answer(result)
                
            elif action == 'buy_gift':
                offer_id = data.get('offer_id')
                # Обрабатываем покупку
                result = await self.process_purchase(message.from_user.id, offer_id)
                await message.answer(result)
                
            elif action == 'sync_gifts':
                # Синхронизация подарков с аккаунтом Telegram
                await self.sync_user_gifts(message.from_user.id)
                await message.answer("✅ Подарки синхронизированы!")
    
    async def process_sale(self, user_id: int, gift_id: str):
        # Здесь логика продажи через Telegram API
        user = await self.db.get_user(user_id)
        gift = await self.db.get_gift(gift_id)
        
        if not gift or gift.user_id != user.id:
            return "❌ Подарок не найден"
        
        # TODO: Реальная продажа через Telegram API
        # Сейчас просто симуляция
        
        user.stars_balance += gift.price
        gift.is_sold = True
        gift.sold_at = datetime.utcnow()
        
        await self.db.commit()
        
        return f"✅ Подарок {gift.name} продан за {gift.price} ⭐"
    
    async def process_purchase(self, user_id: int, offer_id: str):
        # Здесь логика покупки
        user = await self.db.get_user(user_id)
        offer = await self.db.get_offer(offer_id)
        
        if not offer:
            return "❌ Предложение не найдено"
        
        if user.stars_balance < offer.buy_price:
            return "❌ Недостаточно звёзд"
        
        # TODO: Реальная покупка через Telegram API
        
        user.stars_balance -= offer.buy_price
        
        # Создаём новый подарок
        new_gift = Gift(
            user_id=user.id,
            gift_id=f"gift_{datetime.utcnow().timestamp()}",
            name=offer.gift_name,
            price=offer.predicted_sell_price,
            icon=offer.gift_icon
        )
        
        await self.db.add_gift(new_gift)
        
        return f"✅ Подарок {offer.gift_name} куплен за {offer.buy_price} ⭐"
    
    async def sync_user_gifts(self, user_id: int):
        """
        Синхронизация подарков с аккаунтом Telegram
        """
        # TODO: Реальная синхронизация через Telegram API
        # Сейчас просто заглушка
        pass
    
    async def run(self):
        await self.db.init()
        await self.dp.start_polling(self.bot)

if __name__ == "__main__":
    bot = GiftTraderBot()
    asyncio.run(bot.run())
