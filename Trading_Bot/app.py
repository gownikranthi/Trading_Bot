import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
import httpx
import openai
from dotenv import load_dotenv
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import your trading functions and utilities
from utils.binance_client import BinanceClient
from utils.logger import logger
from market_orders import place_market_order
from limit_orders import place_limit_order
from advanced.stop_limit import place_stop_limit_order
from advanced.oco import place_oco_order
from advanced.twap import place_twap_order
from advanced.grid_strategy import place_grid_orders

# Load environment variables for the OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow communication from your HTML file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Binance client globally
try:
    binance_client = BinanceClient(mainnet=False)
except ValueError:
    logger.error("Failed to initialize Binance client. Check API keys.")
    sys.exit(1)

# --- Pydantic Models for Request Validation ---
class TradeRequestBase(BaseModel):
    strategy: str
    side: str
    symbol: str
    amount: float

class ManualTradeRequest(TradeRequestBase):
    price: float = None
    time_in_force: str = Field("GTC", alias="time-in-force")

class TwapTradeRequest(TradeRequestBase):
    duration: int
    interval: int

class OcoTradeRequest(TradeRequestBase):
    tp: float
    sl: float

class GridTradeRequest(TradeRequestBase):
    side: str = Field("BUY") # Default for grid strategy
    lower_bound: float
    upper_bound: float
    num_levels: int

class StopLimitTradeRequest(BaseModel):
    strategy: str
    side: str
    symbol: str
    amount: float
    stop_price: float
    limit_price: float

# --- API Endpoints ---
@app.get("/health")
def health_check():
    """
    A simple health check endpoint to confirm the server is running.
    """
    return {"status": "ok"}

@app.get("/assets")
def get_assets():
    """
    Fetches the list of all available trading symbols from the Binance Testnet.
    """
    try:
        exchange_info = binance_client.get_client().futures_exchange_info()
        symbols = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']
        return {"symbols": symbols}
    except Exception as e:
        logger.error(f"Error fetching assets from Binance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch trading assets.")

@app.get("/price/{symbol}")
def get_live_price(symbol: str):
    """
    Fetches the live market price for a given symbol.
    """
    try:
        ticker = binance_client.get_client().futures_symbol_ticker(symbol=symbol)
        return {"symbol": ticker['symbol'], "price": float(ticker['price'])}
    except Exception as e:
        logger.error(f"Error fetching live price for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch live price.")


@app.post("/trade")
def place_trade(request: dict):
    """
    Unified endpoint to handle all trading strategies.
    The function will dynamically validate and route the request
    to the correct trading function.
    """
    strategy = request.get("strategy")
    if not strategy:
        raise HTTPException(status_code=400, detail="Strategy not specified.")

    try:
        # Pydantic models automatically validate the input data
        if strategy == "manual":
            if "price" not in request or not request["price"]:
                validated_request = ManualTradeRequest(**{**request, "price": None})
                result = place_market_order(binance_client, validated_request.symbol, validated_request.side, validated_request.amount)
            else:
                validated_request = ManualTradeRequest(**request)
                result = place_limit_order(binance_client, validated_request.symbol, validated_request.side, validated_request.amount, validated_request.price, validated_request.time_in_force)
        elif strategy == "twap":
            validated_request = TwapTradeRequest(**request)
            result = place_twap_order(binance_client, validated_request.symbol, validated_request.side, validated_request.amount, validated_request.duration, validated_request.interval)
        elif strategy == "oco":
            validated_request = OcoTradeRequest(**request)
            result = place_oco_order(binance_client, validated_request.symbol, validated_request.side, validated_request.amount, validated_request.tp, validated_request.sl)
        elif strategy == "grid":
            validated_request = GridTradeRequest(**request)
            result = place_grid_orders(binance_client, validated_request.symbol, validated_request.lower_bound, validated_request.upper_bound, validated_request.num_levels, validated_request.amount)
        elif strategy == "stop-limit":
            validated_request = StopLimitTradeRequest(**request)
            result = place_stop_limit_order(binance_client, validated_request.symbol, validated_request.side, validated_request.amount, validated_request.stop_price, validated_request.limit_price)
        else:
            raise HTTPException(status_code=400, detail="Invalid strategy.")

        if result:
            return {"status": "success", "message": f"Order for '{validated_request.symbol}' placed successfully.", "details": result}
        else:
            return {"status": "error", "message": "Failed to place order. See logs for details."}
    except Exception as e:
        logger.error(f"Error processing trade request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/generate_rationale")
async def generate_rationale(request: dict):
    """
    Generates a trade rationale using the OpenAI API based on trade parameters.
    """
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured.")

    try:
        # Construct the prompt for the LLM
        prompt_message = (
            f"Generate a short, concise, and professional-sounding rationale for a trading order "
            f"with the following parameters: Symbol: {request.get('symbol')}, "
            f"Side: {request.get('side')}, Amount: {request.get('amount')}. "
            f"The rationale should be suitable for a log entry."
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial assistant."},
                {"role": "user", "content": prompt_message}
            ]
        )

        # Extract the generated text from the response
        rationale_text = response.choices[0].message.content
        return {"status": "success", "rationale": rationale_text}
            
    except Exception as e:
        logger.error(f"Error generating rationale: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate rationale: {e}")

# If you want to run this file directly with `python app.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
