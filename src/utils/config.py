# src/utils/config.py
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    update_interval: int = 300  # 5 minutes in seconds
    fast_ma_period: int = 7
    slow_ma_period: int = 40
    default_investment: float = 100.0

@dataclass
class DatabaseConfig:
    """Database configuration parameters"""
    db_name: str = "crypto.db"
    log_file: str = "trading_log.csv"

class Config:
    """Central configuration management"""
    def __init__(self):
        self.load_environment()
        self.trading = TradingConfig()
        self.database = DatabaseConfig()
        
    def load_environment(self) -> None:
        """Load environment variables"""
        load_dotenv()
        
        # API credentials
        self.api_key = os.getenv("KEY_BINANCE")
        self.api_secret = os.getenv("SECRET_BINANCE")
        
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not found in environment variables")
            
    @property
    def binance_config(self) -> Dict[str, str]:
        """Get Binance API configuration"""
        return {
            "api_key": self.api_key,
            "api_secret": self.api_secret
        }