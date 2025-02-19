# src/database/crypto_db.py

from typing import List, Tuple, Optional
from datetime import datetime
from .base import BaseDatabase, DatabaseError

class CryptoDatabase(BaseDatabase):
    """Database operations for cryptocurrency management"""
    def create_tables(self) -> None:
        """Create necessary tables for cryptocurrency management"""
        queries = [
            # Cryptocurrencies table
            """
            CREATE TABLE IF NOT EXISTS cryptocurrencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL UNIQUE,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
            """,
            # Trading sessions table
            """
            CREATE TABLE IF NOT EXISTS trading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                crypto_code TEXT NOT NULL,
                status INTEGER DEFAULT 1,
                investment_value DECIMAL(15,8) NOT NULL,
                investment_quantity DECIMAL(15,8) NOT NULL,
                FOREIGN KEY (crypto_code) REFERENCES cryptocurrencies(code)
            )
            """,
            # Trading operations table
            """
            CREATE TABLE IF NOT EXISTS trading_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                operation_type TEXT NOT NULL,
                crypto_code TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                price DECIMAL(15,8) NOT NULL,
                quantity DECIMAL(15,8) NOT NULL,
                total_value DECIMAL(15,8) NOT NULL,
                FOREIGN KEY (session_id) REFERENCES trading_sessions(id),
                FOREIGN KEY (crypto_code) REFERENCES cryptocurrencies(code)
            )
            """
        ]
        
        for query in queries:
            self.execute_query(query)
    
    # Cryptocurrency Management Methods
    def add_crypto(self, name: str, code: str, is_active: bool = True) -> bool:
        """Add a new cryptocurrency"""
        try:
            self.execute_query(
                "INSERT INTO cryptocurrencies (name, code, is_active) VALUES (?, ?, ?)",
                (name, code, is_active)
            )
            return True
        except DatabaseError:
            return False
            
    def update_crypto(self, code: str, name: Optional[str] = None, 
                     is_active: Optional[bool] = None) -> bool:
        """Update cryptocurrency information"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(is_active)
            
        if not updates:
            return False
            
        params.append(code)
        query = f"UPDATE cryptocurrencies SET {', '.join(updates)} WHERE code = ?"
        
        try:
            self.execute_query(query, tuple(params))
            return True
        except DatabaseError:
            return False
            
    def get_crypto(self, code: str) -> Optional[Tuple]:
        """Get cryptocurrency by code"""
        try:
            result = self.execute_query(
                "SELECT * FROM cryptocurrencies WHERE code = ?",
                (code,)
            )
            return result[0] if result else None
        except DatabaseError:
            return None
            
    def get_all_cryptos(self) -> List[Tuple]:
        """Get all cryptocurrencies"""
        try:
            result = self.execute_query("SELECT * FROM cryptocurrencies ORDER BY name")
            return result if result else []
        except DatabaseError:
            return []
            
    def get_active_cryptos(self) -> List[Tuple]:
        """Get all active cryptocurrencies"""
        try:
            result = self.execute_query(
                "SELECT * FROM cryptocurrencies WHERE is_active = 1 ORDER BY name"
            )
            return result if result else []
        except DatabaseError:
            return []
            
    # Trading Session Methods
    def start_trading_session(self, crypto_code: str, 
                            investment_value: float, 
                            investment_quantity: float) -> Optional[int]:
        """Start a new trading session"""
        try:
            result = self.execute_query(
                """
                INSERT INTO trading_sessions 
                (start_time, crypto_code, investment_value, investment_quantity)
                VALUES (CURRENT_TIMESTAMP, ?, ?, ?)
                """,
                (crypto_code, investment_value, investment_quantity)
            )
            # Get the last inserted id
            session_id = self.execute_query("SELECT last_insert_rowid()")[0][0]
            return session_id
        except DatabaseError:
            return None
            
    def stop_trading_session(self, session_id: int) -> bool:
        """Stop a trading session"""
        try:
            self.execute_query(
                """
                UPDATE trading_sessions 
                SET end_time = CURRENT_TIMESTAMP, status = 0
                WHERE id = ? AND status = 1
                """,
                (session_id,)
            )
            return True
        except DatabaseError:
            return False
            
    def get_active_session(self, crypto_code: str) -> Optional[Tuple]:
        """Get active trading session for a cryptocurrency"""
        try:
            result = self.execute_query(
                """
                SELECT * FROM trading_sessions 
                WHERE crypto_code = ? AND status = 1
                ORDER BY start_time DESC LIMIT 1
                """,
                (crypto_code,)
            )
            return result[0] if result else None
        except DatabaseError:
            return None
            
    # Trading Operations Methods
    def add_operation(self, session_id: int, operation_type: str,
                     crypto_code: str, price: float, quantity: float) -> bool:
        """Add a new trading operation"""
        try:
            total_value = price * quantity
            self.execute_query(
                """
                INSERT INTO trading_operations 
                (session_id, operation_type, crypto_code, price, quantity, total_value)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, operation_type, crypto_code, price, quantity, total_value)
            )
            return True
        except DatabaseError:
            return False
            
    def get_session_operations(self, session_id: int) -> List[Tuple]:
        """Get all operations for a trading session"""
        try:
            result = self.execute_query(
                "SELECT * FROM trading_operations WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            )
            return result if result else []
        except DatabaseError:
            return []
            
    def get_session_summary(self, session_id: int) -> Optional[dict]:
        """Get summary of a trading session"""
        try:
            operations = self.get_session_operations(session_id)
            if not operations:
                return None
                
            total_buy = 0
            total_sell = 0
            
            # Calcula totais de compra e venda
            for op in operations:
                value = op[5] * op[6]  # preço * quantidade
                if op[2] == "COMPRA":
                    total_buy += value
                elif op[2] == "VENDA":
                    total_sell += value
            
            return {
                "total_operations": len(operations),
                "total_buy": total_buy,
                "total_sell": total_sell,
                "profit": total_sell - total_buy  # Lucro é venda - compra
            }
        except DatabaseError:
            return None
            
    def get_trading_history(self, crypto_code: Optional[str] = None) -> List[Tuple]:
        """Get trading history, optionally filtered by crypto"""
        try:
            query = "SELECT * FROM trading_sessions ORDER BY start_time DESC"
            params = ()
            
            if crypto_code:
                query = "SELECT * FROM trading_sessions WHERE crypto_code = ? ORDER BY start_time DESC"
                params = (crypto_code,)
                
            result = self.execute_query(query, params)
            return result if result else []
        except DatabaseError:
            return []