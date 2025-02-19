# tests/test_database.py

import unittest
import sqlite3
import os
from datetime import datetime
from src.database.crypto_db import CryptoDatabase
from src.database.base import DatabaseError

class TestCryptoDatabase(unittest.TestCase):
    """Test cases for CryptoDatabase"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = "test_crypto.db"
        self.db = CryptoDatabase(self.test_db)
        
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_add_crypto(self):
        """Test adding a new cryptocurrency"""
        # Test successful addition
        self.assertTrue(self.db.add_crypto("Bitcoin", "BTCBRL", True))
        
        # Test duplicate code
        self.assertFalse(self.db.add_crypto("Bitcoin Copy", "BTCBRL", True))
        
        # Verify the added crypto
        crypto = self.db.get_crypto("BTCBRL")
        self.assertIsNotNone(crypto)
        self.assertEqual(crypto[1], "Bitcoin")
        
    def test_get_active_cryptos(self):
        """Test retrieving active cryptocurrencies"""
        # Add test data
        self.db.add_crypto("Bitcoin", "BTCBRL", True)
        self.db.add_crypto("Ethereum", "ETHBRL", True)
        self.db.add_crypto("Litecoin", "LTCBRL", False)
        
        # Get active cryptos
        active_cryptos = self.db.get_active_cryptos()
        
        # Verify results
        self.assertEqual(len(active_cryptos), 2)
        self.assertIn("BTCBRL", [crypto[2] for crypto in active_cryptos])
        self.assertIn("ETHBRL", [crypto[2] for crypto in active_cryptos])
        self.assertNotIn("LTCBRL", [crypto[2] for crypto in active_cryptos])
        
    def test_trading_session(self):
        """Test trading session operations"""
        # Add test crypto
        self.db.add_crypto("Bitcoin", "BTCBRL", True)
        
        # Start session
        session_id = self.db.start_trading_session("BTCBRL", 1000.0, 0.05)
        self.assertIsNotNone(session_id)
        
        # Add operations
        # Compra: 0.05 BTC a 20000.0 = 1000.0 BRL
        self.assertTrue(self.db.add_operation(
            session_id, "COMPRA", "BTCBRL", 20000.0, 0.05
        ))
        
        # Venda: 0.05 BTC a 21000.0 = 1050.0 BRL (lucro de 50.0)
        self.assertTrue(self.db.add_operation(
            session_id, "VENDA", "BTCBRL", 21000.0, 0.05
        ))
        
        # Get session summary
        summary = self.db.get_session_summary(session_id)
        self.assertIsNotNone(summary)
        self.assertEqual(summary["total_operations"], 2)
        
        # Verifica o lucro: 1050.0 - 1000.0 = 50.0
        self.assertTrue(summary["profit"] > 0)
        self.assertEqual(summary["profit"], 50.0)