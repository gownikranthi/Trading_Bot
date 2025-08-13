# Binance USDT-M Futures Order Bot

This is a full-stack trading application with a Python backend and an HTML/JavaScript frontend. It allows you to place various orders on the Binance USDT-M Futures Testnet and even generates a trade rationale using the OpenAI API.

**WARNING: This project is designed for the Binance Futures Testnet for educational and development purposes. It should NOT be used on the Binance Mainnet without extensive testing and understanding of the code. Trading financial assets carries significant risk.**

## Features

-   **Frontend UI:** A clean, single-page web interface to interact with the bot.
-   **Backend API:** A FastAPI server that connects the UI to your trading logic.
-   **Core Orders:** Place market and limit orders.
-   **Advanced Strategies:** Implement and execute Stop-Limit, OCO, TWAP, and Grid trading.
-   **Live Data:** Fetches real-time asset prices and available symbols from the Binance Testnet.
-   **AI Integration:** Generates a professional rationale for your trades using the OpenAI API.
-   **Input Validation:** Ensures all orders adhere to Binance's trading rules (e.g., tick size, minimum quantity).
-   **Secure Configuration:** Manages API keys via a `.env` file.
-   **Structured Logging:** Logs all activity and errors to a `bot.log` file.
-   **Unit Tests:** Verifies the functionality of core modules.

## Prerequisites

-   Python 3.10+
-   A Binance Futures Testnet account and API keys.
-   An OpenAI API key for the rationale generator.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone ([https://github.com/gownikranthi/Binance_Trading_bot.git])
    cd trading-bot
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Python Dependencies:**
    This project has dependencies for both the trading logic and the web server.
    ```bash
    pip install -r requirements.txt
    pip install "fastapi[all]" uvicorn openai
    ```

4.  **Configure API Keys:**
    -   Copy the `.env.example` file to a new file named `.env`.
    -   Edit the `.env` file and add your Binance Testnet API key, secret, and your OpenAI API key.
    
    ```
    BINANCE_API_KEY=your_binance_api_key_here
    BINANCE_API_SECRET=your_binance_api_secret_here
    OPENAI_API_KEY=your_openai_api_key_here
    ```

## Usage

### 1. Start the Backend Server

Open your terminal in the project's root directory and run the following command. The server will run on `http://127.0.0.1:8000`. Keep this terminal window open.

```bash
uvicorn app:app --reload
```

### 2. Open the Frontend UI

With the server running, simply open the `index.html` file in your web browser. The UI will automatically connect to the backend, and you can begin interacting with the bot.

### 3. Placing Orders

Use the control panel in the UI to select a strategy and set your trade parameters.

-   **Buy/Sell:** Place orders directly on the Binance Testnet. The outcome will be logged in the "Status & Notifications" area.
-   **Generate Rationale ✨:** Use the OpenAI API to get a professional explanation for your trade parameters.

### 4. Running Unit Tests

To verify that the core trading logic is working correctly, run the unit tests.

```bash
python -m unittest tests/
```

This will run all the test files in the `tests/` directory.
