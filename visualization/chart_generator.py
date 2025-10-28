import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict
import logging
from config.database import DatabaseHandler

logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        self.db = DatabaseHandler()
        
    def create_price_chart(self, symbol: str, days: int = 30):
        try:
            session = self.db.get_session()
            from datetime import datetime, timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            market_data = session.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date
            ).order_by(MarketData.timestamp).all()
            
            if not market_data:
                logger.warning(f"No data found for {symbol}")
                return None
            
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'open': data.open_price,
                'high': data.high_price,
                'low': data.low_price,
                'close': data.close_price,
                'volume': data.volume
            } for data in market_data])
            
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} Price', 'Volume'),
                row_width=[0.7, 0.3]
            )
            
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )

            # Volume
            colors = ['red' if row['open'] > row['close'] else 'green' for _, row in df.iterrows()]
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f'{symbol} Price Chart - Last {days} Days',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_dark',
                height=600
            )
            
            fig.update_xaxes(rangeslider_visible=False)
            
            return fig
            
        except Exception as e:
            logger.error(f"Chart creation error: {e}")
            return None
        finally:
            session.close()
    
    def create_technical_chart(self, symbol: str, days: int = 30):
        try:
            session = self.db.get_session()
            from datetime import datetime, timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            market_data = session.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date
            ).order_by(MarketData.timestamp).all()
            
            if not market_data:
                return None
            
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'open': data.open_price,
                'high': data.high_price,
                'low': data.low_price,
                'close': data.close_price,
                'volume': data.volume,
                'rsi': data.rsi,
                'macd': data.macd,
                'macd_signal': data.macd_signal,
                'sma_20': data.sma_20,
                'sma_50': data.sma_50
            } for data in market_data])

            # Volume
            colors = ['red' if row['open'] > row['close'] else 'green' for _, row in df.iterrows()]
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f'{symbol} Price Chart - Last {days} Days',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_dark',
                height=600
            )
            
            fig.update_xaxes(rangeslider_visible=False)
            
            return fig
            
        except Exception as e:
            logger.error(f"Chart creation error: {e}")
            return None
        finally:
            session.close()
    
    def create_technical_chart(self, symbol: str, days: int = 30):
        try:
            session = self.db.get_session()
            from datetime import datetime, timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            market_data = session.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date
            ).order_by(MarketData.timestamp).all()
            
            if not market_data:
                return None
            
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'open': data.open_price,
                'high': data.high_price,
                'low': data.low_price,
                'close': data.close_price,
                'volume': data.volume,
                'rsi': data.rsi,
                'macd': data.macd,
                'macd_signal': data.macd_signal,
                'sma_20': data.sma_20,
                'sma_50': data.sma_50
            } for data in market_data])

            # 3 subplotlu grafik
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f'{symbol} Price with MA', 'RSI', 'MACD'),
                row_width=[0.4, 0.3, 0.3]
            )
            
            # Price ve Moving Averages
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            if df['sma_20'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['sma_20'],
                        name='SMA 20',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            if df['sma_50'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['sma_50'],
                        name='SMA 50',
                        line=dict(color='blue', width=1)
                    ),
                    row=1, col=1
                )
            
            # RSI
            if df['rsi'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['rsi'],
                        name='RSI',
                        line=dict(color='purple', width=1)
                    ),
                    row=2, col=1
                )
                
                # RSI seviyeleri
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

            # MACD
            if df['macd'].notna().any() and df['macd_signal'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['macd'],
                        name='MACD',
                        line=dict(color='blue', width=1)
                    ),
                    row=3, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['macd_signal'],
                        name='MACD Signal',
                        line=dict(color='red', width=1)
                    ),
                    row=3, col=1
                )
            
            fig.update_layout(
                title=f'{symbol} Technical Analysis - Last {days} Days',
                template='plotly_dark',
                height=800
            )
            
            fig.update_xaxes(rangeslider_visible=False)
            
            return fig
            
        except Exception as e:
            logger.error(f"Technical chart error: {e}")
            return None
        finally:
            session.close()
    
    def create_portfolio_chart(self):
        try:
            session = self.db.get_session()
            
            trades = session.query(Trade).filter(
                Trade.status == 'CLOSED'
            ).order_by(Trade.exit_timestamp).all()
            
            if not trades:
                return None
            
            # Cumulative PnL hesapla
            cumulative_pnl = 0
            dates = []
            pnls = []
            
            for trade in trades:
                cumulative_pnl += trade.pnl or 0
                dates.append(trade.exit_timestamp)
                pnls.append(cumulative_pnl)
            
            # Line chart
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=pnls,
                    mode='lines+markers',
                    name='Cumulative PnL',
                    line=dict(color='green' if cumulative_pnl > 0 else 'red', width=2)
                )
            )
            
            fig.update_layout(
                title='Portfolio Performance',
                xaxis_title='Date',
                yaxis_title='Cumulative PnL (USD)',
                template='plotly_dark',
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Portfolio chart error: {e}")
            return None
        finally:
            session.close()
    
    def save_chart(self, fig, filename: str):
        try:
            if fig:
                fig.write_html(f"charts/{filename}.html")
                logger.info(f"Chart saved: charts/{filename}.html")
                return True
            return False
        except Exception as e:
            logger.error(f"Save chart error: {e}")
            return False
