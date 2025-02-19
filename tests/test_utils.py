# tests/test_utils.py

import unittest
from unittest.mock import patch, MagicMock
import os
from src.utils.config import Config
from src.utils.logger import Logger

class TestConfig(unittest.TestCase):
    """Test cases for Config"""
    
    @patch.dict(os.environ, {
        'KEY_BINANCE': 'test_key',
        'SECRET_BINANCE': 'test_secret'
    })
    def test_config_loading(self):
        """Test configuration loading"""
        config = Config()
        
        self.assertEqual(config.api_key, 'test_key')
        self.assertEqual(config.api_secret, 'test_secret')
        
        binance_config = config.binance_config
        self.assertEqual(binance_config['api_key'], 'test_key')
        self.assertEqual(binance_config['api_secret'], 'test_secret')

class TestLogger(unittest.TestCase):
    """Test cases for Logger"""
    
    def setUp(self):
        """Set up test logger"""
        self.log_file = "test_log.txt"
        self.logger = Logger(self.log_file)
        
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            
    def test_logging(self):
        """Test logging functionality"""
        test_message = "Test log message"
        self.logger.log(test_message)
        
        # Verify message was logged to file
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            self.assertIn(test_message, log_content)

if __name__ == '__main__':
    unittest.main()
