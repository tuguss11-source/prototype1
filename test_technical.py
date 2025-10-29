import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.data_fetcher import DataFetcher
from analysis.technical_analyzer import TechnicalAnalyzer

def test_technical_analysis():
    print("🧪 Teknik Analiz Testi Başlıyor...")
    
    # Veri çek
    fetcher = DataFetcher()
    data = fetcher.get_historical_data("BTCUSDT", "1h", 100)
    
    if data.empty:
        print("❌ Veri çekilemedi!")
        return
    
    print(f"📊 Analiz için {len(data)} bar veri kullanılıyor...")
    
    # Teknik analiz
    analyzer = TechnicalAnalyzer()
    
    # RSI
    rsi = analyzer.calculate_rsi(data)
    if not rsi.empty:
        print(f"📈 RSI: {rsi.iloc[-1]:.2f}")
    
    # MACD
    macd, signal, histogram = analyzer.calculate_macd(data)
    if not macd.empty:
        print(f"📊 MACD: {macd.iloc[-1]:.2f}, Signal: {signal.iloc[-1]:.2f}")
    
    # Moving Averages
    ma_dict = analyzer.calculate_moving_averages(data, [20, 50])
    for ma_name, ma_values in ma_dict.items():
        if not ma_values.empty:
            print(f"📉 {ma_name}: {ma_values.iloc[-1]:.2f}")
    
    # Bollinger Bands
    upper, middle, lower = analyzer.calculate_bollinger_bands(data)
    if not upper.empty:
        print(f"📊 Bollinger Bands - Upper: {upper.iloc[-1]:.2f}, Middle: {middle.iloc[-1]:.2f}, Lower: {lower.iloc[-1]:.2f}")
    
    # Sinyaller
    signals = analyzer.generate_signals(data)
    print("🎯 Sinyaller:", signals)
    
    print("✅ Teknik analiz testi tamamlandı!")

if __name__ == "__main__":
    test_technical_analysis()