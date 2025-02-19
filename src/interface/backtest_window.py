# src/interface/backtest_window.py

import customtkinter as ctk
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
from ..backtesting.engine import Backtester
from ..backtesting.visualization import BacktestVisualizer
from ..trading.strategy import MovingAverageStrategy
from ..utils.binance_client import BinanceClient
from .base_window import BaseWindow

class BacktestWindow(BaseWindow):
    """Window for backtesting trading strategies"""
    def __init__(self, parent: ctk.CTk, binance_client: BinanceClient):
        super().__init__()
        self.window = ctk.CTkToplevel(parent)
        self.client = binance_client
        self.setup_window()
        self.setup_components()
        
    def setup_window(self):
        """Initialize window properties"""
        self.window.title("Backtest Estratégia")
        self.window.geometry("1200x800")
        
    def setup_components(self):
        """Setup UI components"""
        # Control Frame
        control_frame = ctk.CTkFrame(self.window)
        control_frame.pack(pady=10, padx=10, fill="x")
        
        # Symbol selection
        self.create_label(control_frame, "Par de Trading:").pack(side="left", padx=5)
        self.symbol_var = ctk.StringVar(value="BTCBRL")
        self.symbol_entry = self.create_entry(
            control_frame,
            textvariable=self.symbol_var
        )
        self.symbol_entry.pack(side="left", padx=5)
        
        # Date range
        self.create_label(control_frame, "Período (dias):").pack(side="left", padx=5)
        self.days_var = ctk.StringVar(value="30")
        self.days_entry = self.create_entry(
            control_frame,
            textvariable=self.days_var
        )
        self.days_entry.pack(side="left", padx=5)
        
        # Initial capital
        self.create_label(control_frame, "Capital Inicial:").pack(side="left", padx=5)
        self.capital_var = ctk.StringVar(value="10000")
        self.capital_entry = self.create_entry(
            control_frame,
            textvariable=self.capital_var
        )
        self.capital_entry.pack(side="left", padx=5)
        
        # Run button
        self.create_button(
            control_frame,
            "Executar Backtest",
            self.run_backtest
        ).pack(side="left", padx=20)
        
        # Results Frame
        results_frame = ctk.CTkFrame(self.window)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Metrics Frame
        self.metrics_frame = ctk.CTkFrame(results_frame)
        self.metrics_frame.pack(pady=5, padx=5, fill="x")
        
        metrics_title = self.create_label(
            self.metrics_frame,
            "Métricas de Performance",
            font_size=self.title_font_size
        )
        metrics_title.pack(pady=5)
        
        # Create labels for metrics
        self.metric_labels = {}
        for metric in ['total_trades', 'win_rate', 'total_profit', 
                      'max_drawdown', 'sharpe_ratio', 'profit_factor']:
            self.metric_labels[metric] = self.create_label(self.metrics_frame, "-")
            self.metric_labels[metric].pack(pady=2)
            
        # Chart Frame
        self.chart_frame = ctk.CTkFrame(results_frame)
        self.chart_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
    def run_backtest(self):
        """Execute backtest and display results"""
        try:
            # Get parameters
            symbol = self.symbol_var.get()
            days = int(self.days_var.get())
            capital = float(self.capital_var.get())
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = self.client.get_historical_klines(
                symbol=symbol,
                interval=self.client.KLINE_INTERVAL_1HOUR,
                limit=24 * days
            )
            
            # Create and run backtest
            strategy = MovingAverageStrategy()
            backtester = Backtester(data, strategy, initial_capital=capital)
            result = backtester.run()
            
            # Update metrics display
            self.update_metrics(result)
            
            # Create and display visualization
            self.display_chart(data, result)
            
        except Exception as e:
            self.show_error("Erro no Backtest", str(e))
            
    def update_metrics(self, result):
        """Update metrics display with backtest results"""
        metrics = {
            'total_trades': f"Total de Trades: {result.metrics['total_trades']}",
            'win_rate': f"Taxa de Acerto: {result.metrics['win_rate']:.2%}",
            'total_profit': f"Lucro Total: R$ {result.metrics['total_profit']:.2f}",
            'max_drawdown': f"Drawdown Máximo: {result.metrics['max_drawdown']:.2%}",
            'sharpe_ratio': f"Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}",
            'profit_factor': f"Profit Factor: {result.metrics['profit_factor']:.2f}"
        }
        
        for metric, value in metrics.items():
            self.metric_labels[metric].configure(text=value)
            
    def display_chart(self, data: pd.DataFrame, result):
        """Display interactive chart with backtest results"""
        try:
            visualizer = BacktestVisualizer(data, result)
            fig = visualizer.create_dashboard()
            
            # Create HTML file with chart
            html_file = "backtest_chart.html"
            fig.write_html(html_file)
            
            # Open chart in default browser
            import webbrowser
            webbrowser.open(html_file)
            
        except Exception as e:
            self.show_error("Erro na Visualização", str(e))
            
    def show_error(self, title: str, message: str):
        """Show error message"""
        error_window = ctk.CTkToplevel(self.window)
        error_window.title(title)
        error_window.geometry("400x200")
        
        ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350
        ).pack(pady=20, padx=20)
        
        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy
        ).pack(pady=10)
            
class BacktestTab(ctk.CTkFrame):
    """Tab for backtest functionality in main window"""
    def __init__(self, parent, binance_client: BinanceClient):
        super().__init__(parent)
        self.client = binance_client
        self.setup_components()
        
    def setup_components(self):
        """Setup UI components"""
        # Strategy Selection
        strategy_frame = ctk.CTkFrame(self)
        strategy_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(
            strategy_frame,
            text="Estratégia:",
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        self.strategy_var = ctk.StringVar(value="Média Móvel")
        strategy_combo = ctk.CTkComboBox(
            strategy_frame,
            values=["Média Móvel", "RSI", "MACD"],
            variable=self.strategy_var,
            font=("Arial", 14)
        )
        strategy_combo.pack(side="left", padx=5)
        
        # Parameters Frame
        params_frame = ctk.CTkFrame(self)
        params_frame.pack(pady=10, padx=10, fill="x")
        
        # Moving Average Parameters
        self.ma_params = {
            'fast_period': ctk.StringVar(value="7"),
            'slow_period': ctk.StringVar(value="40")
        }
        
        ctk.CTkLabel(
            params_frame,
            text="Média Rápida:",
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        ctk.CTkEntry(
            params_frame,
            textvariable=self.ma_params['fast_period'],
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            params_frame,
            text="Média Lenta:",
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        ctk.CTkEntry(
            params_frame,
            textvariable=self.ma_params['slow_period'],
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        # Open Backtest Window Button
        ctk.CTkButton(
            self,
            text="Abrir Backtest",
            command=self.open_backtest_window,
            font=("Arial", 14)
        ).pack(pady=10)
        
    def open_backtest_window(self):
        """Open backtest window"""
        backtest_window = BacktestWindow(self, self.client)
        backtest_window.window.grab_set()  # Make window modal
        
        # Update strategy parameters
        if self.strategy_var.get() == "Média Móvel":
            backtest_window.strategy = MovingAverageStrategy(
                fast_period=int(self.ma_params['fast_period'].get()),
                slow_period=int(self.ma_params['slow_period'].get())
            )