from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from config.settings import Settings

Base = declarative_base()
logger = logging.getLogger(__name__)

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # BUY/SELL
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    exit_price = Column(Float)
    pnl = Column(Float)
    pnl_percentage = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    exit_timestamp = Column(DateTime)
    status = Column(String(20), default='OPEN')  # OPEN/CLOSED/CANCELLED
    strategy = Column(String(50))
    notes = Column(Text)

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), default='1m')
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Teknik göstergeler
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    ema_12 = Column(Float)
    ema_26 = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)

class Portfolio(Base):
    __tablename__ = 'portfolio'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_balance = Column(Float)
    available_balance = Column(Float)
    locked_balance = Column(Float)
    total_pnl = Column(Float)
    daily_pnl = Column(Float)

class DatabaseHandler:
    def __init__(self):
        self.settings = Settings()
        self.engine = create_engine(self.settings.get_db_url())
        self.Session = sessionmaker(bind=self.engine)
        self.init_db()
        
    def init_db(self):
        """Veritabanı tablolarını oluştur"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Veritabanı tabloları oluşturuldu")
        except Exception as e:
            logger.error(f"Veritabanı oluşturma hatası: {e}")
        
    def get_session(self):
        """Database session'ı döndür"""
        return self.Session()
    
    def add_trade(self, symbol, side, quantity, entry_price, stop_loss=None, take_profit=None, strategy=""):
        """Yeni trade ekle"""
        session = self.get_session()
        try:
            trade = Trade(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                strategy=strategy,
                current_price=entry_price
            )
            session.add(trade)
            session.commit()
            logger.info(f"Trade eklendi: {symbol} {side} {quantity}")
            return trade.id
        except Exception as e:
            session.rollback()
            logger.error(f"Trade ekleme hatası: {e}")
            return None
        finally:
            session.close()
    
    def update_trade(self, trade_id, **kwargs):
        """Trade güncelle"""
        session = self.get_session()
        try:
            trade = session.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                for key, value in kwargs.items():
                    setattr(trade, key, value)
                session.commit()
                logger.info(f"Trade güncellendi: {trade_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Trade güncelleme hatası: {e}")
            return False
        finally:
            session.close()
    
    def close_trade(self, trade_id, exit_price):
        """Trade'i kapat"""
        session = self.get_session()
        try:
            trade = session.query(Trade).filter(Trade.id == trade_id).first()
            if trade and trade.status == 'OPEN':
                trade.exit_price = exit_price
                trade.exit_timestamp = datetime.utcnow()
                trade.status = 'CLOSED'
                
                # PnL hesapla
                if trade.side == 'BUY':
                    trade.pnl = (exit_price - trade.entry_price) * trade.quantity
                    trade.pnl_percentage = (exit_price - trade.entry_price) / trade.entry_price * 100
                else:  # SELL
                    trade.pnl = (trade.entry_price - exit_price) * trade.quantity
                    trade.pnl_percentage = (trade.entry_price - exit_price) / trade.entry_price * 100
                
                session.commit()
                logger.info(f"Trade kapatıldı: {trade_id} PnL: {trade.pnl:.2f}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Trade kapatma hatası: {e}")
            return False
        finally:
            session.close()
    
    def get_open_trades(self):
        """Açık trade'leri getir"""
        session = self.get_session()
        try:
            return session.query(Trade).filter(Trade.status == 'OPEN').all()
        finally:
            session.close()
    
    def save_market_data(self, symbol, data, analysis=None):
        """Market verisini kaydet"""
        session = self.get_session()
        try:
            market_data = MarketData(
                symbol=symbol,
                open_price=data['open'] if 'open' in data else None,
                high_price=data['high'] if 'high' in data else None,
                low_price=data['low'] if 'low' in data else None,
                close_price=data['close'] if 'close' in data else None,
                volume=data['volume'] if 'volume' in data else None,
                timestamp=datetime.utcnow()
            )
            
            if analysis:
                market_data.rsi = analysis.get('rsi')
                market_data.macd = analysis.get('macd')
                market_data.macd_signal = analysis.get('macd_signal')
                market_data.sma_20 = analysis.get('sma_20')
                market_data.sma_50 = analysis.get('sma_50')
                market_data.ema_12 = analysis.get('ema_12')
                market_data.ema_26 = analysis.get('ema_26')
                market_data.bb_upper = analysis.get('bb_upper')
                market_data.bb_lower = analysis.get('bb_lower')
            
            session.add(market_data)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Market data kaydetme hatası: {e}")
        finally:
            session.close()
