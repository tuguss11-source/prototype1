import asyncio
import websocket
import json
import logging
from threading import Thread
import pandas as pd
from config.settings import Settings
from config.database import DatabaseHandler, MarketData, Trade

logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self):
        self.settings = Settings()
        self.db = DatabaseHandler()
        self.ws = None
        self.is_connected = False
        self.data_buffer = {}
        
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if 'k' in data:
                kline = data['k']
                symbol = kline['s']
                close_price = float(kline['c'])
                high_price = float(kline['h'])
                low_price = float(kline['l'])
                open_price = float(kline['o'])
                volume = float(kline['v'])
                
                market_data = {
                    'symbol': symbol,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                }
                
                self.db.save_market_data(symbol, market_data)
                logger.debug(f"WebSocket data: {symbol} - {close_price}")
                
        except Exception as e:
            logger.error(f"WebSocket message error: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket connection closed")
        self.is_connected = False
    
    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        self.is_connected = True
        
        for symbol in self.settings.trading.symbols:
            stream_name = f"{symbol.lower().replace('/', '')}@kline_1m"
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [stream_name],
                "id": 1
            }
            ws.send(json.dumps(subscribe_message))
            logger.info(f"Subscribed to: {stream_name}")
    
    def connect(self):
        try:
            self.ws = websocket.WebSocketApp(
                self.settings.api.websocket_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            def run_ws():
                self.ws.run_forever()
            
            ws_thread = Thread(target=run_ws)
            ws_thread.daemon = True
            ws_thread.start()
            
            logger.info("WebSocket client started")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.ws:
            self.ws.close()
            self.is_connected = False
            logger.info("WebSocket disconnected")

class RealTimeDataCollector:
    def __init__(self):
        self.settings = Settings()
        self.ws_client = WebSocketClient()
        self.data_cache = {}
        
    async def start(self):
        logger.info("Starting real-time data collection...")
        return self.ws_client.connect()
    
    async def stop(self):
        self.ws_client.disconnect()
        logger.info("Real-time data collection stopped")
    
    async def get_current_prices(self):
        prices = {}
        session = self.ws_client.db.get_session()
        try:
            for symbol in self.settings.trading.symbols:
                latest_data = session.query(MarketData).filter(
                    MarketData.symbol == symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    prices[symbol] = latest_data.close_price
            return prices
        finally:
            session.close()

