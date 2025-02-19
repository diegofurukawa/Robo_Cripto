# src/interface/__init__.py
"""
Interface module for the crypto trading application.
Provides all GUI components and windows.
"""

from .base_window import BaseWindow
from .main_window import MainWindow
from .crypto_manager import CryptoManagerWindow
from .backtest_window import BacktestWindow, BacktestTab

__all__ = [
    'BaseWindow',
    'MainWindow',
    'CryptoManagerWindow',
    'BacktestWindow',
    'BacktestTab'
]