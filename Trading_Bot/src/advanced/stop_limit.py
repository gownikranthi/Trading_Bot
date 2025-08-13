import argparse
import sys
from binance.enums import *
from src.utils.binance_client import BinanceClient
from src.utils.logger import logger
from src.utils.validation import validate_input

def place_stop_limit_order(client, symbol, side, quantity, stop_price, limit_price):
    """
    Places a stop-limit order. The limit order is placed once the stop price is reached.
    :param client: BinanceClient instance.
    :param symbol: Trading symbol.
    :param side: 'BUY' or 'SELL'.
    :param quantity: Order quantity.
    :param stop_price: The price at which the limit order will be triggered.
    :param limit_price: The price of the limit order itself.
    """
    try:
        # Validate inputs before placing the order
        if not validate_input(client, symbol, quantity, limit_price):
            logger.error("Input validation failed, aborting order placement.")
            return

        # Note: Stop-limit orders on futures require both stopPrice and price
        order = client.get_client().futures_create_order(
            symbol=symbol,
            side=side,
            type=FUTURE_ORDER_TYPE_STOP,
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
            timeInForce="GTC"
        )
        logger.info("Stop-Limit order placed successfully.", extra={'details': order})
        return order
    except Exception as e:
        client.handle_error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place a Stop-Limit order on Binance Futures.")
    parser.add_argument("symbol", type=str, help="The trading symbol, e.g., 'BTCUSDT'")
    parser.add_argument("side", type=str, choices=["BUY", "SELL"], help="Order side: 'BUY' or 'SELL'")
    parser.add_argument("quantity", type=float, help="The quantity of the asset to trade")
    parser.add_argument("--stop-price", type=float, required=True, help="The stop price to trigger the order")
    parser.add_argument("--limit-price", type=float, required=True, help="The price of the limit order")
    parser.add_argument("--mainnet", action="store_true", help="Use Binance Mainnet instead of Testnet (DANGEROUS)")

    args = parser.parse_args()

    if args.mainnet:
        response = input("WARNING: You are about to use the Binance Mainnet. Type 'yes' to proceed: ")
        if response.lower() != 'yes':
            print("Mainnet operation cancelled.")
            sys.exit(0)

    try:
        binance_client = BinanceClient(mainnet=args.mainnet)
        place_stop_limit_order(binance_client, args.symbol, args.side, args.quantity, args.stop_price, args.limit_price)
    except Exception:
        sys.exit(1)