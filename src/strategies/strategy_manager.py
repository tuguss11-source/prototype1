from typing import Dict, List, Any
import pandas as pd
from .scalp_strategy import ScalpStrategy
from .swing_strategy import SwingStrategy
from .daily_strategy import DailyStrategy

class StrategyManager:
    def __init__(self):
        self.strategies = {
            'scalp': ScalpStrategy(),
            'swing': SwingStrategy(),
            'daily': DailyStrategy()
        }
    
    def analyze_symbol(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        
        for strategy_name, strategy in self.strategies.items():
            try:
                signal = strategy.generate_signal(data)
                results[strategy_name] = signal
            except Exception as e:
                results[strategy_name] = {
                    "signal": "ERROR",
                    "confidence": 0,
                    "message": f"Hata: {str(e)}"
                }
        
        return results
    
    def get_all_strategies_info(self) -> Dict[str, Any]:
        info = {}
        for strategy_name, strategy in self.strategies.items():
            info[strategy_name] = {
                "name": strategy.name,
                "parameters": strategy.get_parameters()
            }
        return info