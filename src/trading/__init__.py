# src/trading/__init__.py
"""
Trading module containing trading logic, strategy implementations,
and position management.
"""

from .trading_engine import TradingEngine
from .strategy import (
    TradingStrategy,
    MovingAverageStrategy
)
from .data_fetcher import DataFetcher
from .position_manager import PositionManager

__all__ = [
    'TradingEngine',
    'TradingStrategy',
    'MovingAverageStrategy',
    'DataFetcher',
    'PositionManager'
]

