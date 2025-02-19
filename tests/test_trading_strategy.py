# tests/test_trading_strategy.py
import pytest
import pandas as pd
from src.trading.strategy import MovingAverageStrategy

def test_moving_average_strategy():
    """Test moving average strategy signals"""
    # Create test data
    data = pd.DataFrame({
        'fechamento': [100, 110, 120, 115, 105, 95, 85, 80, 90, 100]
    })
    
    strategy = MovingAverageStrategy(fast_period=2, slow_period=5)
    strategy.update(data)
    signal = strategy.get_signal()
    
    assert signal in [None, "BUY", "SELL"]