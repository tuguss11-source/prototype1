import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import sys
import os

# Proje yollarını ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.data_fetcher import DataFetcher
from strategies.strategy_manager import StrategyManager
from deepseek.analyzer import DeepSeekAnalyzer

class CryptoTradingDashboard:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.strategy_manager = StrategyManager()
        
        # DeepSeek analyzer'ı başlat
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.deepseek_analyzer = DeepSeekAnalyzer(api_key=api_key) if api_key else None
        
        # Dashboard state'ini başlat
        self.setup_page_config()
        
    def setup_page_config(self):
        """Streamlit sayfa ayarlarını yapılandır"""
        st.set_page_config(
            page_title="Crypto Trading Signals",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Özel CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #1E90FF;
            text-align: center;
            margin-bottom: 2rem;
        }
        .signal-buy {
            background-color: #00FF00 !important;
            color: black !important;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .signal-sell {
            background-color: #FF0000 !important;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .signal-hold {
            background-color: #FFA500 !important;
            color: black !important;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .metric-card {
            background-color: #2E2E2E;
            padding: 15px;
            border-radius: 10px;
            margin: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Dashboard'u çalıştır"""
        # Sidebar
        self.render_sidebar()
        
        # Ana içerik
        st.markdown('<div class="main-header">🚀 Crypto Trading Signal System</div>', unsafe_allow_html=True)
        
        # Real-time veri güncellemesi
        if st.button("🔄 Verileri Güncelle"):
            st.rerun()
        
        # Dashboard bileşenleri
        self.render_price_charts()
        self.render_trading_signals()
        self.render_technical_analysis()
        self.render_portfolio_section()
        self.render_deepseek_analysis()
        
    def render_sidebar(self):
        """Sidebar içeriğini oluştur"""
        with st.sidebar:
            st.title("⚙️ Ayarlar")
            
            # Sembol seçimi
            st.subheader("Semboller")
            selected_symbols = st.multiselect(
                "Analiz Edilecek Semboller:",
                ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"],
                default=["BTCUSDT", "ETHUSDT"]
            )
            
            # Zaman dilimi seçimi
            st.subheader("Zaman Dilimi")
            timeframe = st.selectbox(
                "Zaman Dilimi:",
                ["1m", "5m", "15m", "1h", "4h", "1d"],
                index=3
            )
            
            # DeepSeek API ayarları
            st.subheader("DeepSeek API")
            api_key = st.text_input("API Key:", type="password", value=os.environ.get("DEEPSEEK_API_KEY", ""))
            if api_key and api_key != os.environ.get("DEEPSEEK_API_KEY"):
                os.environ["DEEPSEEK_API_KEY"] = api_key
                st.success("API Key güncellendi!")
            
            # Strateji ayarları
            st.subheader("Stratejiler")
            scalp_active = st.checkbox("Scalp Stratejisi", value=True)
            swing_active = st.checkbox("Swing Stratejisi", value=True)
            daily_active = st.checkbox("Günlük Strateji", value=True)
            
            # Sistem bilgileri
            st.subheader("Sistem Durumu")
            st.metric("Veri Kaynağı", "Binance ✓")
            st.metric("Stratejiler", "3 Aktif ✓")
            st.metric("DeepSeek", "Hazır" if self.deepseek_analyzer else "API Key Bekleniyor")
    
    def render_price_charts(self):
        """Fiyat grafiklerini oluştur"""
        st.header("📊 Canlı Fiyat Grafikleri")
        
        # Seçili semboller için grafikler
        symbols = ["BTCUSDT", "ETHUSDT"]  # Örnek semboller
        
        for symbol in symbols:
            with st.expander(f"{symbol} - Canlı Grafik", expanded=True):
                # Tarihsel veriyi al
                data = self.data_fetcher.get_historical_data(symbol, "1h", 100)
                
                if not data.empty:
                    # Candlestick grafiği
                    fig = go.Figure()
                    
                    # Candlestick
                    fig.add_trace(go.Candlestick(
                        x=data.index,
                        open=data['open'],
                        high=data['high'],
                        low=data['low'],
                        close=data['close'],
                        name=symbol
                    ))
                    
                    # 20 periyotluk moving average
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['close'].rolling(20).mean(),
                        line=dict(color='orange', width=1),
                        name='MA 20'
                    ))
                    
                    fig.update_layout(
                        title=f"{symbol} Fiyat Hareketleri",
                        xaxis_title="Zaman",
                        yaxis_title="Fiyat (USDT)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Hızlı istatistikler
                    col1, col2, col3, col4 = st.columns(4)
                    current_price = data['close'].iloc[-1]
                    price_change = ((current_price - data['close'].iloc[-2]) / data['close'].iloc[-2]) * 100
                    
                    with col1:
                        st.metric("Mevcut Fiyat", f"${current_price:,.2f}")
                    with col2:
                        st.metric("24s Değişim", f"{price_change:+.2f}%")
                    with col3:
                        st.metric("24s Yüksek", f"${data['high'].max():,.2f}")
                    with col4:
                        st.metric("24s Düşük", f"${data['low'].min():,.2f}")
    
    def render_trading_signals(self):
        """Trading sinyallerini göster"""
        st.header("🎯 Trading Sinyalleri")
        
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        for symbol in symbols:
            with st.expander(f"{symbol} - Strateji Sinyalleri", expanded=True):
                # Veriyi al
                data = self.data_fetcher.get_historical_data(symbol, "1h", 200)
                
                if not data.empty:
                    # Strateji analizleri
                    strategies_results = self.strategy_manager.analyze_symbol(symbol, data)
                    
                    # Sinyal kartları
                    cols = st.columns(3)
                    
                    for idx, (strategy_name, result) in enumerate(strategies_results.items()):
                        with cols[idx]:
                            signal = result['signal']
                            confidence = result['confidence'] * 100
                            
                            # Sinyal renk sınıfı
                            signal_class = "signal-buy" if signal == "BUY" else "signal-sell" if signal == "SELL" else "signal-hold"
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>{strategy_name.upper()}</h3>
                                <div class="{signal_class}">{signal}</div>
                                <p>Güven: %{confidence:.1f}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    def render_technical_analysis(self):
        """Teknik analiz göstergelerini göster"""
        st.header("📈 Teknik Analiz")
        
        symbol = "BTCUSDT"  # Örnek sembol
        data = self.data_fetcher.get_historical_data(symbol, "1h", 100)
        
        if not data.empty:
            cols = st.columns(4)
            
            # RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            with cols[0]:
                rsi_color = "green" if current_rsi < 30 else "red" if current_rsi > 70 else "orange"
                st.metric("RSI (14)", f"{current_rsi:.2f}", delta=None, delta_color="off")
                st.progress(current_rsi/100)
                st.caption(f"Durum: {'Oversold' if current_rsi < 30 else 'Overbought' if current_rsi > 70 else 'Nötr'}")
            
            # MACD
            exp1 = data['close'].ewm(span=12).mean()
            exp2 = data['close'].ewm(span=26).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=9).mean()
            current_macd = macd.iloc[-1]
            
            with cols[1]:
                macd_status = "AL" if current_macd > macd_signal.iloc[-1] else "SAT"
                st.metric("MACD", f"{current_macd:.2f}", macd_status)
            
            # Moving Averages
            ma_20 = data['close'].rolling(20).mean().iloc[-1]
            ma_50 = data['close'].rolling(50).mean().iloc[-1]
            
            with cols[2]:
                ma_status = "Yükseliş" if ma_20 > ma_50 else "Düşüş"
                st.metric("MA 20/50", f"{ma_20:.2f}/{ma_50:.2f}", ma_status)
            
            # Bollinger Bands
            bb_upper = data['close'].rolling(20).mean() + (data['close'].rolling(20).std() * 2)
            bb_lower = data['close'].rolling(20).mean() - (data['close'].rolling(20).std() * 2)
            current_price = data['close'].iloc[-1]
            
            with cols[3]:
                bb_position = ((current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])) * 100
                st.metric("Bollinger Pos", f"%{bb_position:.1f}")
                st.caption(f"Durum: {'Üst Band' if bb_position > 80 else 'Alt Band' if bb_position < 20 else 'Orta'}")
    
    def render_portfolio_section(self):
        """Portföy takip bölümünü oluştur"""
        st.header("🛒 Sepet Takibi")
        
        # Portföy yönetimi
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Portföyüm")
            
            # Örnek portföy verileri
            portfolio_data = {
                "BTCUSDT": {"miktar": 0.1, "ortalama_fiyat": 110000, "mevcut_fiyat": 112730},
                "ETHUSDT": {"miktar": 2.0, "ortalama_fiyat": 2400, "mevcut_fiyat": 2450},
                "ADAUSDT": {"miktar": 1000, "ortalama_fiyat": 0.45, "mevcut_fiyat": 0.42}
            }
            
            for symbol, data in portfolio_data.items():
                with st.expander(f"{symbol} - {data['miktar']} adet"):
                    cols = st.columns(3)
                    
                    with cols[0]:
                        st.metric("Ortalama", f"${data['ortalama_fiyat']:.2f}")
                    with cols[1]:
                        st.metric("Mevcut", f"${data['mevcut_fiyat']:.2f}")
                    with cols[2]:
                        pnl = ((data['mevcut_fiyat'] - data['ortalama_fiyat']) / data['ortalama_fiyat']) * 100
                        st.metric("K/Z", f"%{pnl:+.2f}")
        
        with col2:
            st.subheader("Yeni Ekle")
            
            # Yeni coin ekleme formu
            with st.form("yeni_coin"):
                symbol = st.text_input("Sembol (örn: BTCUSDT)")
                miktar = st.number_input("Miktar", min_value=0.0, step=0.1)
                ortalama_fiyat = st.number_input("Ortalama Fiyat", min_value=0.0, step=1.0)
                
                if st.form_submit_button("Sepete Ekle"):
                    st.success(f"{symbol} sepete eklendi!")
    
    def render_deepseek_analysis(self):
        """DeepSeek analiz bölümünü oluştur"""
        st.header("🤖 DeepSeek AI Analizi")
        
        if not self.deepseek_analyzer:
            st.warning("DeepSeek analizi için lütfen API key girin. (Sidebar → DeepSeek API)")
            return
        
        symbol = "BTCUSDT"
        data = self.data_fetcher.get_historical_data(symbol, "1h", 200)
        
        if not data.empty:
            current_price = data['close'].iloc[-1]
            strategies_results = self.strategy_manager.analyze_symbol(symbol, data)
            
            try:
                # DeepSeek analizini al
                analysis = self.deepseek_analyzer.analyze_trading_signals(symbol, strategies_results, current_price)
                
                # Analiz sonuçlarını göster
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("AI Önerisi")
                    
                    recommendation = analysis['recommendation']
                    confidence = analysis['confidence']
                    risk_level = analysis['risk_level']
                    
                    # Öneri kartı
                    if recommendation == "AL":
                        st.success(f"🎯 **{recommendation}** (%{confidence} Güven)")
                    elif recommendation == "SAT":
                        st.error(f"🎯 **{recommendation}** (%{confidence} Güven)")
                    else:
                        st.warning(f"🎯 **{recommendation}** (%{confidence} Güven)")
                    
                    st.metric("Risk Seviyesi", risk_level)
                
                with col2:
                    st.subheader("Detaylı Analiz")
                    st.write(analysis['reasoning'])
                    
                    # Fiyat hedefleri
                    price_targets = analysis.get('analysis', {}).get('price_targets', {})
                    if price_targets:
                        st.subheader("🎯 Fiyat Hedefleri")
                        for target, value in price_targets.items():
                            st.write(f"**{target}**: {value}")
                
            except Exception as e:
                st.error(f"DeepSeek analiz hatası: {str(e)}")

def main():
    """Ana uygulama"""
    dashboard = CryptoTradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()