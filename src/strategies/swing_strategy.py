import pandas as pd
from typing import Dict, Any
from .base_strategy import BaseStrategy
from analysis.technical_analyzer import TechnicalAnalyzer

class SwingStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Swing Trading")
        self.analyzer = TechnicalAnalyzer()
        self.required_periods = 50
    
    def generate_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        if len(data) < self.required_periods:
            return {"signal": "HOLD", "confidence": 0, "message": "Yetersiz veri"}
        
        # Swing için orta vadeli göstergeler
        rsi = self.analyzer.calculate_rsi(data, period=14)
        macd, macd_signal, histogram = self.analyzer.calculate_macd(data)
        ma_dict = self.analyzer.calculate_moving_averages(data, [20, 50])
        upper_bb, middle_bb, lower_bb = self.analyzer.calculate_bollinger_bands(data)
        
        signals = []
        confidence = 0
        
        # RSI sinyali
        if not rsi.empty:
            last_rsi = rsi.iloc[-1]
            if last_rsi > 70:
                signals.append("SELL")
                confidence += 0.2
            elif last_rsi < 30:
                signals.append("BUY")
                confidence += 0.2
        
        # MACD sinyali
        if not macd.empty and not macd_signal.empty:
            if macd.iloc[-1] > macd_signal.iloc[-1] and histogram.iloc[-1] > 0:
                signals.append("BUY")
                confidence += 0.3
            elif macd.iloc[-1] < macd_signal.iloc[-1] and histogram.iloc[-1] < 0:
                signals.append("SELL")
                confidence += 0.3
        
        # Bollinger Bands sinyali
        if not upper_bb.empty and not lower_bb.empty:
            last_close = data['close'].iloc[-1]
            if last_close <= lower_bb.iloc[-1]:
                signals.append("BUY")
                confidence += 0.3
            elif last_close >= upper_bb.iloc[-1]:
                signals.append("SELL")
                confidence += 0.3
        
        # Moving Average sinyali
        if 'sma_20' in ma_dict and 'sma_50' in ma_dict:
            sma_20 = ma_dict['sma_20'].iloc[-1]
            sma_50 = ma_dict['sma_50'].iloc[-1]
            if sma_20 > sma_50 and data['close'].iloc[-1] > sma_20:
                signals.append("BUY")
                confidence += 0.2
            elif sma_20 < sma_50 and data['close'].iloc[-1] < sma_20:
                signals.append("SELL")
                confidence += 0.2
        
        # Sinyal kararı
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        
        if buy_count >= 2 and buy_count > sell_count:
            final_signal = "BUY"
        elif sell_count >= 2 and sell_count > buy_count:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
            confidence = confidence * 0.5
        
        return {
            "signal": final_signal,
            "confidence": min(confidence, 1.0),
            "indicators": {
                "rsi": rsi.iloc[-1] if not rsi.empty else None,
                "macd": macd.iloc[-1] if not macd.empty else None,
                "bollinger_upper": upper_bb.iloc[-1] if not upper_bb.empty else None,
                "bollinger_lower": lower_bb.iloc[-1] if not lower_bb.empty else None
            },
            "message": f"Swing sinyali: {final_signal} (Güven: %{confidence*100:.1f})"
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "timeframe": "1h-4h",
            "hold_time": "günler-haftalar",
            "risk_level": "orta",
            "indicators": ["RSI(14)", "MACD(12,26,9)", "Bollinger Bands(20,2)", "MA(20,50)"]
        }