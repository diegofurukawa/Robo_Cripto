# tests/test_position_manager.py
import pytest
from src.trading.position_manager import PositionManager

def test_position_manager(mock_binance_client, test_logger):
    """Test position manager operations"""
    manager = PositionManager(mock_binance_client, test_logger)
    
    # Test quantity adjustment
    adjusted_qty = manager.adjust_quantity(0.12345678, 0.001)
    assert adjusted_qty == 0.123
    
    # Test position opening
    success = manager.open_position("BTCBRL", 0.1)
    assert success == True
    assert manager.has_position == True