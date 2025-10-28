import pandas as pd
import talib
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    def __init__(self):
        self.indicators = {}
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Teknik analiz göstergelerini hesapla"""
        if df.empty:
            return {}
        
        try:
            # Price data
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            volume = df['volume'].values
            
            # Trend göstergeleri
            sma_20 = talib.SMA(close, timeperiod=20)
            sma_50 = talib.SMA(close, timeperiod=50)
            ema_12 = talib.EMA(close, timeperiod=12)
            ema_26 = talib.EMA(close, timeperiod=26)
            
            # MACD
            macd, macd_signal, macd_hist = talib.MACD(close)
            
            # RSI
            rsi = talib.RSI(close, timeperiod=14)
            
            # Bollinger Bantları
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            
            # Stochastic
            slowk, slowd = talib.STOCH(high, low, close)
            
            # Volume göstergeleri
            ad = talib.AD(high, low, close, volume)
            
            analysis_result = {
                'sma_20': sma_20[-1] if not np.isnan(sma_20[-1]) else None,
                'sma_50': sma_50[-1] if not np.isnan(sma_50[-1]) else None,
                'ema_12': ema_12[-1] if not np.isnan(ema_12[-1]) else None,
                'ema_26': ema_26[-1] if not np.isnan(ema_26[-1]) else None,
                'macd': macd[-1] if not np.isnan(macd[-1]) else None,
                'macd_signal': macd_signal[-1] if not np.isnan(macd_signal[-1]) else None,
                'rsi': rsi[-1] if not np.isnan(rsi[-1]) else None,
                'bb_upper': bb_upper[-1] if not np.isnan(bb_upper[-1]) else None,
                'bb_lower': bb_lower[-1] if not np.isnan(bb_lower[-1]) else None,
                'stoch_k': slowk[-1] if not np.isnan(slowk[-1]) else None,
                'stoch_d': slowd[-1] if not np.isnan(slowd[-1]) else None,
                'current_price': close[-1],
                'timestamp': df['timestamp'].iloc[-1]
            }
            
            logger.debug(f"Teknik analiz tamamlandı: {analysis_result}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Teknik analiz hatası: {e}")
            return {}
    
    def generate_signals(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Analiz sonuçlarına göre sinyal üret"""
        if not analysis:
            return {}
        
        signals = {}
        
        # RSI sinyalleri
        if analysis['rsi'] > 70:
            signals['rsi'] = 'SELL'
        elif analysis['rsi'] < 30:
            signals['rsi'] = 'BUY'
        
        # MACD sinyalleri
        if analysis['macd'] and analysis['macd_signal']:
            if analysis['macd'] > analysis['macd_signal']:
                signals['macd'] = 'BUY'
            else:
                signals['macd'] = 'SELL'
        
        # Moving Average sinyalleri
        if analysis['sma_20'] and analysis['sma_50']:
            if analysis['sma_20'] > analysis['sma_50']:
                signals['ma'] = 'BUY'
            else:
                signals['ma'] = 'SELL'
        
        return signals
