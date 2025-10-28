import logging
from typing import Dict, Any
from config.settings import Settings

logger = logging.getLogger(__name__)

class TradingStrategy:
    def __init__(self):
        self.settings = Settings()
        self.position_size = 0.0
    
    def generate_signals(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Trading sinyalleri oluştur"""
        if not analysis:
            return {}
        
        signals = {}
        
        # Basit strateji: Çoklu gösterge uyumu
        buy_signals = 0
        sell_signals = 0
        
        # RSI sinyali
        if analysis.get('rsi', 50) < 35:
            buy_signals += 1
        elif analysis.get('rsi', 50) > 65:
            sell_signals += 1
        
        # MACD sinyali
        if analysis.get('macd', 0) > analysis.get('macd_signal', 0):
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Moving Average sinyali
        if analysis.get('sma_20', 0) > analysis.get('sma_50', 0):
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Sonuç
        if buy_signals >= 2:
            signals['action'] = 'BUY'
            signals['price'] = analysis.get('current_price', 0)
            signals['stop_loss'] = analysis.get('current_price', 0) * (1 - self.settings.trading.stop_loss_pct)
            signals['take_profit'] = analysis.get('current_price', 0) * (1 + self.settings.trading.take_profit_pct)
            
        elif sell_signals >= 2:
            signals['action'] = 'SELL'
            signals['price'] = analysis.get('current_price', 0)
            signals['stop_loss'] = analysis.get('current_price', 0) * (1 + self.settings.trading.stop_loss_pct)
            signals['take_profit'] = analysis.get('current_price', 0) * (1 - self.settings.trading.take_profit_pct)
        
        if signals:
            logger.info(f"Trading sinyali oluşturuldu: {signals}")
        
        return signals
    
    def calculate_position_size(self, portfolio_value: float, risk_per_trade: float = 0.02) -> float:
        """Pozisyon büyüklüğünü hesapla"""
        max_position = portfolio_value * self.settings.trading.max_position_size
        risk_based_position = portfolio_value * risk_per_trade
        
        return min(max_position, risk_based_position)
