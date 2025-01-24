"""
Crypto Trading Bot - Módulo de trading automatizado para criptomoedas
------------------------------------------------------------

Este módulo fornece uma interface para trading automatizado de criptomoedas
usando a API da Binance.

Classes principais:
    - CryptoDatabase: Gerenciamento do banco de dados SQLite
    - CryptoTradingBot: Interface gráfica e lógica de trading
"""

# Importações principais
try:
    from .crypto_database import CryptoDatabase
    from .cripto_robot_interface import CryptoTradingBot, CryptoWindow
except ImportError as e:
    print(f"Erro ao importar componentes: {e}")
    raise

# Metadata do pacote
__title__ = 'Crypto Trading Bot'
__version__ = '1.0.0'
__author__ = 'Seu Nome'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024'

# Componentes públicos do módulo
__all__ = [
    'CryptoDatabase',
    'CryptoTradingBot',
    'CryptoWindow',
    '__version__',
]

# Verificação de dependências necessárias
def check_dependencies():
    """Verifica se todas as dependências necessárias estão instaladas"""
    required_packages = [
        'tkinter',
        'customtkinter',
        'pandas',
        'python-binance',
        'python-dotenv',
        'sqlite3'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(
            f"Pacotes necessários não encontrados: {', '.join(missing_packages)}. "
            "Por favor, instale-os usando 'pip install -r requirements.txt'"
        )

# Executa verificação de dependências na importação
try:
    check_dependencies()
except ImportError as e:
    print(f"Aviso: {e}")