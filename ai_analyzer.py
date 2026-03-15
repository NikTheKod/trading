import openai
from typing import List, Dict
import json
import asyncio
from datetime import datetime, timedelta

class GiftAnalyzer:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
    async def analyze_market_trends(self, market_data: List[Dict]) -> List[Dict]:
        """
        Анализирует рыночные тренды и возвращает рекомендации
        """
        prompt = f"""
        Ты эксперт по торговле подарками в Telegram. 
        Проанализируй эти данные о подарках и определи самые выгодные для покупки:
        
        {json.dumps(market_data, indent=2, ensure_ascii=False)}
        
        Верни JSON массив с 5 самыми выгодными предложениями, где каждый объект содержит:
        - gift_name: название подарка
        - buy_price: цена покупки
        - predicted_sell_price: предсказанная цена продажи
        - profit_percent: процент прибыли
        - confidence: твоя уверенность (0-1)
        - reasoning: краткое объяснение почему выгодно
        
        Учитывай: редкость, спрос, сезонность, тренды.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Ты аналитик рынка подарков Telegram. Отвечай только валидным JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("offers", [])
            
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return []
    
    async def get_buy_recommendations(self, user_balance: int, user_gifts: List[Dict]) -> List[Dict]:
        """
        Персональные рекомендации для пользователя
        """
        prompt = f"""
        У пользователя {user_balance} звёзд и такие подарки:
        {json.dumps(user_gifts, indent=2, ensure_ascii=False)}
        
        Какие подарки ему стоит купить для перепродажи?
        Учти его бюджет и текущую коллекцию.
        
        Верни JSON массив из 3 рекомендаций с полями:
        - gift_name
        - reason
        - estimated_profit
        - risk_level (low/medium/high)
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Ты персональный финансовый советник по подаркам."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Recommendation Error: {e}")
            return []
    
    async def get_sell_timing(self, gift_name: str, current_price: int) -> Dict:
        """
        Определяет лучшее время для продажи
        """
        prompt = f"""
        Подарок: {gift_name}
        Текущая цена: {current_price} звёзд
        
        Когда лучше продать этот подарок?
        Учти сезонность, праздники, тренды.
        
        Ответь JSON с полями:
        - recommendation: sell_now / wait
        - wait_days: если ждать, то сколько дней
        - predicted_price: предсказанная цена
        - reason: объяснение
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Ты эксперт по таймингу продаж."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Timing Error: {e}")
            return {"recommendation": "sell_now", "reason": "Ошибка анализа"}
