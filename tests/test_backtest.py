# tests/test_backtest.py
import pandas as pd
import numpy as np
import pytest
from src.backtesting.engine import Backtester
from src.trading.strategy import MovingAverageStrategy

def test_backtester(mock_binance_client):
    """Test backtesting engine"""
    # Criar dados de teste como DataFrame
    test_data = pd.DataFrame({
        'tempo_abertura': pd.date_range(start='2024-01-01', periods=100, freq='1H'),
        'abertura': np.random.random(100) * 100 + 100,
        'maxima': np.random.random(100) * 100 + 150,
        'minima': np.random.random(100) * 100 + 50,
        'fechamento': np.random.random(100) * 100 + 100,
        'volume': np.random.random(100) * 1000
    })
    
    # Configurar o mock para retornar os dados de teste
    mock_binance_client.get_historical_klines.return_value = test_data
    
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
    assert isinstance(result.equity_curve, pd.Series)
    assert len(result.equity_curve) > 0