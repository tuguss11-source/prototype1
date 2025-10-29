import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class TechnicalAnalyzer:
    def __init__(self):
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/technical_analysis.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        RSI (Relative Strength Index) hesaplama
        """
        try:
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            self.logger.error(f"RSI hesaplama hatası: {e}")
            return pd.Series()
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence) hesaplama
        """
        try:
            exp1 = data['close'].ewm(span=fast).mean()
            exp2 = data['close'].ewm(span=slow).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=signal).mean()
            macd_histogram = macd - macd_signal
            return macd, macd_signal, macd_histogram
        except Exception as e:
            self.logger.error(f"MACD hesaplama hatası: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_moving_averages(self, data: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Dict[str, pd.Series]:
        """
        Çoklu Moving Average hesaplama
        """
        try:
            ma_dict = {}
            for period in periods:
                ma_dict[f'sma_{period}'] = data['close'].rolling(window=period).mean()
                ma_dict[f'ema_{period}'] = data['close'].ewm(span=period).mean()
            return ma_dict
        except Exception as e:
            self.logger.error(f"Moving Average hesaplama hatası: {e}")
            return {}
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands hesaplama
        """
        try:
            sma = data['close'].rolling(window=period).mean()
            rolling_std = data['close'].rolling(window=period).std()
            
            upper_band = sma + (rolling_std * std)
            lower_band = sma - (rolling_std * std)
            
            return upper_band, sma, lower_band
        except Exception as e:
            self.logger.error(f"Bollinger Bands hesaplama hatası: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator hesaplama
        """
        try:
            low_min = data['low'].rolling(window=k_period).min()
            high_max = data['high'].rolling(window=k_period).max()
            
            k = 100 * ((data['close'] - low_min) / (high_max - low_min))
            d = k.rolling(window=d_period).mean()
            
            return k, d
        except Exception as e:
            self.logger.error(f"Stochastic hesaplama hatası: {e}")
            return pd.Series(), pd.Series()
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Tüm göstergelere göre sinyal üretme
        """
        try:
            signals = {}
            
            # RSI sinyali
            rsi = self.calculate_rsi(data)
            if not rsi.empty:
                last_rsi = rsi.iloc[-1]
                if last_rsi > 70:
                    signals['rsi'] = 'SELL'
                elif last_rsi < 30:
                    signals['rsi'] = 'BUY'
                else:
                    signals['rsi'] = 'NEUTRAL'
            
            # MACD sinyali
            macd, macd_signal, _ = self.calculate_macd(data)
            if not macd.empty and not macd_signal.empty:
                if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
                    signals['macd'] = 'BUY'
                elif macd.iloc[-1] < macd_signal.iloc[-1] and macd.iloc[-2] >= macd_signal.iloc[-2]:
                    signals['macd'] = 'SELL'
                else:
                    signals['macd'] = 'NEUTRAL'
            
            # Moving Average sinyali
            ma_dict = self.calculate_moving_averages(data, [20, 50])
            if 'sma_20' in ma_dict and 'sma_50' in ma_dict:
                sma_20 = ma_dict['sma_20'].iloc[-1]
                sma_50 = ma_dict['sma_50'].iloc[-1]
                if sma_20 > sma_50:
                    signals['ma'] = 'BUY'
                else:
                    signals['ma'] = 'SELL'
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Sinyal üretme hatası: {e}")
            return {}