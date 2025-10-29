import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.data_fetcher import DataFetcher
from strategies.strategy_manager import StrategyManager
from deepseek.analyzer import DeepSeekAnalyzer

def test_local_deepseek():
    print("🚀 Local DeepSeek Testi Başlıyor...")
    print("=" * 50)
    
    # Local analyzer oluştur
    analyzer = DeepSeekAnalyzer()
    
    # Bağlantı testi
    if not analyzer.test_connection():
        print("❌ LM Studio bağlantısı yok!")
        print("   Lütfen LM Studio'yu çalıştırıp model yükleyin.")
        print("   URL: http://localhost:1234")
        return
    
    print("✅ LM Studio bağlantısı başarılı!")
    
    # Kullanılabilir modelleri göster
    models = analyzer.get_available_models()
    print(f"📋 Mevcut Modeller: {models}")
    
    # Veri çek
    fetcher = DataFetcher()
    data = fetcher.get_historical_data("BTCUSDT", "1h", 100)
    
    if data.empty:
        print("❌ Veri çekilemedi!")
        return
    
    current_price = data['close'].iloc[-1]
    
    # Strateji analizi
    strategy_manager = StrategyManager()
    strategies_results = strategy_manager.analyze_symbol("BTCUSDT", data)
    
    print("📊 Strateji Sonuçları:")
    for strategy, result in strategies_results.items():
        print(f"  {strategy}: {result['signal']} (%{result['confidence']*100:.1f})")
    
    # Local DeepSeek analizi
    print("\n🤖 Local DeepSeek Analiz Çalışıyor...")
    try:
        analysis = analyzer.analyze_trading_signals("BTCUSDT", strategies_results, current_price)
        
        print(f"\n🎯 {analysis['source']} ANALİZİ:")
        print(f"  Öneri: {analysis['recommendation']}")
        print(f"  Güven: %{analysis['confidence']}")
        print(f"  Risk: {analysis['risk_level']}")
        print(f"  Gerekçe: {analysis['reasoning']}")
        print(f"  Piyasa: {analysis.get('market_context', 'N/A')}")
        
    except ConnectionError as e:
        print(f"❌ Bağlantı Hatası: {e}")
    except Exception as e:
        print(f"❌ Beklenmeyen Hata: {e}")

def setup_instructions():
    print("\n🔧 LM Studio Kurulum Talimatları:")
    print("1. LM Studio'yu indirin ve kurun: https://lmstudio.ai/")
    print("2. LM Studio'yu açın ve 'Search Models' sekmesine tıklayın")
    print("3. Arama kutusuna 'deepseek' yazın")
    print("4. Bir DeepSeek modeli seçin (örneğin: deepseek-coder)")
    print("5. Modeli indirin ve yükleyin")
    print("6. 'Local Server' sekmesine geçin")
    print("7. 'Start Server' butonuna tıklayın")
    print("8. Server'ın http://localhost:1234 adresinde çalıştığından emin olun")
    print("9. Testi tekrar çalıştırın: python test_local_deepseek.py")

if __name__ == "__main__":
    test_local_deepseek()
    setup_instructions()