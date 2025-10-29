import pandas as pd
from typing import Dict, Any
from .base_strategy import BaseStrategy
from analysis.technical_analyzer import TechnicalAnalyzer

class DailyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Daily Trading")
        self.analyzer = TechnicalAnalyzer()
        self.required_periods = 100
    
    def generate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        if len(data) < self.required_periods:
            return {"signal": "HOLD", "confidence": 0, "message": "Yetersiz veri"}
        
        # Günlük trading için uzun vadeli göstergeler
        rsi = self.analyzer.calculate_rsi(data, period=21)
        macd, macd_signal, histogram = self.analyzer.calculate_macd(data, fast=12, slow=26, signal=9)
        ma_dict = self.analyzer.calculate_moving_averages(data, [50, 200])
        k, d = self.analyzer.calculate_stochastic(data)
        
        signals = []
        confidence = 0
        
        # RSI sinyali
        if not rsi.empty:
            last_rsi = rsi.iloc[-1]
            if last_rsi > 65:
                signals.append("SELL")
                confidence += 0.15
            elif last_rsi < 35:
                signals.append("BUY")
                confidence += 0.15
        
        # MACD sinyali
        if not macd.empty and not macd_signal.empty:
            if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
                signals.append("BUY")
                confidence += 0.25
            elif macd.iloc[-1] < macd_signal.iloc[-1] and macd.iloc[-2] >= macd_signal.iloc[-2]:
                signals.append("SELL")
                confidence += 0.25
        
        # Moving Average sinyali
        if 'sma_50' in ma_dict and 'sma_200' in ma_dict:
            sma_50 = ma_dict['sma_50'].iloc[-1]
            sma_200 = ma_dict['sma_200'].iloc[-1]
            if sma_50 > sma_200:
                signals.append("BUY")
                confidence += 0.3
            else:
                signals.append("SELL")
                confidence += 0.3
        
        # Stochastic sinyali
        if not k.empty and not d.empty:
            if k.iloc[-1] < 20 and d.iloc[-1] < 20 and k.iloc[-1] > d.iloc[-1]:
                signals.append("BUY")
                confidence += 0.15
            elif k.iloc[-1] > 80 and d.iloc[-1] > 80 and k.iloc[-1] < d.iloc[-1]:
                signals.append("SELL")
                confidence += 0.15
        
        # Volume analizi
        volume_avg = data['volume'].rolling(20).mean()
        if not volume_avg.empty:
            last_volume = data['volume'].iloc[-1]
            avg_volume = volume_avg.iloc[-1]
            if last_volume > avg_volume * 1.5 and data['close'].iloc[-1] > data['close'].iloc[-2]:
                signals.append("BUY")
                confidence += 0.15
        
        # Sinyal kararı
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        
        if buy_count >= 3:
            final_signal = "BUY"
        elif sell_count >= 3:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
            confidence = confidence * 0.3
        
        return {
            "signal": final_signal,
            "confidence": min(confidence, 1.0),
            "indicators": {
                "rsi": rsi.iloc[-1] if not rsi.empty else None,
                "macd": macd.iloc[-1] if not macd.empty else None,
                "sma_50": ma_dict.get('sma_50', pd.Series()).iloc[-1] if 'sma_50' in ma_dict else None,
                "sma_200": ma_dict.get('sma_200', pd.Series()).iloc[-1] if 'sma_200' in ma_dict else None,
                "stochastic_k": k.iloc[-1] if not k.empty else None,
                "stochastic_d": d.iloc[-1] if not d.empty else None
            },
            "message": f"Günlük sinyal: {final_signal} (Güven: %{confidence*100:.1f})"
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "timeframe": "4h-1d",
            "hold_time": "haftalar-aylar",
            "risk_level": "düşük",
            "indicators": ["RSI(21)", "MACD(12,26,9)", "MA(50,200)", "Stochastic(14,3)"]
        }