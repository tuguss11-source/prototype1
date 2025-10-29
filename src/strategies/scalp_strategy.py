import pandas as pd
from typing import Dict, Any
from .base_strategy import BaseStrategy
from analysis.technical_analyzer import TechnicalAnalyzer

class ScalpStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Scalp Trading")
        self.analyzer = TechnicalAnalyzer()
        self.required_periods = 20
    
    def generate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        if len(data) < self.required_periods:
            return {"signal": "HOLD", "confidence": 0, "message": "Yetersiz veri"}
        
        # Scalp için kısa vadeli göstergeler
        rsi = self.analyzer.calculate_rsi(data, period=10)
        macd, macd_signal, _ = self.analyzer.calculate_macd(data, fast=6, slow=13, signal=5)
        ma_dict = self.analyzer.calculate_moving_averages(data, [5, 10])
        
        signals = []
        confidence = 0
        
        # RSI sinyali
        if not rsi.empty:
            last_rsi = rsi.iloc[-1]
            if last_rsi > 80:
                signals.append("SELL")
                confidence += 0.3
            elif last_rsi < 20:
                signals.append("BUY")
                confidence += 0.3
        
        # MACD sinyali
        if not macd.empty and not macd_signal.empty:
            if macd.iloc[-1] > macd_signal.iloc[-1]:
                signals.append("BUY")
                confidence += 0.3
            else:
                signals.append("SELL")
                confidence += 0.3
        
        # Moving Average sinyali
        if 'sma_5' in ma_dict and 'sma_10' in ma_dict:
            sma_5 = ma_dict['sma_5'].iloc[-1]
            sma_10 = ma_dict['sma_10'].iloc[-1]
            if sma_5 > sma_10:
                signals.append("BUY")
                confidence += 0.4
            else:
                signals.append("SELL")
                confidence += 0.4
        
        # Sinyal kararı
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        
        if buy_count > sell_count:
            final_signal = "BUY"
        elif sell_count > buy_count:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
        
        return {
            "signal": final_signal,
            "confidence": min(confidence, 1.0),
            "indicators": {
                "rsi": rsi.iloc[-1] if not rsi.empty else None,
                "macd": macd.iloc[-1] if not macd.empty else None,
                "macd_signal": macd_signal.iloc[-1] if not macd_signal.empty else None
            },
            "message": f"Scalp sinyali: {final_signal} (Güven: %{confidence*100:.1f})"
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "timeframe": "1m-5m",
            "hold_time": "dakikalar",
            "risk_level": "yüksek",
            "indicators": ["RSI(10)", "MACD(6,13,5)", "MA(5,10)"]
        }