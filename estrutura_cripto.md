# Description of modules:

## Interface Module
- BaseWindow: Base class for all windows
- MainWindow: Main application window
- CryptoManagerWindow: Cryptocurrency management window
- BacktestWindow: Backtesting interface
- BacktestTab: Backtesting tab in main window

## Components Module
- PriceFrame: Frame for price display and quantity calculation
- BalanceFrame: Frame for balance display
- MetricsFrame: Frame for trading metrics display
- CryptoTable: Table for cryptocurrency data display

## Trading Module
- TradingEngine: Main trading engine
- TradingStrategy: Base strategy class
- MovingAverageStrategy: Moving average crossover strategy
- DataFetcher: Market data fetching
- PositionManager: Position and order management


📁 crypto_trading/
├── 📁 src/
│   ├── 📁 interface/
│   │   ├── __init__.py
│   │   ├── base_window.py          # Classe base para janelas
│   │   ├── main_window.py          # Interface principal
│   │   ├── crypto_manager.py       # Interface de gerenciamento de moedas
│   │   └── components/             # Componentes reutilizáveis da UI
│   │       ├── __init__.py
│   │       ├── price_frame.py      # Frame de preços
│   │       ├── balance_frame.py    # Frame de saldo
│   │       ├── metrics_frame.py    # Frame de métricas
│   │       └── trading_frame.py    # Frame de trading
│   │
│   ├── 📁 trading/
│   │   ├── __init__.py
│   │   ├── trading_engine.py       # Lógica principal de trading
│   │   ├── strategy.py            # Estratégias de trading
│   │   ├── data_fetcher.py        # Busca de dados da Binance
│   │   └── position_manager.py    # Gerenciamento de posições
│   │
│   ├── 📁 database/
│   │   ├── __init__.py
│   │   ├── base.py                # Classe base de database
│   │   ├── crypto_db.py           # Gerenciamento de criptomoedas
│   │   └── trading_db.py          # Log de trades e sessões
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       ├── config.py              # Configurações e constantes
│       ├── logger.py              # Sistema de logging
│       └── binance_client.py      # Cliente Binance wrapper
│
├── 📁 tests/                      # Testes unitários
├── main.py                        # Ponto de entrada
├── requirements.txt
└── README.md