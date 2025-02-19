# tests/test_backtest.py
import pytest
import pandas as pd
from src.backtesting.engine import Backtester
from src.trading.strategy import MovingAverageStrategy

def test_backtester(mock_binance_client):
    """Test backtesting engine"""
    # Get test data
    data = mock_binance_client.get_historical_klines("BTCBRL", "1h")
    
    # Create and run backtest
    strategy = MovingAverageStrategy()
    backtester = Backtester(data, strategy, initial_capital=10000.0)
    result = backtester.run()
    
    # Verify results
    assert result.metrics['total_trades'] >= 0
    assert 0 <= result.metrics['win_rate'] <= 1
    assert isinstance(result.metrics['total_profit'], float)