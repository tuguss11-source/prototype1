import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.data_fetcher import DataFetcher
from strategies.strategy_manager import StrategyManager

def test_strategies():
    print("🎯 Strateji Testi Başlıyor...")
    
    # Veri çek
    fetcher = DataFetcher()
    data = fetcher.get_historical_data("BTCUSDT", "1h", 200)
    
    if data.empty:
        print("❌ Veri çekilemedi!")
        return
    
    print(f"📊 {len(data)} bar veri ile stratejiler test ediliyor...")
    
    # Strateji yöneticisi
    strategy_manager = StrategyManager()
    
    # Strateji bilgileri
    strategies_info = strategy_manager.get_all_strategies_info()
    print("📋 Strateji Bilgileri:")
    for strategy_name, info in strategies_info.items():
        print(f"  {info['name']}: {info['parameters']}")
    
    # Sembol analizi
    results = strategy_manager.analyze_symbol("BTCUSDT", data)
    
    print("\n🎯 Strateji Sonuçları:")
    for strategy_name, result in results.items():
        print(f"  {strategy_name.upper()}: {result['signal']} (Güven: %{result['confidence']*100:.1f})")
        print(f"     Mesaj: {result['message']}")
        
        # Göstergeleri göster
        if 'indicators' in result and result['indicators']:
            print("     Göstergeler:")
            for indicator, value in result['indicators'].items():
                if value is not None:
                    if isinstance(value, float):
                        print(f"       {indicator}: {value:.2f}")
                    else:
                        print(f"       {indicator}: {value}")
    
    print("\n✅ Strateji testi tamamlandı!")

if __name__ == "__main__":
    test_strategies()