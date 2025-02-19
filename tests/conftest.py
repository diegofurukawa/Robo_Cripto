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
    client = Mock()
    
    # Add necessary constants that would be in the real client
    client.SIDE_BUY = 'BUY'
    client.SIDE_SELL = 'SELL'
    client.ORDER_TYPE_MARKET = 'MARKET'
    
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