import websocket
import json
import threading
import time
from datetime import datetime
import logging
from typing import Dict, List, Optional
import ccxt
import pandas as pd

class DataFetcher:
    def __init__(self):
        self.logger = self._setup_logger()
        self.binance = ccxt.binance()
        self.real_time_data = {}
        self.historical_data = {}
        self.ws_connections = {}
        self.symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
        self.is_running = False
        
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_fetcher.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_historical_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        try:
            self.logger.info(f"{symbol} için tarihsel veri çekiliyor...")
            
            ohlcv = self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            self.historical_data[symbol] = df
            self.logger.info(f"{symbol} için {len(df)} bar veri çekildi")
            return df
            
        except Exception as e:
            self.logger.error(f"Tarihsel veri çekme hatası ({symbol}): {e}")
            return pd.DataFrame()
    
    def get_multiple_symbols_data(self, symbols: List[str], timeframe: str = '1h', limit: int = 100) -> Dict[str, pd.DataFrame]:
        data = {}
        for symbol in symbols:
            df = self.get_historical_data(symbol, timeframe, limit)
            if not df.empty:
                data[symbol] = df
            time.sleep(0.1)
        return data

    def start_real_time_data(self, symbols: List[str]):
        self.logger.info("Real-time veri akışı başlatılıyor...")
        self.is_running = True
        
        for symbol in symbols:
            thread = threading.Thread(target=self._start_individual_websocket, args=(symbol,))
            thread.daemon = True
            thread.start()
            time.sleep(0.5)
    
    def _start_individual_websocket(self, symbol: str):
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                if 'e' in data and data['e'] == '24hrTicker':
                    tick_data = {
                        'symbol': data['s'],
                        'price': float(data['c']),
                        'timestamp': datetime.now(),
                        'change_percent': float(data['P']),
                        'high_24h': float(data['h']),
                        'low_24h': float(data['l']),
                        'volume': float(data['v']),
                        'price_change': float(data['p'])
                    }
                    
                    self.real_time_data[symbol] = tick_data
                    self.logger.debug(f"Real-time {symbol}: {tick_data['price']}")
                    
            except Exception as e:
                self.logger.error(f"WebSocket mesaj işleme hatası ({symbol}): {e}")
        
        def on_error(ws, error):
            self.logger.error(f"WebSocket hatası ({symbol}): {error}")
        
        def on_close(ws, close_status_code, close_msg):
            self.logger.warning(f"WebSocket bağlantısı kapandı ({symbol})")
            if self.is_running:
                time.sleep(5)
                self._start_individual_websocket(symbol)
        
        def on_open(ws):
            self.logger.info(f"WebSocket bağlantısı açıldı ({symbol})")
        
        stream_url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@ticker"
        
        ws = websocket.WebSocketApp(
            stream_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws_connections[symbol] = ws
        
        while self.is_running:
            try:
                ws.run_forever()
            except Exception as e:
                self.logger.error(f"WebSocket çalıştırma hatası ({symbol}): {e}")
                time.sleep(5)
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        if symbol in self.real_time_data:
            return self.real_time_data[symbol]['price']
        return None
    
    def get_24h_stats(self, symbol: str) -> Dict:
        try:
            ticker = self.binance.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price_change': ticker.get('percentage', 0),
                'high_24h': ticker.get('high'),
                'low_24h': ticker.get('low'),
                'volume': ticker.get('baseVolume'),
                'last_price': ticker.get('last')
            }
        except Exception as e:
            self.logger.error(f"24h stats hatası ({symbol}): {e}")
            return {}
    
    def stop_all_connections(self):
        self.is_running = False
        for symbol, ws in self.ws_connections.items():
            try:
                ws.close()
                self.logger.info(f"WebSocket bağlantısı kapatıldı ({symbol})")
            except Exception as e:
                self.logger.error(f"WebSocket kapatma hatası ({symbol}): {e}")