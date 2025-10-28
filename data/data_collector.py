import asyncio
import pandas as pd
import ccxt
from websocket import create_connection
import logging
from config.settings import Settings

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.settings = Settings()
        self.exchange = ccxt.binance({
            'apiKey': self.settings.api.binance_api_key,
            'secret': self.settings.api.binance_secret,
            'enableRateLimit': True
        })
        
    async def get_real_time_data(self, symbol="BTC/USDT", timeframe="1m", limit=100):
        """Gerçek zamanlı veri al"""
        try:
            # OHLCV verilerini al
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            logger.info(f"{symbol} verisi alındı: {len(df)} bar")
            return df
            
        except Exception as e:
            logger.error(f"Veri alım hatası: {e}")
            return pd.DataFrame()
    
    async def get_multiple_symbols_data(self):
        """Birden fazla sembol için veri al"""
        tasks = []
        for symbol in self.settings.trading.symbols:
            task = self.get_real_time_data(symbol)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(self.settings.trading.symbols, results))
