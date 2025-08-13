import unittest
from unittest.mock import Mock, patch
import sys

# Add the src directory to the path so we can import modules
sys.path.insert(0, './src')
from limit_orders import place_limit_order
from utils.binance_client import BinanceClient
from utils.validation import validate_input

class MockResponse:
    """Mock a successful Binance API response."""
    def __init__(self, status_code=200, order_id=456):
        self.status_code = status_code
        self.orderId = order_id
        self.status = "NEW"
    def __getitem__(self, key):
        return getattr(self, key)

class TestLimitOrders(unittest.TestCase):
    def setUp(self):
        # Mock the BinanceClient and its methods
        self.mock_client = Mock()
        self.mock_binance_client = self.mock_client.get_client()
        self.mock_binance_client.futures_create_order = Mock(return_value=MockResponse())

    @patch('src.limit_orders.validate_input', return_value=True)
    def test_limit_order_success(self, mock_validate_input):
        """Test a successful limit order placement."""
        order = place_limit_order(self.mock_client, 'BTCUSDT', 'SELL', 0.001, 68000)
        self.assertIsNotNone(order)
        self.assertEqual(order.orderId, 456)
        self.mock_binance_client.futures_create_order.assert_called_once()
        self.assertTrue(mock_validate_input.called)

    @patch('src.limit_orders.validate_input', return_value=False)
    def test_limit_order_validation_failure(self, mock_validate_input):
        """Test that no order is placed if validation fails."""
        order = place_limit_order(self.mock_client, 'BTCUSDT', 'SELL', 0.001, 68000.123) # Invalid price
        self.assertIsNone(order)
        self.assertFalse(self.mock_binance_client.futures_create_order.called)
        self.assertTrue(mock_validate_input.called)


if __name__ == '__main__':
    unittest.main()
