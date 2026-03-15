from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    stars_balance = Column(Integer, default=0)  # звёзды Telegram
    gifts_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)
    settings = Column(JSON, default={})  # настройки пользователя

class Gift(Base):
    __tablename__ = "gifts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gift_id = Column(String)  # ID подарка в Telegram
    name = Column(String)
    price = Column(Integer)  # стоимость в звёздах
    icon = Column(String)
    purchased_at = Column(DateTime, default=datetime.datetime.utcnow)
    sold_at = Column(DateTime, nullable=True)
    is_sold = Column(Boolean, default=False)
    
class MarketOffer(Base):
    __tablename__ = "market_offers"
    
    id = Column(Integer, primary_key=True)
    gift_name = Column(String)
    gift_icon = Column(String)
    buy_price = Column(Integer)  # цена покупки
    predicted_sell_price = Column(Integer)  # предсказанная цена продажи
    profit_percent = Column(Float)  # процент прибыли
    confidence = Column(Float)  # уверенность ИИ (0-1)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gift_id = Column(String)
    type = Column(String)  # buy / sell
    amount = Column(Integer)  # сумма в звёздах
    profit = Column(Integer, nullable=True)  # прибыль если продажа
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
