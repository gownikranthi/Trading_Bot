import argparse
import sys
from binance.enums import *
from src.utils.binance_client import BinanceClient
from src.utils.logger import logger
from src.utils.validation import validate_input

def place_grid_orders(client, symbol, lower_bound, upper_bound, num_levels, quantity_per_level):
    """
    Places a simple grid trading strategy.
    This function places a series of limit buy and sell orders at
    evenly spaced price intervals.
    Note: This is a static grid. A dynamic grid would require
    cancellation and re-placement of orders as they are filled.
    :param client: BinanceClient instance.
    :param symbol: Trading symbol.
    :param lower_bound: The lowest price of the grid.
    :param upper_bound: The highest price of the grid.
    :param num_levels: The number of grid levels.
    :param quantity_per_level: The quantity for each order.
    """
    try:
        if num_levels <= 1:
            logger.error("Number of grid levels must be greater than 1.")
            return

        price_step = (upper_bound - lower_bound) / (num_levels - 1)
        orders = []

        for i in range(num_levels):
            # Place buy orders below a central point and sell orders above
            order_price = lower_bound + i * price_step
            order_side = "BUY" if order_price < (lower_bound + upper_bound) / 2 else "SELL"

            if not validate_input(client, symbol, quantity_per_level, order_price):
                logger.error(f"Grid order validation failed at price {order_price}. Aborting grid placement.")
                return

            try:
                order = client.get_client().futures_create_order(
                    symbol=symbol,
                    side=order_side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    quantity=quantity_per_level,
                    price=order_price,
                    timeInForce="GTC"
                )
                orders.append(order)
                logger.info(
                    f"Grid order placed: {order_side} {quantity_per_level} at {order_price}",
                    extra={'details': order}
                )
            except Exception as e:
                client.handle_error(e)
                logger.warning(f"Failed to place grid order at price {order_price}. Continuing to next level.")

        logger.info("Static grid strategy orders placed successfully.", extra={'details': {'orders_count': len(orders)}})
        return orders
    except Exception as e:
        client.handle_error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place a static grid trading strategy on Binance Futures.")
    parser.add_argument("symbol", type=str, help="The trading symbol, e.g., 'BTCUSDT'")
    parser.add_argument("lower_bound", type=float, help="The lower price boundary of the grid")
    parser.add_argument("upper_bound", type=float, help="The upper price boundary of the grid")
    parser.add_argument("num_levels", type=int, help="The number of price levels in the grid")
    parser.add_argument("quantity_per_level", type=float, help="The quantity for each order in the grid")
    parser.add_argument("--mainnet", action="store_true", help="Use Binance Mainnet instead of Testnet (DANGEROUS)")

    args = parser.parse_args()

    if args.mainnet:
        response = input("WARNING: You are about to use the Binance Mainnet. Type 'yes' to proceed: ")
        if response.lower() != 'yes':
            print("Mainnet operation cancelled.")
            sys.exit(0)

    try:
        binance_client = BinanceClient(mainnet=args.mainnet)
        place_grid_orders(binance_client, args.symbol, args.lower_bound, args.upper_bound, args.num_levels, args.quantity_per_level)
    except Exception:
        sys.exit(1)
