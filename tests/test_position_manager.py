# tests/test_position_manager.py
import pytest
from src.trading.position_manager import PositionManager

def test_position_manager(mock_binance_client, test_logger):
    """Test position manager operations"""
    manager = PositionManager(mock_binance_client, test_logger)
    
    # Configure o mock do cliente para retornar informações do símbolo
    mock_binance_client.get_symbol_info.return_value = {
        'filters': [
            {
                'filterType': 'LOT_SIZE',
                'minQty': '0.001',
                'maxQty': '100000.0',
                'stepSize': '0.001'
            }
        ]
    }
    
    # Test quantity adjustment
    adjusted_qty = manager.adjust_quantity(0.12345678, 0.001)
    assert adjusted_qty == 0.123
    
    # Configure o mock para simular uma ordem bem-sucedida
    mock_binance_client.create_order.return_value = {
        'orderId': 1234,
        'status': 'FILLED'
    }
    
    # Test position opening
    success = manager.open_position("BTCBRL", 0.1)
    assert success == True
    assert manager.has_position == True
    assert manager.position_size == 0.1
    assert manager.current_symbol == "BTCBRL"

    # Verify that create_order was called with correct parameters
    mock_binance_client.create_order.assert_called_once_with(
        symbol="BTCBRL",
        side=mock_binance_client.SIDE_BUY,
        type=mock_binance_client.ORDER_TYPE_MARKET,
        quantity=0.1
    )