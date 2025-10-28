#!/usr/bin/env python3
"""
Ana Trade Programı - Güncellenmiş Versiyon
"""
import asyncio
import logging
import signal
import sys
from config.settings import Settings
from data.data_collector import DataCollector
from data.websocket_client import RealTimeDataCollector
from analysis.technical_analysis import TechnicalAnalysis
from trading.strategy import TradingStrategy
from trading.order_manager import OrderManager
from trading.risk_manager import RiskManager
from visualization.chart_generator import ChartGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TradeProgram:
    def __init__(self):
        self.settings = Settings()
        self.data_collector = DataCollector()
        self.realtime_collector = RealTimeDataCollector()
        self.technical_analysis = TechnicalAnalysis()
        self.trading_strategy = TradingStrategy()
        self.order_manager = OrderManager()
        self.risk_manager = RiskManager()
        self.chart_generator = ChartGenerator()
        
        self.running = False
        
        # Signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def initialize(self):
        """Programı başlat"""
        logger.info("Trade programı başlatılıyor...")
        
        # WebSocket bağlantısını başlat
        ws_connected = await self.realtime_collector.start()
        if not ws_connected:
            logger.warning("WebSocket connection failed, using fallback data collection")
        
        # Başlangıç verisi al
        initial_data = await self.data_collector.get_multiple_symbols_data()
        logger.info(f"Initial data collected for {len(initial_data)} symbols")
        
        return True
    
    async def run(self):
        """Ana program döngüsü"""
        self.running = True
        
        try:
            # Initialize
            success = await self.initialize()
            if not success:
                logger.error("Initialization failed")
                return
            
            logger.info("Trade programı çalışıyor...")
            
            # Ana döngü
            iteration = 0
            while self.running:
                try:
                    iteration += 1
                    logger.info(f"=== Iteration {iteration} ===")
                    
                    # 1. Stop loss ve take profit kontrolü
                    await self.order_manager.check_stop_losses()
                    
                    # 2. Gerçek zamanlı veri al
                    current_prices = await self.realtime_collector.get_current_prices()
                    if not current_prices:
                        # Fallback: REST API'den veri al
                        market_data = await self.data_collector.get_multiple_symbols_data()
                        current_prices = {
                            symbol: data['close'].iloc[-1] if not data.empty else 0 
                            for symbol, data in market_data.items()
                        }
                    
                    # 3. Her sembol için analiz yap
                    for symbol in self.settings.trading.symbols:
                        try:
                            # Veri al
                            data = await self.data_collector.get_real_time_data(symbol)
                            if data.empty:
                                continue
                            
                            # Teknik analiz
                            analysis = self.technical_analysis.analyze(data)
                            if not analysis:
                                continue

                            # Trading sinyali oluştur
                            signals = self.trading_strategy.generate_signals(analysis)
                            
                            # Sinyal varsa işle
                            if signals:
                                await self.process_trading_signal(symbol, signals, analysis)
                            
                            # Her 10 iterasyonda bir grafik oluştur
                            if iteration % 10 == 0:
                                self.generate_charts(symbol)
                            
                        except Exception as e:
                            logger.error(f"Symbol {symbol} processing error: {e}")
                    
                    # 4. Bekle
                    logger.info(f"Waiting {self.settings.trading.update_interval} seconds...")
                    await asyncio.sleep(self.settings.trading.update_interval)
                    
                except Exception as e:
                    logger.error(f"Main loop error: {e}")
                    await asyncio.sleep(10)  # Hata durumunda kısa bekle
                    
        except KeyboardInterrupt:
            logger.info("Program kullanıcı tarafından durduruldu")
        except Exception as e:
            logger.error(f"Program hatası: {e}")
        finally:
            await self.shutdown()
    
    async def process_trading_signal(self, symbol: str, signals: dict, analysis: dict):
        """Trading sinyalini işle"""
        try:
            current_price = analysis.get('current_price', 0)
            if not current_price:
                return
            
            action = signals.get('action')
            stop_loss = signals.get('stop_loss')
            take_profit = signals.get('take_profit')
            
            # Portfolio değeri (gerçek uygulamada exchange'den alınacak)
            portfolio_value = 10000  # Örnek değer
            
            if action == 'BUY':
                # Pozisyon büyüklüğünü hesapla
                position_size = self.risk_manager.calculate_position_size(portfolio_value)
                quantity = position_size / current_price
                
                # Siparişi yerleştir
                result = await self.order_manager.place_order(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    order_type='market',
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )

                if result['success']:
                    logger.info(f"BUY order executed: {symbol} {quantity} @ {current_price}")
                else:
                    logger.warning(f"BUY order failed: {result.get('error', 'Unknown error')}")
            
            elif action == 'SELL':
                # Açık pozisyonları kontrol et
                open_trades = self.order_manager.db.get_open_trades()
                symbol_trades = [t for t in open_trades if t.symbol == symbol and t.side == 'BUY']
                
                for trade in symbol_trades:
                    # Satış yap
                    result = await self.order_manager.close_order(trade.id, "strategy_signal")
                    if result['success']:
                        logger.info(f"SELL order executed: {symbol} PnL: {result.get('pnl', 0):.2f}")
                    else:
                        logger.warning(f"SELL order failed: {result.get('error', 'Unknown error')}")
                        
        except Exception as e:
            logger.error(f"Signal processing error for {symbol}: {e}")
    
    def generate_charts(self, symbol: str):
        """Grafikler oluştur"""
        try:
            # Fiyat grafiği
            price_chart = self.chart_generator.create_price_chart(symbol, days=7)
            if price_chart:
                self.chart_generator.save_chart(price_chart, f"{symbol}_price_7d")
            
            # Teknik analiz grafiği
            tech_chart = self.chart_generator.create_technical_chart(symbol, days=7)
            if tech_chart:
                self.chart_generator.save_chart(tech_chart, f"{symbol}_technical_7d")
            
            # Portfolio grafiği (her sembol için değil, genel)
            if symbol == self.settings.trading.symbols[0]:  # Sadece ilk sembol için
                portfolio_chart = self.chart_generator.create_portfolio_chart()
                if portfolio_chart:
                    self.chart_generator.save_chart(portfolio_chart, "portfolio_performance")
                    
        except Exception as e:
            logger.error(f"Chart generation error: {e}")

    async def shutdown(self):
        """Programı kapat"""
        logger.info("Shutting down trade program...")
        
        # WebSocket bağlantısını kapat
        await self.realtime_collector.stop()
        
        # Açık pozisyonları kapat (isteğe bağlı)
        # await self.close_all_positions()
        
        logger.info("Trade program shut down successfully")

async def main():
    """Ana fonksiyon"""
    program = TradeProgram()
    await program.run()

if __name__ == "__main__":
    asyncio.run(main())
