# tests/conftest.py
import pytest
import os
from unittest.mock import Mock
import pandas as pd
from src.utils.binance_client import BinanceClient
from src.database.crypto_db import CryptoDatabase
from src.utils.logger import Logger

@pytest.fixture
def mock_binance_client():
    """Mock Binance client for testing"""
    client = Mock(spec=BinanceClient)
    
    # Mock historical data
    historical_data = pd.DataFrame({
        'open_time': pd.date_range(start='2024-01-01', periods=100, freq='1H'),
        'open': range(100, 200),
        'high': range(105, 205),
        'low': range(95, 195),
        'close': range(102, 202),
        'volume': [1000] * 100
    })
    
    client.get_historical_klines.return_value = historical_data
    client.get_current_price.return_value = 150.0
    
    return client

@pytest.fixture
def test_db():
    """Test database fixture"""
    db_name = "test_crypto.db"
    db = CryptoDatabase(db_name)
    yield db
    # Cleanup
    if os.path.exists(db_name):
        os.remove(db_name)

@pytest.fixture
def test_logger(tmp_path):
    """Test logger fixture"""
    log_file = tmp_path / "test.log"
    return Logger(str(log_file))