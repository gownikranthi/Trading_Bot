import argparse
import sys
from binance.enums import *
from src.utils.binance_client import BinanceClient
from src.utils.logger import logger
from src.utils.validation import validate_input

def place_market_order(client, symbol, side, quantity):
    """
    Places a market order on Binance Futures.
    :param client: BinanceClient instance.
    :param symbol: Trading symbol (e.g., 'BTCUSDT').
    :param side: 'BUY' or 'SELL'.
    :param quantity: The order quantity.
    """
    try:
        # Validate inputs before placing the order
        if not validate_input(client, symbol, quantity):
            logger.error("Input validation failed, aborting order placement.")
            return

        order = client.get_client().futures_create_order(
            symbol=symbol,
            side=side,
            type=FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity
        )
        logger.info("Market order placed successfully.", extra={'details': order})
        return order
    except Exception as e:
        client.handle_error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place a market order on Binance Futures.")
    parser.add_argument("symbol", type=str, help="The trading symbol, e.g., 'BTCUSDT'")
    parser.add_argument("side", type=str, choices=["BUY", "SELL"], help="Order side: 'BUY' or 'SELL'")
    parser.add_argument("quantity", type=float, help="The quantity of the asset to trade")
    parser.add_argument("--mainnet", action="store_true", help="Use Binance Mainnet instead of Testnet (DANGEROUS)")

    args = parser.parse_args()

    # Safety check for mainnet
    if args.mainnet:
        response = input("WARNING: You are about to use the Binance Mainnet. Type 'yes' to proceed: ")
        if response.lower() != 'yes':
            print("Mainnet operation cancelled.")
            sys.exit(0)

    try:
        binance_client = BinanceClient(mainnet=args.mainnet)
        place_market_order(binance_client, args.symbol, args.side, args.quantity)
    except Exception:
        # Errors are already logged within BinanceClient.handle_error
        sys.exit(1)