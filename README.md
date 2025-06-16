# Stock Market Data Fetcher

This Python project fetches stock market data using the Alpha Vantage API.

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Get your free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

3. Create a `.env` file:
   - Copy `.env.example` to `.env`
   - Replace `your_api_key_here` with your actual Alpha Vantage API key
   ```bash
   cp .env.example .env
   # Then edit .env with your API key
   ```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python stock_data.py
```

The script will fetch the latest stock data for AAPL (Apple Inc.) by default. You can modify the symbol in the script to fetch data for other stocks.

## Security Note

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore` to prevent accidental commits
- Keep your API key secure and don't share it publicly

## Features

- Fetches real-time stock data
- Displays current price and daily change
- Shows trading volume
- Includes error handling for API limits and invalid symbols 