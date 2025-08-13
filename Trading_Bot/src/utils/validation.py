import sys
from binance.exceptions import BinanceAPIException
from src.utils.binance_client import BinanceClient
from src.utils.logger import logger

class ExchangeInfo:
    """
    A class to fetch and cache Binance exchange information.
    This avoids repeated API calls for validation.
    """
    _instance = None
    _info = None

    def __new__(cls, client):
        if cls._instance is None:
            cls._instance = super(ExchangeInfo, cls).__new__(cls)
            try:
                # Fetch exchange info and store it
                cls._info = client.futures_exchange_info()
            except (BinanceAPIException, Exception) as e:
                client.handle_error(e)
                sys.exit(1)
        return cls._instance

    def get_symbol_info(self, symbol):
        """
        Retrieves the symbol-specific information from the cached data.
        """
        if self._info:
            for s in self._info['symbols']:
                if s['symbol'] == symbol:
                    return s
        return None

def validate_input(client, symbol, quantity, price=None):
    """
    Validates a trading pair, quantity, and price against Binance's exchange information.
    :param client: The BinanceClient instance.
    :param symbol: The trading symbol (e.g., 'BTCUSDT').
    :param quantity: The order quantity.
    :param price: The order price (optional, for limit orders).
    :return: True if validation passes, False otherwise.
    """
    exchange_info = ExchangeInfo(client.get_client())
    symbol_info = exchange_info.get_symbol_info(symbol)

    if not symbol_info:
        logger.error(f"Invalid symbol: {symbol}", extra={'details': 'Symbol not found in exchange info.'})
        return False

    # Get filters for price and quantity validation
    price_filter = next((f for f in symbol_info['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
    lot_size_filter = next((f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'), None)

    if not price_filter or not lot_size_filter:
        logger.error(f"Could not retrieve filters for symbol: {symbol}", extra={'details': 'Missing price or lot size filter.'})
        return False

    min_qty = float(lot_size_filter['minQty'])
    max_qty = float(lot_size_filter['maxQty'])
    step_size = float(lot_size_filter['stepSize'])

    # Validate quantity
    if quantity < min_qty or quantity > max_qty:
        logger.error(
            f"Invalid quantity {quantity} for {symbol}. Min: {min_qty}, Max: {max_qty}",
            extra={'details': {'quantity': quantity, 'min': min_qty, 'max': max_qty}}
        )
        return False

    if (quantity - min_qty) % step_size != 0:
        logger.error(
            f"Invalid quantity step for {symbol}. Step size is {step_size}",
            extra={'details': {'quantity': quantity, 'stepSize': step_size}}
        )
        return False

    # Validate price if provided
    if price:
        min_price = float(price_filter['minPrice'])
        max_price = float(price_filter['maxPrice'])
        tick_size = float(price_filter['tickSize'])

        if price < min_price or price > max_price:
            logger.error(
                f"Invalid price {price} for {symbol}. Min: {min_price}, Max: {max_price}",
                extra={'details': {'price': price, 'min': min_price, 'max': max_price}}
            )
            return False

        if (price - min_price) % tick_size != 0:
            logger.error(
                f"Invalid price tick size for {symbol}. Tick size is {tick_size}",
                extra={'details': {'price': price, 'tickSize': tick_size}}
            )
            return False

    return True