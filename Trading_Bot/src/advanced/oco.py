import argparse
import sys
from src.utils.binance_client import BinanceClient
from src.utils.logger import logger
from src.utils.validation import validate_input

def place_oco_order(client, symbol, side, quantity, take_profit, stop_loss):
    """
    Places a simulated One-Cancels-the-Other (OCO) order.
    Binance Futures API does not have a native OCO type, so we
    simulate it by placing a limit order, a take-profit order, and a stop-loss order.
    The `binance-python` library can help with this.
    For this example, we will place a limit order and a stop-market order
    for simplicity. A true OCO would require order cancellation logic.
    :param client: BinanceClient instance.
    :param symbol: Trading symbol.
    :param side: 'BUY' or 'SELL'.
    :param quantity: Order quantity.
    :param take_profit: Take profit price (limit order).
    :param stop_loss: Stop loss price (market order).
    """
    try:
        # Validate inputs
        if not validate_input(client, symbol, quantity, take_profit) or not validate_input(client, symbol, quantity, stop_loss):
            logger.error("Input validation failed, aborting OCO order placement.")
            return

        client_instance = client.get_client()

        # Place a Take Profit Limit Order
        tp_side = "SELL" if side == "BUY" else "BUY"
        tp_order = client_instance.futures_create_order(
            symbol=symbol,
            side=tp_side,
            type='TAKE_PROFIT',
            quantity=quantity,
            stopPrice=take_profit
        )

        # Place a Stop Market Order
        sl_side = "SELL" if side == "BUY" else "BUY"
        sl_order = client_instance.futures_create_order(
            symbol=symbol,
            side=sl_side,
            type='STOP',
            quantity=quantity,
            stopPrice=stop_loss
        )

        logger.info(
            "OCO (simulated) orders placed successfully.",
            extra={'details': {'take_profit_order': tp_order, 'stop_loss_order': sl_order}}
        )
        return tp_order, sl_order
    except Exception as e:
        client.handle_error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Place a simulated OCO order on Binance Futures.")
    parser.add_argument("symbol", type=str, help="The trading symbol, e.g., 'BTCUSDT'")
    parser.add_argument("side", type=str, choices=["BUY", "SELL"], help="Order side: 'BUY' or 'SELL'")
    parser.add_argument("quantity", type=float, help="The quantity of the asset to trade")
    parser.add_argument("--tp", type=float, required=True, help="Take profit price")
    parser.add_argument("--sl", type=float, required=True, help="Stop loss price")
    parser.add_argument("--mainnet", action="store_true", help="Use Binance Mainnet instead of Testnet (DANGEROUS)")

    args = parser.parse_args()

    if args.mainnet:
        response = input("WARNING: You are about to use the Binance Mainnet. Type 'yes' to proceed: ")
        if response.lower() != 'yes':
            print("Mainnet operation cancelled.")
            sys.exit(0)

    try:
        binance_client = BinanceClient(mainnet=args.mainnet)
        place_oco_order(binance_client, args.symbol, args.side, args.quantity, args.tp, args.sl)
    except Exception:
        sys.exit(1)