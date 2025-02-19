# tests/test_trading.py

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from src.trading.strategy import MovingAverageStrategy
from src.trading.position_manager import PositionManager

class TestMovingAverageStrategy(unittest.TestCase):
    """Test cases for MovingAverageStrategy"""
    
    def setUp(self):
        """Set up test strategy"""
        self.strategy = MovingAverageStrategy()
        
    def test_strategy_signals(self):
        """Test trading signals generation"""
        # Create test data
        data = pd.DataFrame({
            'fechamento': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        })
        
        # Update strategy with data
        self.strategy.update(data)
        
        # Get signal
        signal = self.strategy.get_signal()
        
        # Signal should be None or one of "BUY"/"SELL"
        self.assertIn(signal, [None, "BUY", "SELL"])

class TestPositionManager(unittest.TestCase):
    """Test cases for PositionManager"""
    
    def setUp(self):
        """Set up test position manager"""
        self.mock_client = Mock()
        self.mock_logger = Mock()
        self.position_manager = PositionManager(self.mock_client, self.mock_logger)
        
    def test_position_adjustments(self):
        """Test position size adjustments"""
        # Test quantity adjustment
        adjusted = self.position_manager.adjust_quantity(0.12345678, 0.00100000)
        self.assertEqual(adjusted, 0.123)
        
        # Test with minimum quantity
        adjusted = self.position_manager.adjust_quantity(0.0001, 0.001)
        self.assertEqual(adjusted, 0.0)