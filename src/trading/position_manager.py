# src/trading/position_manager.py

from decimal import Decimal
from typing import Optional, Dict, Any
from binance.client import Client
from ..utils.logger import Logger

class PositionManager:
    """Handle all position-related operations"""
    def __init__(self, client: Client, logger: Logger):
        self.client = client
        self.logger = logger
        self.current_symbol: Optional[str] = None
        self.has_position = False
        self.position_size: Optional[float] = None
        
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get trading rules for a symbol"""
        try:
            info = self.client.get_symbol_info(symbol)
            for filter in info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    return {
                        'min_qty': float(filter['minQty']),
                        'max_qty': float(filter['maxQty']),
                        'step_size': float(filter['stepSize'])
                    }
            return None
        except Exception as e:
            self.logger.log(f"Erro ao obter informações do símbolo: {str(e)}")
            return None
            
    def adjust_quantity(self, quantity: float, step_size: float) -> float:
        """Adjust quantity to match symbol's step size"""
        step_size_decimals = len(str(step_size).split('.')[-1])
        return float(("{:." + str(step_size_decimals) + "f}").format(quantity - (quantity % step_size)))
        
    def open_position(self, symbol: str, quantity: float) -> bool:
        """Open a new position"""
        try:
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return False
                
            adjusted_quantity = self.adjust_quantity(quantity, symbol_info['step_size'])
            
            if adjusted_quantity < symbol_info['min_qty']:
                self.logger.log(f"Quantidade muito pequena. Mínimo: {symbol_info['min_qty']}")
                return False
                
            if adjusted_quantity > symbol_info['max_qty']:
                self.logger.log(f"Quantidade muito grande. Máximo: {symbol_info['max_qty']}")
                return False
                
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=adjusted_quantity
            )
            
            self.has_position = True
            self.position_size = adjusted_quantity
            self.current_symbol = symbol
            
            self.logger.log(f"Posição aberta: {adjusted_quantity} {symbol}")
            return True
            
        except Exception as e:
            self.logger.log(f"Erro ao abrir posição: {str(e)}")
            return False
            
    def close_position(self, symbol: str) -> bool:
        """Close current position"""
        try:
            if not self.has_position or not self.position_size:
                return False
                
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=self.position_size
            )
            
            self.has_position = False
            self.position_size = None
            self.current_symbol = None
            
            self.logger.log(f"Posição fechada: {symbol}")
            return True
            
        except Exception as e:
            self.logger.log(f"Erro ao fechar posição: {str(e)}")
            return False