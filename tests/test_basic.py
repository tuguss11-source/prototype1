#!/usr/bin/env python3
"""
Temel test scripti
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from analysis.technical_analysis import TechnicalAnalysis
import pandas as pd
import numpy as np

def test_basic_functionality():
    """Temel fonksiyonları test et"""
    print("=== TEMEL TESTLER ===")
    
    # Settings test
    settings = Settings()
    print(f"✓ Settings yüklendi: {settings.trading.symbols}")
    
    # Technical Analysis test
    ta = TechnicalAnalysis()
    print("✓ Technical Analysis yüklendi")
    
    # Test data oluştur
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.normal(100, 10, 100),
        'high': np.random.normal(105, 10, 100),
        'low': np.random.normal(95, 10, 100),
        'close': np.random.normal(100, 10, 100),
        'volume': np.random.normal(1000, 100, 100)
    })
    
    # Analiz testi
    analysis = ta.analyze(test_data)
    print(f"✓ Teknik analiz tamamlandı: {len(analysis)} gösterge")
    
    # Sinyal testi
    signals = ta.generate_signals(analysis)
    print(f"✓ Sinyal üretimi: {signals}")
    
    print("🎉 Tüm temel testler başarılı!")

if __name__ == "__main__":
    test_basic_functionality()
