# src/trading/data_fetcher.py

import pandas as pd
from binance.client import Client
from typing import Dict, Any

class DataFetcher:
    """Handle all market data fetching operations"""
    def __init__(self, client: Client):
        self.client = client
        
    def get_market_data(self, symbol: str, interval: str) -> pd.DataFrame:
        """Fetch and process market data"""
        candles = self.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=1000
        )
        
        df = pd.DataFrame(candles)
        df.columns = [
            "tempo_abertura", "abertura", "maxima", "minima",
            "fechamento", "volume", "tempo_fechamento",
            "moedas_negociadas", "numero_trades",
            "volume_ativo_base_compra", "volume_ativo_cotação", "-"
        ]
        
        # Process data
        df = df[["fechamento", "tempo_fechamento"]]
        df["tempo_fechamento"] = pd.to_datetime(df["tempo_fechamento"], unit="ms")
        df["tempo_fechamento"] = df["tempo_fechamento"].dt.tz_localize("UTC").dt.tz_convert("America/Sao_Paulo")
        df["fechamento"] = df["fechamento"].astype(float)
        
        return df