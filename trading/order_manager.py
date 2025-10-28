import asyncio
import logging
import ccxt
from typing import Dict, Optional
from config.settings import Settings
from config.database import DatabaseHandler
from trading.risk_manager import RiskManager

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self):
        self.settings = Settings()
        self.db = DatabaseHandler()
        self.risk_manager = RiskManager()
        
        # Exchange connection
        self.exchange = ccxt.binance({
            'apiKey': self.settings.api.binance_api_key,
            'secret': self.settings.api.binance_secret,
            'enableRateLimit': True,
            'sandbox': True if self.settings.debug else False  # Testnet için
        })
    
    async def place_order(self, symbol: str, side: str, quantity: float, order_type: str = 'market', 
                         price: Optional[float] = None, stop_loss: Optional[float] = None, 
                         take_profit: Optional[float] = None) -> Dict:
        """Sipariş yerleştir"""
        try:
            # Portfolio value (gerçek uygulamada exchange'den alınacak)
            portfolio_value = 1000  # Örnek değer
            
            # Risk kontrolü
            validation = self.risk_manager.validate_trade(symbol, side, quantity, price or 0, portfolio_value)
            if not validation['is_valid']:
                logger.error(f"Risk kontrolü başarısız: {validation['errors']}")
                return {'success': False, 'errors': validation['errors']}
            
            # Exchange'e sipariş gönder
            order_params = {
                'symbol': symbol.replace('/', ''),
                'type': order_type,
                'side': side.lower(),
                'amount': quantity,
            }
            
            if order_type == 'limit' and price:
                order_params['price'] = price
            
            # Stop loss ve take profit (binance için OCO order)
            if stop_loss and take_profit:
                order_params['stopPrice'] = stop_loss
                # Not: Gerçek uygulamada OCO order logic eklenmeli
            
            # Gerçek trade yapma (debug modunda simüle et)
            if self.settings.debug:
                logger.info(f"SIMÜLE SİPARİŞ: {order_params}")
                order_result = {
                    'id': 'simulated_order_' + str(hash(str(order_params))),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price or 0,
                    'status': 'filled'
                }
            else:
                # Gerçek sipariş (dikkat: para kaybedebilirsiniz!)
                order_result = self.exchange.create_order(**order_params)
            
            # Database'e kaydet
            if order_result.get('status') in ['filled', 'closed']:
                trade_id = self.db.add_trade(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    entry_price=price or float(order_result.get('price', 0)),
                    stop_loss=validation['stop_loss'],
                    take_profit=validation['take_profit'],
                    strategy="auto_trader"
                )
                
                if trade_id:
                    logger.info(f"Sipariş başarıyla yerleştirildi: {symbol} {side} {quantity}")
                    return {
                        'success': True,
                        'order_id': order_result.get('id'),
                        'trade_id': trade_id,
                        'stop_loss': validation['stop_loss'],
                        'take_profit': validation['take_profit']
                    }
            
            return {'success': False, 'error': 'Order placement failed'}
            
        except Exception as e:
            logger.error(f"Sipariş yerleştirme hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close_order(self, trade_id: int, reason: str = "manual"):
        """Siparişi kapat"""
        try:
            trade = self.db.get_session().query(Trade).filter(Trade.id == trade_id).first()
            if not trade or trade.status != 'OPEN':
                return {'success': False, 'error': 'Trade not found or already closed'}
            
            # Current price al
            ticker = self.exchange.fetch_ticker(trade.symbol.replace('/', ''))
            current_price = ticker['last']
            
            # Exchange'de sipariş kapat
            close_side = 'sell' if trade.side == 'BUY' else 'buy'
            
            if self.settings.debug:
                logger.info(f"SIMÜLE KAPATMA: {trade.symbol} {close_side} {trade.quantity}")
                close_result = {'status': 'closed'}
            else:
                close_result = self.exchange.create_order(
                    symbol=trade.symbol.replace('/', ''),
                    type='market',
                    side=close_side,
                    amount=trade.quantity
                )
            
            # Database'i güncelle
            if close_result.get('status') in ['filled', 'closed']:
                self.db.close_trade(trade_id, current_price)
                logger.info(f"Trade kapatıldı: {trade_id} - {reason}")
                return {'success': True, 'pnl': trade.pnl}
            
            return {'success': False, 'error': 'Close order failed'}
            
        except Exception as e:
            logger.error(f"Sipariş kapatma hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_stop_losses(self):
        """Stop loss'ları kontrol et"""
        open_trades = self.db.get_open_trades()
        
        for trade in open_trades:
            try:
                # Current price al
                ticker = self.exchange.fetch_ticker(trade.symbol.replace('/', ''))
                current_price = ticker['last']
                
                # Stop loss kontrolü
                if trade.side == 'BUY' and current_price <= trade.stop_loss:
                    logger.warning(f"Stop loss tetiklendi: {trade.symbol} {current_price} <= {trade.stop_loss}")
                    await self.close_order(trade.id, "stop_loss")
                
                elif trade.side == 'SELL' and current_price >= trade.stop_loss:
                    logger.warning(f"Stop loss tetiklendi: {trade.symbol} {current_price} >= {trade.stop_loss}")
                    await self.close_order(trade.id, "stop_loss")
                
                # Take profit kontrolü
                elif trade.side == 'BUY' and current_price >= trade.take_profit:
                    logger.info(f"Take profit tetiklendi: {trade.symbol} {current_price} >= {trade.take_profit}")
                    await self.close_order(trade.id, "take_profit")
                
                elif trade.side == 'SELL' and current_price <= trade.take_profit:
                    logger.info(f"Take profit tetiklendi: {trade.symbol} {current_price} <= {trade.take_profit}")
                    await self.close_order(trade.id, "take_profit")
                
                # Trailing stop güncelle
                self.risk_manager.update_trailing_stop(trade.id, current_price)
                
                # Current price güncelle
                self.db.update_trade(trade.id, current_price=current_price)
                
            except Exception as e:
                logger.error(f"Stop loss kontrol hatası {trade.id}: {e}")
