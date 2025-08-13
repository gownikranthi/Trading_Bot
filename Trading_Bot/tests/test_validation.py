import unittest
from unittest.mock import Mock, MagicMock
import sys

# Add the src directory to the path so we can import modules
sys.path.insert(0, './src')
from utils.validation import validate_input, ExchangeInfo
from utils.binance_client import BinanceClient

class MockClient:
    """Mock for the BinanceClient to simulate API responses."""
    def futures_exchange_info(self):
        return {
            'symbols': [
                {
                    'symbol': 'BTCUSDT',
                    'filters': [
                        {'filterType': 'PRICE_FILTER', 'minPrice': '0.01', 'maxPrice': '100000', 'tickSize': '0.01'},
                        {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'}
                    ]
                }
            ]
        }
    def handle_error(self, e):
        pass # Do nothing in the mock

class TestValidation(unittest.TestCase):
    def setUp(self):
        # Create a mock Binance client and ExchangeInfo instance
        self.mock_client = Mock()
        self.mock_client.get_client.return_value = MockClient()
        self.mock_client.handle_error = MockClient().handle_error

    def test_valid_input(self):
        """Test with a valid symbol, quantity, and price."""
        self.assertTrue(validate_input(self.mock_client, 'BTCUSDT', 0.002, 65000.00))

    def test_invalid_symbol(self):
        """Test with an invalid symbol."""
        self.assertFalse(validate_input(self.mock_client, 'XYZUSDT', 0.002, 65000.00))

    def test_invalid_quantity_step(self):
        """Test with a quantity that doesn't match the step size."""
        self.assertFalse(validate_input(self.mock_client, 'BTCUSDT', 0.0025))

    def test_invalid_quantity_below_min(self):
        """Test with a quantity below the minimum allowed."""
        self.assertFalse(validate_input(self.mock_client, 'BTCUSDT', 0.0005))

    def test_invalid_price_tick(self):
        """Test with a price that doesn't match the tick size."""
        self.assertFalse(validate_input(self.mock_client, 'BTCUSDT', 0.002, 65000.001))

    def test_invalid_price_below_min(self):
        """Test with a price below the minimum allowed."""
        self.assertFalse(validate_input(self.mock_client, 'BTCUSDT', 0.002, 0.005))

if __name__ == '__main__':
    unittest.main()
