import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime

class CryptoDatabase:
    def __init__(self, db_name: str = 'crypto.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        
    def create_tables(self) -> None:
        cursor = self.conn.cursor()
        
        # Original cryptocurrencies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cryptocurrencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )''')
        
        # New trading_log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trading_log (
            idTrading INTEGER PRIMARY KEY AUTOINCREMENT,
            startTrading DATETIME,
            stopTrading DATETIME,
            codigoAtivo TEXT NOT NULL,
            status INTEGER DEFAULT 1,
            valueInvestido DECIMAL(15,8),
            qtdeInvestida DECIMAL(15,8),
            FOREIGN KEY (codigoAtivo) REFERENCES cryptocurrencies(code)
        )''')
        
        # New entradas table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entradas (
            idEntrada INTEGER PRIMARY KEY AUTOINCREMENT,
            idTrading INTEGER NOT NULL,
            type TEXT NOT NULL,
            codigoAtivo TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            value DECIMAL(15,8),
            quantidade DECIMAL(15,8),
            FOREIGN KEY (idTrading) REFERENCES trading_log(idTrading),
            FOREIGN KEY (codigoAtivo) REFERENCES cryptocurrencies(code)
        )''')
        
        self.conn.commit()

    # Original cryptocurrency methods remain the same
    def add_crypto(self, name: str, code: str, is_active: bool = True) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO cryptocurrencies (name, code, is_active) VALUES (?, ?, ?)',
                (name, code, is_active)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def get_all_cryptos(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cryptocurrencies')
        return cursor.fetchall()
        
    def get_active_cryptos(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM cryptocurrencies WHERE is_active = 1')
        return cursor.fetchall()

    # New methods for trading_log
    def start_trading_session(self, codigo_ativo: str, value_investido: float, qtde_investida: float) -> int:
        """Start a new trading session and return its ID"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trading_log (startTrading, codigoAtivo, status, valueInvestido, qtdeInvestida)
            VALUES (CURRENT_TIMESTAMP, ?, 1, ?, ?)
        ''', (codigo_ativo, value_investido, qtde_investida))
        self.conn.commit()
        return cursor.lastrowid

    def stop_trading_session(self, trading_id: int) -> bool:
        """Stop an active trading session"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE trading_log 
            SET stopTrading = CURRENT_TIMESTAMP, status = 0
            WHERE idTrading = ? AND status = 1
        ''', (trading_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_active_trading_session(self, codigo_ativo: str) -> Optional[Tuple]:
        """Get the currently active trading session for a given asset"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trading_log 
            WHERE codigoAtivo = ? AND status = 1
            ORDER BY startTrading DESC LIMIT 1
        ''', (codigo_ativo,))
        return cursor.fetchone()

    # New methods for entradas
    def add_entrada(self, trading_id: int, type: str, codigo_ativo: str, 
                   value: float, quantidade: float) -> bool:
        """Add a new entrada (trade entry)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO entradas (idTrading, type, codigoAtivo, value, quantidade)
                VALUES (?, ?, ?, ?, ?)
            ''', (trading_id, type, codigo_ativo, value, quantidade))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_entradas_by_trading_id(self, trading_id: int) -> List[Tuple]:
        """Get all entradas for a specific trading session"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entradas WHERE idTrading = ?', (trading_id,))
        return cursor.fetchall()

    def get_trading_history(self, codigo_ativo: str = None) -> List[Tuple]:
        """Get trading history, optionally filtered by asset"""
        cursor = self.conn.cursor()
        if codigo_ativo:
            cursor.execute('''
                SELECT * FROM trading_log 
                WHERE codigoAtivo = ?
                ORDER BY startTrading DESC
            ''', (codigo_ativo,))
        else:
            cursor.execute('SELECT * FROM trading_log ORDER BY startTrading DESC')
        return cursor.fetchall()

    def __del__(self):
        self.conn.close()