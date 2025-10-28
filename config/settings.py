import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    dialect: str = "sqlite"
    database: str = "trading.db"
    host: str = "localhost"
    port: int = 5432
    username: str = "trader"
    password: str = "password"

@dataclass
class TradingConfig:
    # Risk yönetimi
    max_position_size: float = 0.1  # Toplam portföyün %10'u
    stop_loss_pct: float = 0.02    # %2 stop loss
    take_profit_pct: float = 0.05  # %5 take profit
    trailing_stop: bool = True
    
    # Trading parametreleri
    update_interval: int = 60      # Saniye
    leverage: int = 1
    
    # Semboller
    symbols: list = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]

@dataclass
class APIConfig:
    # Exchange API bilgileri (environment variables'tan alınacak)
    binance_api_key: str = ""
    binance_secret: str = ""
    websocket_url: str = "wss://stream.binance.com:9443/ws"
    
    def __post_init__(self):
        self.binance_api_key = os.getenv("BINANCE_API_KEY", "")
        self.binance_secret = os.getenv("BINANCE_SECRET", "")

class Settings:
    def __init__(self):
        self.database = DatabaseConfig()
        self.trading = TradingConfig()
        self.api = APIConfig()
        self.debug: bool = True
        
    def get_db_url(self) -> str:
        if self.database.dialect == "sqlite":
            return f"sqlite:///{self.database.database}"
        else:
            return f"postgresql://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.database}"
