# src/trading/strategy.py

import pandas as pd
from typing import Literal, Optional

class TradingStrategy:
    """Base class for trading strategies"""
    def update(self, data: pd.DataFrame) -> None:
        raise NotImplementedError
        
    def get_signal(self) -> Optional[Literal["BUY", "SELL"]]:
        raise NotImplementedError

class MovingAverageStrategy(TradingStrategy):
    """Moving average crossover strategy"""
    def __init__(self, fast_period: int = 7, slow_period: int = 40):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.data: Optional[pd.DataFrame] = None
        
    def update(self, data: pd.DataFrame) -> None:
        """Update strategy with new market data"""
        self.data = data
        self.data["media_rapida"] = self.data["fechamento"].rolling(window=self.fast_period).mean()
        self.data["media_devagar"] = self.data["fechamento"].rolling(window=self.slow_period).mean()
        
    def get_signal(self) -> Optional[Literal["BUY", "SELL"]]:
        """Generate trading signal based on strategy"""
        if self.data is None or len(self.data) < self.slow_period:
            return None
            
        ultima_media_rapida = self.data["media_rapida"].iloc[-1]
        ultima_media_devagar = self.data["media_devagar"].iloc[-1]
        
        if ultima_media_rapida > ultima_media_devagar:
            return "BUY"
        elif ultima_media_rapida < ultima_media_devagar:
            return "SELL"
            
        return None