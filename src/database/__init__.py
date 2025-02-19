# src/database/__init__.py
from .base import BaseDatabase, DatabaseError
from .crypto_db import CryptoDatabase

__all__ = ['BaseDatabase', 'DatabaseError', 'CryptoDatabase']