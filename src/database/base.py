# src/database/base.py

import sqlite3
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager
from datetime import datetime

class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class BaseDatabase:
    """Base class for database operations"""
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.create_tables()
        
    @contextmanager
    def get_cursor(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise DatabaseError(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def execute_query(self, query: str, params: Tuple = ()) -> Optional[List[Tuple]]:
        """Execute a query and return results if any"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description is not None:
                return cursor.fetchall()
            return None
            
    def create_tables(self) -> None:
        """Create database tables - to be implemented by child classes"""
        raise NotImplementedError