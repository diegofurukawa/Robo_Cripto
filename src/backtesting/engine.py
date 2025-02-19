# src/backtesting/engine.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from ..trading.strategy import TradingStrategy
from ..utils.logger import Logger

class BacktestResult:
    """Container for backtest results"""
    def __init__(self):
        self.trades: List[Dict] = []
        self.metrics: Dict = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'profit_factor': 0.0
        }
        self.equity_curve: Optional[pd.Series] = None
        
    def add_trade(self, trade: Dict):
        """Add a trade to results"""
        self.trades.append(trade)
        
    def calculate_metrics(self):
        """Calculate performance metrics"""
        if not self.trades:
            return
            
        # Convert trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['profit'] > 0])
        losing_trades = len(trades_df[trades_df['profit'] < 0])
        
        self.metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_profit': trades_df['profit'].sum(),
            'max_drawdown': self.calculate_max_drawdown(),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'profit_factor': self.calculate_profit_factor(trades_df)
        }
        
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        if self.equity_curve is None:
            return 0.0
            
        rolling_max = self.equity_curve.cummax()
        drawdown = self.equity_curve - rolling_max
        return abs(drawdown.min())
        
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.01) -> float:
        """Calculate Sharpe ratio of returns"""
        if self.equity_curve is None:
            return 0.0
            
        returns = self.equity_curve.pct_change().dropna()
        if len(returns) < 2:
            return 0.0
            
        excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
    def calculate_profit_factor(self, trades_df: pd.DataFrame) -> float:
        """Calculate profit factor"""
        if trades_df.empty:
            return 0.0
            
        gross_profit = trades_df[trades_df['profit'] > 0]['profit'].sum()
        gross_loss = abs(trades_df[trades_df['profit'] < 0]['profit'].sum())
        
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')

class Backtester:
    """Backtesting engine for trading strategies"""
    def __init__(self, data: pd.DataFrame, strategy: TradingStrategy, 
                 initial_capital: float = 10000.0, logger: Optional[Logger] = None):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.logger = logger or Logger("backtest.log")
        
        self.current_position = 0
        self.capital = initial_capital
        self.result = BacktestResult()
        
    def run(self):
        """Run backtest"""
        self.logger.log("Starting backtest...")
        
        # Inicializa a lista de equity com o capital inicial
        equity = []
        
        for i in range(len(self.data)):
            # Update strategy with current data
            current_data = self.data.iloc[:i+1]
            self.strategy.update(current_data)
            
            # Get trading signal
            signal = self.strategy.get_signal()
            
            if signal:
                self._process_signal(signal, current_data.index[-1], 
                                float(current_data['fechamento'].iloc[-1]))
            
            # Adiciona o valor atual do patrimônio à lista
            current_equity = self.capital
            if self.current_position > 0:
                current_equity += self.current_position * float(current_data['fechamento'].iloc[-1])
            equity.append(current_equity)
        
        # Cria a Series de equity usando o mesmo índice dos dados
        self.result.equity_curve = pd.Series(
            equity,
            index=self.data.index[:len(equity)]  # Garante que o índice tem o mesmo tamanho dos dados
        )
        
        self.result.calculate_metrics()
        self._log_results()
        return self.result
        
    def _process_signal(self, signal: str, timestamp: datetime, price: float):
        """Process trading signal"""
        if signal == "BUY" and self.current_position <= 0:
            # Calculate position size
            position_size = self.capital * 0.95 / price  # Use 95% of capital
            cost = position_size * price
            
            if cost <= self.capital:
                self.current_position = position_size
                self.capital -= cost
                
                self.result.add_trade({
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'price': price,
                    'quantity': position_size,
                    'cost': cost,
                    'profit': 0
                })
                
        elif signal == "SELL" and self.current_position > 0:
            # Close position
            revenue = self.current_position * price
            profit = revenue - self.result.trades[-1]['cost']
            self.capital += revenue
            
            self.result.add_trade({
                'timestamp': timestamp,
                'type': 'SELL',
                'price': price,
                'quantity': self.current_position,
                'cost': 0,
                'profit': profit
            })
            
            self.current_position = 0
            
    def _log_results(self):
        """Log backtest results"""
        self.logger.log("\nBacktest Results:")
        self.logger.log(f"Total Trades: {self.result.metrics['total_trades']}")
        self.logger.log(f"Win Rate: {self.result.metrics['win_rate']:.2%}")
        self.logger.log(f"Total Profit: {self.result.metrics['total_profit']:.2f}")
        self.logger.log(f"Max Drawdown: {self.result.metrics['max_drawdown']:.2f}")
        self.logger.log(f"Sharpe Ratio: {self.result.metrics['sharpe_ratio']:.2f}")
        self.logger.log(f"Profit Factor: {self.result.metrics['profit_factor']:.2f}")