import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), src))

from data.data_fetcher import DataFetcher
from strategies.strategy_manager import StrategyManager
from deepseek.analyzer import DeepSeekAnalyzer

def test_deepseek_strict()
    print(🚀 DeepSeek Strict Test (Fallback Yok))
    print(=  50)
    
    try
        # DeepSeek Analyzer'ı oluştur
        analyzer = DeepSeekAnalyzer()
        
        if not analyzer.test_connection()
            print(❌ DeepSeek API bağlantısı yok!)
            return
        
        print(✅ DeepSeek API bağlantısı başarılı!)
        
        # Veri çek
        fetcher = DataFetcher()
        data = fetcher.get_historical_data(BTCUSDT, 1h, 100)
        
        if data.empty
            print(❌ Veri çekilemedi!)
            return
        
        current_price = data['close'].iloc[-1]
        
        # Strateji analizi
        strategy_manager = StrategyManager()
        strategies_results = strategy_manager.analyze_symbol(BTCUSDT, data)
        
        print(📊 Strateji Sonuçları)
        for strategy, result in strategies_results.items()
            print(f  {strategy} {result['signal']} (%{result['confidence']100.1f}))
        
        # DeepSeek analizi
        print(n🤖 DeepSeek Analiz Çalışıyor...)
        analysis = analyzer.analyze_trading_signals(BTCUSDT, strategies_results, current_price)
        
        print(fn🎯 DEEPSEEK ANALİZİ)
        print(f  Öneri {analysis['recommendation']})
        print(f  Güven %{analysis['confidence']})
        print(f  Risk {analysis['risk_level']})
        print(f  Gerekçe {analysis['reasoning']})
        
    except ValueError as e
        print(f❌ API Key Hatası {e})
    except ConnectionError as e
        print(f❌ Bağlantı Hatası {e})
    except Exception as e
        print(f❌ Beklenmeyen Hata {e})

if __name__ == __main__
    test_deepseek_strict()