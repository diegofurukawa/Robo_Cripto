# tests/test_integration.py
import pytest
from src.trading.trading_engine import TradingEngine
from src.utils.config import Config

def test_trading_flow(mock_binance_client, test_db, test_logger):
    """Integration test for trading flow"""
    # Setup
    test_db.add_crypto("Bitcoin", "BTCBRL", True)
    
    engine = TradingEngine(
        api_key="test",
        api_secret="test",
        db=test_db,
        logger=test_logger
    )
    engine.client = mock_binance_client
    
    # Start trading session
    session_id = engine.start_trading_session("BTCBRL", 10000.0, 0.1)
    assert session_id is not None
    
    # Run some iterations
    engine._trading_loop()
    
    # Stop trading
    assert engine.stop_trading_session() == True