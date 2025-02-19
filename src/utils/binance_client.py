# src/utils/binance_client.py
from typing import Dict, Any, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
from decimal import Decimal
import pandas as pd

class BinanceClient:
    """Wrapper for Binance API client with additional functionality"""
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        
    def get_account_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        """Get account balance for specific asset or all assets"""
        try:
            account = self.client.get_account()
            balances = {}
            
            for balance in account["balances"]:
                if float(balance["free"]) > 0 or float(balance["locked"]) > 0:
                    if asset and balance["asset"] != asset:
                        continue
                    balances[balance["asset"]] = {
                        "free": float(balance["free"]),
                        "locked": float(balance["locked"])
                    }
                    
            return balances
            
        except BinanceAPIException as e:
            raise Exception(f"Error fetching balance: {str(e)}")
            
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            raise Exception(f"Error fetching price: {str(e)}")
            
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed symbol information"""
        try:
            info = self.client.get_symbol_info(symbol)
            filters = {
                filter["filterType"]: filter
                for filter in info["filters"]
            }
            
            return {
                "base_asset": info["baseAsset"],
                "quote_asset": info["quoteAsset"],
                "min_qty": float(filters["LOT_SIZE"]["minQty"]),
                "max_qty": float(filters["LOT_SIZE"]["maxQty"]),
                "step_size": float(filters["LOT_SIZE"]["stepSize"]),
                "min_notional": float(filters["MIN_NOTIONAL"]["minNotional"])
            }
        except BinanceAPIException as e:
            raise Exception(f"Error fetching symbol info: {str(e)}")
            
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = Client.ORDER_TYPE_MARKET
    ) -> Dict[str, Any]:
        """Place a new order"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity
            )
            return order
        except BinanceAPIException as e:
            raise Exception(f"Error placing order: {str(e)}")
            
    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get historical kline data"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines)
            df.columns = [
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ]
            
            # Convert timestamps
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
            
            # Convert prices to float
            price_columns = ["open", "high", "low", "close"]
            df[price_columns] = df[price_columns].astype(float)
            
            return df
            
        except BinanceAPIException as e:
            raise Exception(f"Error fetching historical data: {str(e)}")