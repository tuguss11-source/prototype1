#!/usr/bin/env python3
"""
Gelişmiş test scripti
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from config.database import DatabaseHandler
from trading.risk_manager import RiskManager
from analysis.backtester import Backtester
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_database():
    """Database test"""
    print("=== DATABASE TEST ===")
    
    db = DatabaseHandler()
    print("✓ Database bağlantısı başarılı")
    
    # Test trade ekle
    trade_id = db.add_trade(
        symbol="BTC/USDT",
        side="BUY",
        quantity=0.01,
        entry_price=50000,
        stop_loss=49000,
        take_profit=52000
    )
    
    if trade_id:
        print(f"✓ Test trade eklendi: ID {trade_id}")
        
        # Trade güncelle
        success = db.update_trade(trade_id, current_price=51000)
        if success:
            print("✓ Trade güncelleme başarılı")
        
        # Trade kapat
        success = db.close_trade(trade_id, 51500)
        if success:
            print("✓ Trade kapatma başarılı")
    else:
        print("✗ Trade ekleme başarısız")

def test_risk_manager():
    """Risk manager test"""
    print("\n=== RISK MANAGER TEST ===")
    
    risk_manager = RiskManager()
    
    # Pozisyon büyüklüğü testi
    is_valid = risk_manager.check_position_size("BTC/USDT", 0.1, 50000, 10000)
    print(f"✓ Pozisyon büyüklüğü kontrolü: {'Geçerli' if is_valid else 'Geçersiz'}")
    
    # Stop loss hesaplama
    stop_loss = risk_manager.calculate_stop_loss(50000, "BUY")
    take_profit = risk_manager.calculate_take_profit(50000, "BUY")
    print(f"✓ Stop loss: {stop_loss:.2f}")
    print(f"✓ Take profit: {take_profit:.2f}")
    
    # Trade validation
    validation = risk_manager.validate_trade("BTC/USDT", "BUY", 0.01, 50000, 10000)
    print(f"✓ Trade validation: {'Geçerli' if validation['is_valid'] else 'Geçersiz'}")

def test_backtester():
    """Backtester test"""
    print("\n=== BACKTESTER TEST ===")
    
    # Test verisi oluştur
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    test_data = {
        'BTC/USDT': pd.DataFrame({
            'timestamp': dates,
            'open': np.random.normal(50000, 2000, 200),
            'high': np.random.normal(51000, 2000, 200),
            'low': np.random.normal(49000, 2000, 200),
            'close': np.random.normal(50000, 2000, 200),
            'volume': np.random.normal(1000, 100, 200)
        })
    }
    
    backtester = Backtester(initial_balance=10000)
    results = backtester.run_backtest(test_data)
    
    print("✓ Backtest tamamlandı")
    backtester.generate_report(results)

def main():
    """Ana test fonksiyonu"""
    print("GELİŞMİŞ TESTLER BAŞLATILIYOR...")
    
    try:
        test_database()
        test_risk_manager()
        test_backtester()
        
        print("\n🎉 TÜM GELİŞMİŞ TESTLER BAŞARILI!")
        
    except Exception as e:
        print(f"\n❌ TEST HATASI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
