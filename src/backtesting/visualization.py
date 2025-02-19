# src/backtesting/visualization.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .engine import Backtester, BacktestResult
from typing import Optional
import pandas as pd

class BacktestVisualizer:
    """Visualize backtest results"""
    def __init__(self, data: pd.DataFrame, result: BacktestResult):
        self.data = data
        self.result = result
        
    def create_dashboard(self) -> go.Figure:
        """Create interactive dashboard of backtest results"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price & Trades', 'Equity Curve', 'Drawdown'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Price chart with trades
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['abertura'],
                high=self.data['maxima'],
                low=self.data['minima'],
                close=self.data['fechamento'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Add trade markers
        buy_trades = [t for t in self.result.trades if t['type'] == 'BUY']
        sell_trades = [t for t in self.result.trades if t['type'] == 'SELL']
        
        fig.add_trace(
            go.Scatter(
                x=[t['timestamp'] for t in buy_trades],
                y=[t['price'] for t in buy_trades],
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'),
                name='Buy'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=[t['timestamp'] for t in sell_trades],
                y=[t['price'] for t in sell_trades],
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name='Sell'
            ),
            row=1, col=1
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=self.result.equity_curve.index,
                y=self.result.equity_curve.values,
                name='Equity'
            ),
            row=2, col=1
        )
        
        # Drawdown
        drawdown = (self.result.equity_curve - self.result.equity_curve.cummax()) / self.result.equity_curve.cummax()
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values * 100,
                name='Drawdown',
                fill='tozeroy'
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='Backtest Results',
            height=900,
            showlegend=True
        )
        
        return fig