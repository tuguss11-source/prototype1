import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from deepseek.analyzer import DeepSeekAnalyzer
from strategies.strategy_manager import StrategyManager
from data.data_fetcher import DataFetcher

class PortfolioManager:
    def __init__(self, api_key: str = None):
        self.logger = self._setup_logger()
        self.api_key = api_key
        self.deepseek_analyzer = None
        self.strategy_manager = StrategyManager()
        self.data_fetcher = DataFetcher()
        self.portfolio = {}
        
        # API key varsa analyzer'ı başlat
        if self.api_key or os.environ.get("DEEPSEEK_API_KEY"):
            try:
                self.deepseek_analyzer = DeepSeekAnalyzer(api_key=self.api_key)
            except Exception as e:
                self.logger.warning(f"DeepSeek analyzer başlatılamadı: {e}")
        
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/portfolio_manager.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def add_to_portfolio(self, symbol: str, average_buy_price: float, position_size: float):
        """
        Portföye coin ekle
        """
        self.portfolio[symbol] = {
            'average_buy_price': average_buy_price,
            'position_size': position_size,
            'added_date': datetime.now(),
            'current_price': None,
            'pnl_percentage': 0
        }
        self.logger.info(f"Portföye eklendi: {symbol}")
    
    def analyze_portfolio(self) -> Dict[str, Any]:
        """
        Portföyü DeepSeek ile analiz et
        """
        if not self.deepseek_analyzer:
            raise ValueError("DeepSeek analyzer başlatılamadı. API key gerekli.")
        
        if not self.portfolio:
            return {"error": "Portföy boş"}
        
        results = {}
        
        for symbol in self.portfolio.keys():
            try:
                # Güncel verileri al
                current_data = self.data_fetcher.get_historical_data(symbol, "1h", 200)
                if current_data.empty:
                    continue
                
                current_price = current_data['close'].iloc[-1]
                
                # Strateji analizi
                strategies_results = self.strategy_manager.analyze_symbol(symbol, current_data)
                
                # Portföy verilerini güncelle
                self.portfolio[symbol]['current_price'] = current_price
                avg_price = self.portfolio[symbol]['average_buy_price']
                self.portfolio[symbol]['pnl_percentage'] = ((current_price - avg_price) / avg_price) * 100
                
                # DeepSeek analizi
                portfolio_data = {
                    'average_buy_price': avg_price,
                    'current_position': self.portfolio[symbol]['position_size'],
                    'pnl_percentage': self.portfolio[symbol]['pnl_percentage']
                }
                
                analysis = self.deepseek_analyzer.analyze_trading_signals(
                    symbol, strategies_results, current_price
                )
                
                self.portfolio[symbol]['analysis'] = analysis
                results[symbol] = analysis
                
            except Exception as e:
                self.logger.error(f"Portföy analiz hatası ({symbol}): {e}")
                results[symbol] = {"error": str(e)}
        
        return results
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Portföy özeti
        """
        total_investment = 0
        total_current_value = 0
        
        for symbol, data in self.portfolio.items():
            investment = data['average_buy_price'] * data['position_size']
            current_value = data.get('current_price', data['average_buy_price']) * data['position_size']
            
            total_investment += investment
            total_current_value += current_value
        
        total_pnl = total_current_value - total_investment
        total_pnl_percentage = (total_pnl / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            "total_investment": total_investment,
            "total_current_value": total_current_value,
            "total_pnl": total_pnl,
            "total_pnl_percentage": total_pnl_percentage,
            "number_of_coins": len(self.portfolio)
        }
    
    def remove_from_portfolio(self, symbol: str):
        """
        Portföyden coin çıkar
        """
        if symbol in self.portfolio:
            del self.portfolio[symbol]
            self.logger.info(f"Portföyden çıkarıldı: {symbol}")
    
    def save_portfolio(self, filename: str = "portfolio.json"):
        """
        Portföyü kaydet
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.portfolio, f, indent=4, default=str)
            self.logger.info(f"Portföy kaydedildi: {filename}")
        except Exception as e:
            self.logger.error(f"Portföy kaydetme hatası: {e}")
    
    def load_portfolio(self, filename: str = "portfolio.json"):
        """
        Portföyü yükle
        """
        try:
            with open(filename, 'r') as f:
                self.portfolio = json.load(f)
            self.logger.info(f"Portföy yüklendi: {filename}")
        except Exception as e:
            self.logger.error(f"Portföy yükleme hatası: {e}")