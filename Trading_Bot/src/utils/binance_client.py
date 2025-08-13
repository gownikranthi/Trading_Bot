import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from src.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

class BinanceClient:
    """
    A wrapper class for the Binance Client to handle API key loading,
    environment switching, and common exceptions.
    """
    def __init__(self, mainnet=False):
        """
        Initializes the Binance client.
        :param mainnet: Boolean to specify if Mainnet should be used.
                        Defaults to False (Testnet).
        """
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")

        if not self.api_key or not self.api_secret:
            logger.error(
                "API keys not found in .env file. Please check your .env configuration.",
                extra={'details': 'Missing API_KEY or API_SECRET'}
            )
            raise ValueError("API keys not found.")

        # Set the Testnet vs Mainnet URL based on the flag
        if mainnet:
            self.client = Client(self.api_key, self.api_secret)
        else:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            logger.info("Using Binance Futures TESTNET.", extra={'details': 'Testnet mode enabled.'})

    def get_client(self):
        """
        Returns the configured Binance Client instance.
        """
        return self.client

    def handle_error(self, e):
        """
        A centralized error handler for Binance exceptions.
        Logs the error with a full stack trace.
        """
        if isinstance(e, (BinanceAPIException, BinanceRequestException)):
            logger.error(
                f"Binance API Error: {e.status_code} - {e.message}",
                exc_info=True,
                extra={'details': {'status_code': e.status_code, 'message': e.message}}
            )
        else:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)

