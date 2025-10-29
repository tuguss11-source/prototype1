import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.data_fetcher import DataFetcher

def test_simple():
    print("🚀 Basit Test Başlıyor...")
    fetcher = DataFetcher()
    
    # Sadece tarihsel veri testi
    print("📊 Tarihsel veri testi...")
    data = fetcher.get_historical_data("BTCUSDT", "1h", 10)
    print(f"Veri boyutu: {data.shape}")
    if not data.empty:
        print("Son fiyat:", data["close"].iloc[-1])
    
    # Real-time test (kısa)
    print("⚡ Real-time test (10 saniye)...")
    fetcher.start_real_time_data(["BTCUSDT"])
    
    for i in range(10):
        time.sleep(1)
        price = fetcher.get_current_price("BTCUSDT")
        if price:
            print(f"{i+1}s - BTC: {price}")
        else:
            print(f"{i+1}s - Bekleniyor...")
    
    fetcher.stop_all_connections()
    print("✅ Test tamamlandı!")

if __name__ == "__main__":
    test_simple()