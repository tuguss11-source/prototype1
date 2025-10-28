import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from analysis.technical_analysis import TechnicalAnalysis
from trading.strategy import TradingStrategy

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}
        self.trades = []
        self.technical_analysis = TechnicalAnalysis()
        self.strategy = TradingStrategy()
        
    def run_backtest(self, data: Dict[str, pd.DataFrame], strategy_params: Dict = None):
        """Backtest çalıştır"""
        logger.info("Backtest başlatılıyor...")
        
        results = {}
        
        for symbol, df in data.items():
            symbol_results = self._backtest_symbol(symbol, df, strategy_params)
            results[symbol] = symbol_results
            
        # Portfolio sonuçlarını hesapla
        portfolio_results = self._calculate_portfolio_results(results)
        
        return {
            'symbol_results': results,
            'portfolio_results': portfolio_results,
            'trades': self.trades
        }
    
    def _backtest_symbol(self, symbol: str, df: pd.DataFrame, strategy_params: Dict):
        """Tek bir sembol için backtest çalıştır"""
        balance = self.initial_balance
        position = 0
        entry_price = 0
        trades = []
        
        for i in range(50, len(df)):  # lk 50 barı atla, göstergeler için
            current_data = df.iloc[:i+1]
            
            # Teknik analiz
            analysis = self.technical_analysis.analyze(current_data)
            
            # Sinyal üret
            signals = self.strategy.generate_signals(analysis)
            
            current_price = df.iloc[i]['close']
            current_time = df.iloc[i]['timestamp']
            
            # Trading logic
            if not position and signals.get('action') == 'BUY':
                # Alım yap - %10 pozisyon
                position_size = min(balance * 0.1, balance)
                quantity = position_size / current_price
                entry_price = current_price
                
                trade = {
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'entry_time': current_time,
                    'stop_loss': signals.get('stop_loss'),
                    'take_profit': signals.get('take_profit')
                }
                
                balance -= position_size
                position = quantity
                trades.append(trade)
                
            elif position and signals.get('action') == 'SELL':
                # Satım yap
                exit_value = position * current_price
                pnl = exit_value - (position * entry_price)
                
                trade = trades[-1]  # Son trade'i al
                trade.update({
                    'exit_price': current_price,
                    'exit_time': current_time,
                    'pnl': pnl,
                    'pnl_percentage': (pnl / (position * entry_price)) * 100
                })
                
                balance += exit_value
                position = 0
                
            # Stop loss ve take profit kontrolü
            elif position:
                current_trade = trades[-1]
                if current_trade['stop_loss'] and current_price <= current_trade['stop_loss']:
                    # Stop loss tetiklendi
                    exit_value = position * current_price
                    pnl = exit_value - (position * entry_price)
                    
                    current_trade.update({
                        'exit_price': current_price,
                        'exit_time': current_time,
                        'pnl': pnl,
                        'pnl_percentage': (pnl / (position * entry_price)) * 100,
                        'exit_reason': 'stop_loss'
                    })
                    
                    balance += exit_value
                    position = 0
                    
                elif current_trade['take_profit'] and current_price >= current_trade['take_profit']:
                    # Take profit tetiklendi
                    exit_value = position * current_price
                    pnl = exit_value - (position * entry_price)
                    
                    current_trade.update({
                        'exit_price': current_price,
                        'exit_time': current_time,
                        'pnl': pnl,
                        'pnl_percentage': (pnl / (position * entry_price)) * 100,
                        'exit_reason': 'take_profit'
                    })
                    
                    balance += exit_value
                    position = 0
        
        # Kapanmamış pozisyonları kapat
        if position:
            current_price = df.iloc[-1]['close']
            exit_value = position * current_price
            pnl = exit_value - (position * entry_price)
            
            trades[-1].update({
                'exit_price': current_price,
                'exit_time': df.iloc[-1]['timestamp'],
                'pnl': pnl,
                'pnl_percentage': (pnl / (position * entry_price)) * 100,
                'exit_reason': 'end_of_period'
            })
            
            balance += exit_value
        
        # Sonuçları hesapla
        total_return = (balance - self.initial_balance) / self.initial_balance * 100
        winning_trades = [t for t in trades if 'pnl' in t and t['pnl'] > 0]
        losing_trades = [t for t in trades if 'pnl' in t and t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': balance,
            'total_return': total_return,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'trades': trades
        }
    
    def _calculate_portfolio_results(self, symbol_results: Dict):
        """Portfolio sonuçlarını hesapla"""
        total_initial = self.initial_balance
        total_final = sum(result['final_balance'] for result in symbol_results.values())
        total_return = (total_final - total_initial) / total_initial * 100
        
        all_trades = []
        for symbol, results in symbol_results.items():
            for trade in results.get('trades', []):
                trade['symbol'] = symbol
                all_trades.append(trade)
        
        winning_trades = [t for t in all_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in all_trades if t.get('pnl', 0) <= 0]
        
        return {
            'total_initial_balance': total_initial,
            'total_final_balance': total_final,
            'total_return': total_return,
            'total_trades': len(all_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(all_trades) * 100 if all_trades else 0,
            'all_trades': all_trades
        }
    
    def generate_report(self, backtest_results: Dict):
        """Backtest raporu oluştur"""
        portfolio = backtest_results['portfolio_results']
        
        print("=== BACKTEST RAPORU ===")
        print(f"Başlangıç Bakiyesi: ${portfolio['total_initial_balance']:,.2f}")
        print(f"Son Bakiye: ${portfolio['total_final_balance']:,.2f}")
        print(f"Toplam Getiri: {portfolio['total_return']:.2f}%")
        print(f"Toplam şlem: {portfolio['total_trades']}")
        print(f"Başarılı şlem: {portfolio['winning_trades']}")
        print(f"Başarısız şlem: {portfolio['losing_trades']}")
        print(f"Başarı Oranı: {portfolio['win_rate']:.2f}%")
        
        # Sembol bazlı sonuçlar
        print("\n=== SEMBOLLER ===")
        for symbol, results in backtest_results['symbol_results'].items():
            print(f"{symbol}: {results['total_return']:.2f}% ({results['total_trades']} işlem)")
