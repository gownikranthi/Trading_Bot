import argparse
import sys
import time
from binance.enums import *
from src.utils.binance_client import BinanceClient
from src.utils.logger import logger
from src.utils.validation import validate_input

def place_twap_order(client, symbol, side, total_quantity, duration_minutes, interval_seconds):
    """
    Places a Time-Weighted Average Price (TWAP) order.
    This function breaks down a large order into smaller market orders
    placed over a specific time period.
    :param client: BinanceClient instance.
    :param symbol: Trading symbol.
    :param side: 'BUY' or 'SELL'.
    :param total_quantity: The total quantity to be traded.
    :param duration_minutes: The total duration for the TWAP in minutes.
    :param interval_seconds: The interval between smaller orders in seconds.
    """
    try:
        num_intervals = (duration_minutes * 60) // interval_seconds
        if num_intervals == 0:
            logger.error("Duration is too short for the given interval. No orders will be placed.")
            return

        quantity_per_order = total_quantity / num_intervals
        logger.info(
            f"Starting TWAP for {symbol}. Placing {num_intervals} orders of {quantity_per_order} every {interval_seconds} seconds.",
            extra={'details': {'total_qty': total_quantity, 'duration': duration_minutes, 'interval': interval_seconds}}
        )

        for i in range(int(num_intervals)):
            # Validate each sub-order's quantity
            if not validate_input(client, symbol, quantity_per_order):
                logger.error("TWAP sub-order validation failed. Aborting.")
                return

            try:
                order = client.get_client().futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=FUTURE_ORDER_TYPE_MARKET,
                    quantity=quantity_per_order
                )
                logger.info(
                    f"TWAP order {i+1}/{num_intervals} placed successfully.",
                    extra={'details': order}
                )
            except Exception as e:
                client.handle_error(e)
                # Continue placing orders even if one fails
                logger.warning("TWAP sub-order failed, continuing to next interval.")

            if i < num_intervals - 1:
                time.sleep(interval_seconds)

    except Exception as e:
        client.handle_error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place a TWAP order on Binance Futures.")
    parser.add_argument("symbol", type=str, help="The trading symbol, e.g., 'BTCUSDT'")
    parser.add_argument("side", type=str, choices=["BUY", "SELL"], help="Order side: 'BUY' or 'SELL'")
    parser.add_argument("total_quantity", type=float, help="The total quantity of the asset to trade")
    parser.add_argument("--duration", type=int, required=True, help="Total duration in minutes")
    parser.add_argument("--interval", type=int, default=60, help="Interval between orders in seconds (default: 60)")
    parser.add_argument("--mainnet", action="store_true", help="Use Binance Mainnet instead of Testnet (DANGEROUS)")

    args = parser.parse_args()

    if args.mainnet:
        response = input("WARNING: You are about to use the Binance Mainnet. Type 'yes' to proceed: ")
        if response.lower() != 'yes':
            print("Mainnet operation cancelled.")
            sys.exit(0)

    try:
        binance_client = BinanceClient(mainnet=args.mainnet)
        place_twap_order(binance_client, args.symbol, args.side, args.total_quantity, args.duration, args.interval)
    except Exception:
        sys.exit(1)
