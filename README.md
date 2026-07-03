# 2-
2%
# 📈 DayTrade Pro - Mobile Trading Assistant

## ⚠️ CRITICAL LEGAL DISCLAIMER

**THIS IS NOT FINANCIAL ADVICE.** Trading stocks and options carries substantial risk of loss, including 100% loss of capital. This tool is for educational purposes only. You are solely responsible for all trading decisions. Consult a licensed financial advisor before trading.

---

## 🚀 Quick Start

### Installation

1. **Clone or download the script:**
   ```bash
   # Save the trading_assistant.py file to your computer
   ```

2. **Install Python 3.10+ if not already installed:**
   - Download from [python.org](https://www.python.org/downloads/)

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install streamlit yfinance pandas numpy pytz requests
   ```

4. **Run the app:**
   ```bash
   streamlit run trading_assistant.py
   ```

5. **Open in browser:**
   - Streamlit will open automatically at `http://localhost:8501`
   - For mobile: Open on your phone's browser and navigate to your computer's IP address (shown in terminal) + port 8501

---

## 📱 Mobile Access

### On Same Wi-Fi Network:
1. Find your computer's local IP:
   - **Windows:** `ipconfig` in command prompt (look for IPv4 Address like 192.168.x.x)
   - **Mac/Linux:** `ifconfig` in terminal

2. On your phone, go to: `http://YOUR_IP:8501`

### Remote Access:
- Use Streamlit Cloud or ngrok for remote access (advanced)

---

## 🎯 How It Works

### **TIME-BASED STRATEGY SELECTION**

#### 1️⃣ **BEFORE 8 AM CST - Intraday Recommendation**
- Runs at market open
- Scans for high-momentum stocks with:
  - **Volume Shock:** 150%+ of 10-day average (indicates breakout)
  - **RSI 45-65:** Not overbought/oversold, room to run
  - **Volatility:** True Range confirms price movement potential
- **Goal:** Buy at open, sell for +$1 profit during the day
- **Risk:** -$0.50 max loss (2:1 RRR)

#### 2️⃣ **11 AM CST - END-OF-DAY SWING**
- For end-of-day swing trades
- Buy at market close or last hour
- Hold overnight, sell next morning at opening gap
- **Goal:** Capture overnight momentum or gap-up reversal

#### 3️⃣ **SAME-DAY OPTIONS**
- 0 DTE (zero days to expiration) options
- Buy call if RSI < 45 (oversold reversal expected)
- Buy put if RSI > 65 (overbought pullback expected)
- Sell same day for quick profit
- **⚠️ EXTREME RISK:** Can lose 100% of premium paid

#### 4️⃣ **FRIDAY WEEKLY OPTIONS**
- Only available on Fridays
- Buy near-ATM calls/puts
- Hold through weekend (MASSIVE gap risk)
- Sell Monday morning at open
- **Expected return:** $0.50-$3.00 profit or 50-150%
- **⚠️ EXTREME RISK:** Weekend gaps can wipe out position

---

## 💰 Position Sizing

All calculations respect **$35 max capital**:

```
Risk per trade = $0.50 (ensures 2:1 RRR with $1 profit target)
Shares = (35 × 0.95) / Entry Price
Stop Loss = Entry - (True Range × 1.5)
Take Profit = Entry + (True Range × 3)
```

**Example:**
- Stock: AAPL at $25.00
- Shares: 1 share (uses ~$25 capital)
- Stop Loss: $24.50
- Take Profit: $26.50
- Profit: +$1.50 (meets $1 minimum)
- Risk: -$0.50 (2:1 ratio)

---

## 📊 Trading Log

All recommendations are automatically saved to `trades_history.json` in the same folder:

- **Entry price**
- **Stop loss & take profit**
- **Shares and capital used**
- **Timestamp and strategy type**
- **Performance metrics**

View in the **History tab** to track:
- Win rate
- Total trades
- Net P&L
- Strategy effectiveness

---

## ⚙️ Technical Indicators

### **RSI (Relative Strength Index, 14-period)**
- **0-30:** Oversold (potential reversal buy)
- **30-70:** Neutral (no extreme condition)
- **70-100:** Overbought (potential reversal sell)
- **Strategy uses:** 45-65 (active momentum, not exhausted)

### **Volume Shock**
- **Current volume / 10-day average**
- **Threshold:** > 1.5x (150%)
- **Meaning:** Unusual activity = volatility/breakout likely

### **True Range (ATR component)**
- **Measures volatility:** High TR = big price swings
- **Used for:** Position sizing and profit target calculation
- **Benefit:** Ensures $1 profit is achievable in current conditions

---

## 🛠️ Customization

### **Change Starting Capital:**
Edit line in code:
```python
# Change from $35 to your amount
position_size = risk_amount / (true_range / current_price)
```

### **Change Profit Target:**
Edit to any amount (currently $1.00):
```python
risk_amount = 0.50  # Adjust based on new profit target
```

### **Add More Stocks:**
Edit the watchlist (currently top 30 most liquid):
```python
tickers = ['AAPL', 'MSFT', 'GOOGL', ...] # Add/remove tickers
```

### **Change Time Thresholds:**
```python
if hour < 8:  # Change 8 to 7 or 9 as desired
if hour >= 11:  # Change 11 to 12 or 10 as desired
```

---

## 📈 Real-World Workflow

### **Monday - Friday Before Market Open:**
1. Open app
2. Current time shows "Pre-market (before 8 AM CST)"
3. Click "🌅 Get Intraday Recommendation"
4. App scans 30 stocks, returns best setup
5. Review entry, stop loss, profit target
6. Click "✅ Confirm Trade Placed"
7. App logs trade with timestamp
8. Execute in your broker (TD Ameritrade, Robinhood, etc.)
9. Monitor through the day
10. At profit target or stop loss, close position
11. Manually update trade history with exit price (optional)

### **Monday - Friday at 11 AM CST:**
1. Open app
2. Current time shows "End-of-day (11 AM CST onwards)"
3. Click "🌙 Get Swing Trade Recommendation"
4. App suggests stock to buy before close
5. Execute before 3:55 PM market close
6. Next morning after open, check if profit target/stop hit
7. Close position

### **For Options (Any Time):**
1. Go to "💎 Options" tab
2. Click either "⚡ Same-Day Options" or "📅 Friday Weeklies"
3. App recommends CALL or PUT to buy
4. Buy the contract (specify strike in your broker)
5. Set profit target and stop loss mentally
6. Sell when target hit or stop triggered
7. Log trade in app

---

## ⚠️ Risk Management Rules

**Always follow these:**

1. **Position Size:** Never exceed $35 total capital per trade
2. **Stop Loss:** Place hard stop at recommended price (no exceptions)
3. **Take Profit:** Close at target, don't hold for more (greed kills accounts)
4. **Risk Per Trade:** Max -$0.50 per trade (or adjust if you change capital)
5. **Options:** Assume 100% loss when buying premium
6. **Friday Weeklies:** Only trade if you can afford to lose the entire premium
7. **No Averaging Down:** One entry, one exit per recommendation

---

## 🐛 Troubleshooting

### **"No stocks met criteria"**
- Market may be in consolidation (no clear setups)
- Scan again in 15 minutes
- Adjust RSI range from 45-65 to 40-70 (if you want to be less strict)

### **"yfinance error"**
- Yahoo Finance may be temporarily down
- Try again in 5 minutes
- Check internet connection

### **Mobile app looks zoomed in/small**
- Mobile CSS is built-in, but some browsers may override
- Try: Settings → Zoom → Reset to default
- Or rotate to landscape mode

### **Trades not saving**
- Ensure app folder has write permissions
- Check `trades_history.json` exists in same folder as script
- Restart app if corrupted

---

## 📚 Understanding the Recommendations

### **Why These Filters?**

**Volume Shock (150%+):**
- High volume = institutional/retail interest
- Confirms volatility is real, not noise
- Increases probability of breakout

**RSI 45-65:**
- Avoids oversold (risky reversal trade)
- Avoids overbought (avoid late entries)
- Sweet spot: momentum but not exhausted

**True Range Volatility:**
- Ensures target profit is achievable
- Scales position size to market conditions
- Tight range = smaller positions, wide range = larger positions

**2:1 Risk-to-Reward:**
- You only need 33% win rate to break even
- Built-in margin of safety
- Professional standard

---

## 💡 Pro Tips

1. **Pre-market prep:** Run app 30 mins before market open
2. **Take profits early:** If you hit 50% of target mid-day, take it
3. **Options IV Crush:** Implied volatility drops after earnings (avoid)
4. **Friday Risk:** Weekend gaps are brutal on Friday options
5. **Track in spreadsheet:** Also log actual entry/exit prices for analysis
6. **Market conditions:** Avoid trading during macro news (Fed, jobs report, earnings)
7. **Monthly review:** Check win rate and adjust filters if needed

---

## 📞 Support

If app crashes:
1. Close and reopen
2. Check Python version: `python --version` (need 3.10+)
3. Reinstall dependencies: `pip install --upgrade -r requirements.txt`
4. Check internet connection

---

## 🎓 Educational Resources

- **RSI:** Investopedia - Relative Strength Index
- **Volume Analysis:** Investopedia - Volume Weighted Average Price
- **Options Greeks:** TheOptionsGuide.com
- **2:1 RRR:** Profitable Trading blog

---

**Good luck, and trade responsibly!** 📈🚀
