🔗 THNDR INTEGRATION PARAMETERS
================================

CURRENT STATE (Using yfinance for backtesting):
- Data source: Yahoo Finance API
- Broker costs: Simulated (0.05% spread, 0.1% slippage, 0.1% commission)
- Order execution: Not live (backtest only)
- Authentication: None

REQUIRED CHANGES FOR THNDR:
================================

1️⃣ API AUTHENTICATION
──────────────────────

Replace:
  None (currently using yfinance)

With:
  THNDR_API_KEY = "your_api_key"
  THNDR_API_SECRET = "your_api_secret"
  THNDR_ACCOUNT_ID = "your_account_id"

Location:
  Create: .env file
  Use credentials via python-dotenv

Example (.env file):
```
THNDR_API_KEY=your_key_here
THNDR_API_SECRET=your_secret_here
THNDR_ACCOUNT_ID=your_account_id
THNDR_BASE_URL=https://api.thndr.com/v1
```


2️⃣ REAL BROKER COSTS
──────────────────────

Current (Simulated):
  commission_pct = 0.1%
  bid_ask_spread = 0.05%
  slippage_pct = 0.1%

Need to Update To (Thndr rates):
  # Get from Thndr dashboard or API
  commission_pct = 0.1%  ← Verify exact rate
  bid_ask_spread = 0.05% ← Check for CIB/HRHO/ORAS
  slippage_pct = 0.1%    ← Test with real orders

Location:
  cib_arbitrage_test.py, run_arbitrage.py (backtest_arbitrage method)


3️⃣ DATA SOURCE
───────────────

Current:
  import yfinance as yf
  self.cairo_data = yf.download(ticker, start, end)
  self.london_data = yf.download(ticker, start, end)

Need to Replace With:
  # Option A: Use Thndr API for real data
  def fetch_data_from_thndr(self, ticker):
      response = requests.get(
          f"{THNDR_BASE_URL}/prices/{ticker}",
          headers={"Authorization": f"Bearer {THNDR_API_KEY}"},
          params={"period": "1d", "limit": 365}
      )
      return pd.DataFrame(response.json())
  
  # Option B: Keep yfinance for backtesting, use Thndr for live
  # Can run backtest with yfinance, then execute trades via Thndr

Recommended:
  ✓ Backtest: Keep yfinance (easier, reliable historical data)
  ✓ Live trading: Switch to Thndr API for real-time data & execution


4️⃣ ORDER EXECUTION
────────────────────

Current:
  N/A (backtest only - no actual orders)

Need to Add:
  def place_buy_order_thndr(self, ticker, quantity, price):
      response = requests.post(
          f"{THNDR_BASE_URL}/orders/buy",
          headers={"Authorization": f"Bearer {THNDR_API_KEY}"},
          json={
              "ticker": ticker,
              "quantity": quantity,
              "type": "market",  # or "limit"
              "price": price     # for limit orders
          }
      )
      return response.json()
  
  def place_sell_order_thndr(self, ticker, quantity, price):
      response = requests.post(
          f"{THNDR_BASE_URL}/orders/sell",
          headers={"Authorization": f"Bearer {THNDR_API_KEY}"},
          json={
              "ticker": ticker,
              "quantity": quantity,
              "type": "market",
              "price": price
          }
      )
      return response.json()


5️⃣ CURRENCY & ACCOUNT
───────────────────────

Current:
  Hardcoded for Egyptian market (EGP)
  No account considerations

Need to Update:
  # Account currency
  ACCOUNT_CURRENCY = "EGP"  # Thndr default
  
  # Or if multi-currency:
  CAIRO_CURRENCY = "EGP"
  LONDON_CURRENCY = "GBP"
  EXCHANGE_RATE = 1 EGP → ? GBP
  
  # Account size
  ACCOUNT_BALANCE = 50000  # In EGP
  
  # Position sizing
  MAX_POSITION_SIZE = 0.1  # 10% of account per trade
  MAX_LEVERAGE = 1.0       # No leverage


6️⃣ RATE LIMITING & DELAYS
──────────────────────────

Current:
  None required (backtesting is instant)

With Thndr API:
  Add rate limiting:
    from time import sleep
    API_CALL_DELAY = 0.5  # seconds between calls
    API_RATE_LIMIT = 100  # calls per minute
  
  Handle latency:
    execution_delay_pct = 0.05%  # Update based on actual test


7️⃣ ERROR HANDLING
──────────────────

Add These:
  - Connection errors (internet down)
  - Authentication failures (expired token)
  - Order rejection (insufficient funds)
  - API timeouts (Thndr servers down)
  - Insufficient liquidity
  - Partial fills


8️⃣ CONFIGURATION FILE
──────────────────────

Current:
  Hardcoded in Python files

Better Approach:
  Create: config.toml or config.json
  
  Example config.toml:
  ```
  [broker]
  name = "thndr"
  api_key = "${THNDR_API_KEY}"
  api_secret = "${THNDR_API_SECRET}"
  account_id = "${THNDR_ACCOUNT_ID}"
  
  [costs]
  commission = 0.1
  bid_ask_spread = 0.05
  slippage = 0.1
  
  [trading]
  signal_threshold = 1.0
  max_position_size = 0.1
  max_leverage = 1.0
  
  [markets]
  cairo_ticker = "COMI"
  london_ticker = "CBKD"
  start_date = "2025-04-14"
  end_date = "2026-04-14"
  ```


📋 PARAMETER CHECKLIST FOR THNDR
─────────────────────────────────

□ Get Thndr API credentials (key, secret, account ID)
□ Create .env file with credentials
□ Install required libraries: requests, python-dotenv
□ Test Thndr API connection
□ Get exact commission rate from Thndr
□ Get actual bid-ask spreads for CIB/HRHO
□ Test order placement (paper trading first)
□ Verify execution timing/slippage
□ Set up error handling
□ Create config file
□ Test full workflow:
   ✓ Signal generation
   ✓ Order placement
   ✓ Order confirmation
   ✓ Order closure
   ✓ P&L calculation


🔄 IMPLEMENTATION APPROACH
──────────────────────────

Phase 1: Data Integration
  └─ Replace fetch_data() to use Thndr API
  └─ Backtest with Thndr historical data
  └─ Verify same results as yfinance

Phase 2: Live Signal Generation
  └─ Start monitoring London prices via Thndr
  └─ Generate signals in real-time
  └─ Log signals (don't execute yet)

Phase 3: Paper Trading (Risk-Free)
  └─ Place orders on paper trading account
  └─ Verify execution
  └─ Track "virtual" P&L
  └─ Monitor for 2+ weeks

Phase 4: Live Trading (Small)
  └─ Start with $100-500 per trade
  └─ Monitor closely
  └─ Scale up gradually

Phase 5: Production
  └─ Scale to target capital
  └─ Full monitoring & alerts
  └─ Daily reporting


📝 QUICK START: WHICH TO CHANGE FIRST?
────────────────────────────────────────

Minimum to get started:
1. API authentication (.env file)
2. Commission/spread rates (update backtest_arbitrage params)
3. Data source (if using Thndr for testing)

Optional but recommended:
4. Order placement functions
5. Error handling
6. Configuration file
7. Real-time monitoring


🎯 DO YOU WANT ME TO:
──────────────────────

A) Create Thndr integration module with all these methods?
B) Update parameters for Thndr (need your exact commission rates)?
C) Add .env file support and environment variable loading?
D) All of the above?

Please provide:
• Thndr account/API details (can keep secret, just confirm you have them)
• Commission rates for Egyptian markets
• How many of the 8 phases to implement?
