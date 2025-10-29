import time
import sys
import os

# Proje yollarını ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.data_fetcher import DataFetcher

def test_historical_data():
    print("📊 Tarihsel Veri Testi...")
    fetcher = DataFetcher()
    
    # BTC için tarihsel veri çek
    btc_data = fetcher.get_historical_data('BTCUSDT', '1h', 50)
    print(f"BTC Veri Boyutu: {btc_data.shape}")
    if not btc_data.empty:
        print("Son 3 veri:")
        print(btc_data.tail(3))
    else:
        print("❌ Veri çekilemedi!")
    
    return btc_data

def test_multiple_symbols():
    print("\n🔢 Çoklu Sembol Testi...")
    fetcher = DataFetcher()
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    data = fetcher.get_multiple_symbols_data(symbols, '1h', 20)
    
    for symbol, df in data.items():
        print(f"{symbol}: {len(df)} bar")
    
    return data

def test_24h_stats():
    print("\n📈 24 Saatlik İstatistikler Testi...")
    fetcher = DataFetcher()
    
    stats = fetcher.get_24h_stats('BTCUSDT')
    if stats:
        print(f"BTCUSDT 24h İstatistikleri:")
        print(f"  Fiyat Değişimi: %{stats.get('price_change', 'N/A')}")
        print(f"  Son Fiyat: ${stats.get('last_price', 'N/A')}")
        print(f"  24h Yüksek: ${stats.get('high_24h', 'N/A')}")
        print(f"  24h Düşük: ${stats.get('low_24h', 'N/A')}")
        print(f"  Hacim: {stats.get('volume', 'N/A')}")
    else:
        print("❌ İstatistikler çekilemedi!")

def test_real_time():
    print("\n⚡ Real-time Veri Testi (15 saniye)...")
    fetcher = DataFetcher()
    
    try:
        # Real-time veriyi başlat
        fetcher.start_real_time_data(['BTCUSDT', 'ETHUSDT'])
        
        # 15 saniye boyunca verileri göster
        for i in range(15):
            time.sleep(1)
            btc_price = fetcher.get_current_price('BTCUSDT')
            eth_price = fetcher.get_current_price('ETHUSDT')
            if btc_price or eth_price:
                print(f"⏱️  {i+1}s - BTC: {btc_price}, ETH: {eth_price}")
            else:
                print(f"⏱️  {i+1}s - Veri bekleniyor...")
        
    except Exception as e:
        print(f"❌ Real-time test hatası: {e}")
    finally:
        # Bağlantıları kapat
        fetcher.stop_all_connections()

if __name__ == "__main__":
    print("🚀 Veri Çekme Modülü Testi Başlıyor...")
    print("=" * 50)
    
    try:
        # Test 1: Tarihsel veri
        test_historical_data()
        
        # Test 2: Çoklu sembol
        test_multiple_symbols()
        
        # Test 3: 24h istatistikler
        test_24h_stats()
        
        # Test 4: Real-time veri
        test_real_time()
        
        print("\n✅ Tüm testler tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {e}")
        print("\n🔧 Sorun Giderme:")
        print("1. İnternet bağlantınızı kontrol edin")
        print("2. Binance API erişimine izin verildiğinden emin olun")
        print("3. Gerekli kütüphaneleri yükleyin: pip install ccxt websocket-client")