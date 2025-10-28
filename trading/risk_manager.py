import logging
from typing import Dict, List
from config.settings import Settings
from config.database import DatabaseHandler

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        self.settings = Settings()
        self.db = DatabaseHandler()
        self.max_daily_loss = 0.05  # Günlük maksimum %5 kayıp
        self.daily_pnl = 0.0
        
    def check_position_size(self, symbol: str, quantity: float, price: float, portfolio_value: float) -> bool:
        """Pozisyon büyüklüğünü kontrol et"""
        position_value = quantity * price
        max_position = portfolio_value * self.settings.trading.max_position_size
        
        if position_value > max_position:
            logger.warning(f"Pozisyon büyüklüğü limiti aşıldı: {position_value} > {max_position}")
            return False
        
        logger.info(f"Pozisyon büyüklüğü uygun: {position_value} <= {max_position}")
        return True
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Stop loss fiyatını hesapla"""
        if side == 'BUY':
            return entry_price * (1 - self.settings.trading.stop_loss_pct)
        else:  # SELL
            return entry_price * (1 + self.settings.trading.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Take profit fiyatını hesapla"""
        if side == 'BUY':
            return entry_price * (1 + self.settings.trading.take_profit_pct)
        else:  # SELL
            return entry_price * (1 - self.settings.trading.take_profit_pct)
    
    def check_daily_loss_limit(self, new_trade_pnl: float = 0) -> bool:
        """Günlük kayıp limitini kontrol et"""
        # Burada gerçek PnL hesaplaması yapılacak
        open_trades = self.db.get_open_trades()
        total_pnl = sum(trade.pnl or 0 for trade in open_trades)
        total_pnl += new_trade_pnl
        
        if total_pnl < -self.max_daily_loss:
            logger.warning(f"Günlük kayıp limiti aşıldı: {total_pnl}")
            return False
        
        return True
    
    def validate_trade(self, symbol: str, side: str, quantity: float, price: float, portfolio_value: float) -> Dict:
        """Trade'i validate et"""
        validation_result = {
            'is_valid': True,
            'stop_loss': self.calculate_stop_loss(price, side),
            'take_profit': self.calculate_take_profit(price, side),
            'errors': []
        }
        
        # Pozisyon büyüklüğü kontrolü
        if not self.check_position_size(symbol, quantity, price, portfolio_value):
            validation_result['is_valid'] = False
            validation_result['errors'].append('Position size limit exceeded')
        
        # Günlük kayıp kontrolü
        if not self.check_daily_loss_limit():
            validation_result['is_valid'] = False
            validation_result['errors'].append('Daily loss limit exceeded')
        
        # Aynı sembolde çok fazla açık pozisyon kontrolü
        open_trades = self.db.get_open_trades()
        same_symbol_trades = [t for t in open_trades if t.symbol == symbol]
        if len(same_symbol_trades) >= 3:  # Maksimum 3 açık pozisyon
            validation_result['is_valid'] = False
            validation_result['errors'].append('Too many open positions for this symbol')
        
        return validation_result
    
    def update_trailing_stop(self, trade_id: int, current_price: float):
        """Trailing stop güncelle"""
        if not self.settings.trading.trailing_stop:
            return
        
        trade = self.db.get_session().query(Trade).filter(Trade.id == trade_id).first()
        if trade and trade.status == 'OPEN':
            if trade.side == 'BUY':
                # Yüksek fiyatı takip et, stop loss'u yükselt
                new_stop = current_price * (1 - self.settings.trading.stop_loss_pct)
                if new_stop > trade.stop_loss:
                    self.db.update_trade(trade_id, stop_loss=new_stop)
                    logger.info(f"Trailing stop güncellendi: {trade.stop_loss} -> {new_stop}")
            else:  # SELL
                # Düşük fiyatı takip et, stop loss'u düşür
                new_stop = current_price * (1 + self.settings.trading.stop_loss_pct)
                if new_stop < trade.stop_loss:
                    self.db.update_trade(trade_id, stop_loss=new_stop)
                    logger.info(f"Trailing stop güncellendi: {trade.stop_loss} -> {new_stop}")
