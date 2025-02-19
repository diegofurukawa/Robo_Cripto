# src/trading/trading_engine.py

from typing import Optional, Callable
from datetime import datetime
import threading
import time
from binance.client import Client
from ..database.crypto_db import CryptoDatabase
from ..utils.logger import Logger
from .data_fetcher import DataFetcher
from .strategy import MovingAverageStrategy
from .position_manager import PositionManager

class TradingEngine:
    """Main trading engine that coordinates all trading operations"""
    def __init__(self, api_key: str, api_secret: str, db: CryptoDatabase, logger: Logger):
        self.db = db
        self.logger = logger
        self.client = Client(api_key, api_secret)
        self.data_fetcher = DataFetcher(self.client)
        self.position_manager = PositionManager(self.client, self.logger)
        self.strategy = MovingAverageStrategy()
        
        self.trading_active = False
        self.current_trading_id = None
        self.trading_thread: Optional[threading.Thread] = None
        
    def start_trading_session(self, symbol: str, investment_value: float, quantity: float) -> bool:
        """Start a new trading session"""
        try:
            # Initialize trading session in database
            self.current_trading_id = self.db.start_trading_session(
                codigo_ativo=symbol,
                value_investido=investment_value,
                qtde_investida=quantity
            )
            
            if not self.current_trading_id:
                self.logger.log("Erro ao iniciar sessão de trading no banco de dados")
                return False
                
            self.trading_active = True
            self.trading_thread = threading.Thread(target=self._trading_loop)
            self.trading_thread.daemon = True
            self.trading_thread.start()
            
            self.logger.log(f"Sessão de trading iniciada - ID: {self.current_trading_id}")
            return True
            
        except Exception as e:
            self.logger.log(f"Erro ao iniciar trading: {str(e)}")
            return False
            
    def stop_trading_session(self) -> bool:
        """Stop the current trading session"""
        try:
            if self.current_trading_id:
                if self.db.stop_trading_session(self.current_trading_id):
                    self.logger.log(f"Sessão de trading {self.current_trading_id} finalizada")
                else:
                    self.logger.log("Erro ao finalizar sessão no banco de dados")
                    
            self.trading_active = False
            self.current_trading_id = None
            return True
            
        except Exception as e:
            self.logger.log(f"Erro ao parar trading: {str(e)}")
            return False
            
    def _trading_loop(self):
        """Main trading loop"""
        while self.trading_active:
            try:
                # Get market data
                market_data = self.data_fetcher.get_market_data(
                    symbol=self.position_manager.current_symbol,
                    interval=Client.KLINE_INTERVAL_1HOUR
                )
                
                # Update strategy and get signals
                self.strategy.update(market_data)
                signal = self.strategy.get_signal()
                
                # Execute trades based on signals
                if signal == "BUY" and not self.position_manager.has_position:
                    self.position_manager.open_position(
                        symbol=self.position_manager.current_symbol,
                        quantity=self.position_manager.calculate_position_size()
                    )
                elif signal == "SELL" and self.position_manager.has_position:
                    self.position_manager.close_position(
                        symbol=self.position_manager.current_symbol
                    )
                    
                # Wait for next iteration
                for minute in range(5, 0, -1):
                    if not self.trading_active:
                        break
                    self.logger.log(f"Próxima análise em {minute} minutos")
                    time.sleep(60)
                    
            except Exception as e:
                self.logger.log(f"Erro no loop de trading: {str(e)}")
                time.sleep(60)