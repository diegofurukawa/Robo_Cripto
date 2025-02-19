# main.py
from src.utils.config import Config
from src.utils.logger import Logger
from src.utils.binance_client import BinanceClient
from src.database.crypto_db import CryptoDatabase
from src.interface.main_window import MainWindow
from src.trading.trading_engine import TradingEngine

def main():
    try:
        # Initialize configuration
        config = Config()
        
        # Initialize logger
        logger = Logger(config.database.log_file)
        
        # Initialize database
        db = CryptoDatabase(config.database.db_name)
        
        # Initialize Binance client
        binance_client = BinanceClient(**config.binance_config)
        
        # Initialize trading engine
        trading_engine = TradingEngine(
            api_key=config.api_key,
            api_secret=config.api_secret,
            db=db,
            logger=logger
        )
        
        # Initialize and run main window
        main_window = MainWindow()
        main_window.run()
        
    except Exception as e:
        print(f"Error initializing application: {str(e)}")
        raise

if __name__ == "__main__":
    main()