import streamlit as st
from datetime import datetime
import pytz
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="DayTrade Pro", page_icon="📈", layout="centered")

st.markdown("""
<style>
    h1, h2 { text-align: center; }
    .metric { background: #f0f2f6; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #1f77b4; }
    .success { border-left-color: #2ecc71; }
    .danger { border-left-color: #e74c3c; }
    .stButton > button { width: 100%; padding: 12px; font-weight: bold; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 DayTrade Pro")
now = datetime.now(pytz.timezone('US/Central'))
st.markdown(f"<div style='text-align:center'>🕐 {now.strftime('%I:%M %p %Z')} | 📅 {now.strftime('%a, %b %d, %Y')}</div>", unsafe_allow_html=True)

with st.expander("⚠️ DISCLAIMER - READ FIRST"):
    st.error("""**NOT FINANCIAL ADVICE.** These are heuristic screens based on delayed data (15-20 min).
    No scanner can guarantee profit. Options (especially 0DTE) can lose 100% instantly.
    You are solely responsible for all trades. Consult a licensed advisor.""")

st.divider()

# ============================================================================
# SESSION STATE (results persist between reruns)
# ============================================================================

for key in ['res_overnight', 'res_intraday', 'res_opt_any', 'res_opt_0dte']:
    if key not in st.session_state:
        st.session_state[key] = None

# ============================================================================
# 💰 BUDGET SELECTOR ($1 - $1000)
# ============================================================================

BUDGET = st.slider("💰 Trading Budget ($)", min_value=1, max_value=1000, value=35, step=1,
                   help="Scanners will only pick stocks/options you can afford with this amount")

PROFIT_PCT = 2.0  # target profit as % of budget
PROFIT_TARGET = round(BUDGET * PROFIT_PCT / 100, 2)

st.caption(f"Budget: **${BUDGET}** | Profit target: **+${PROFIT_TARGET}** ({PROFIT_PCT:.0f}% of budget)")

# Clear stale results if budget changed since last scan
if st.session_state.get('last_budget') != BUDGET:
    for key in ['res_overnight', 'res_intraday', 'res_opt_any', 'res_opt_0dte']:
        st.session_state[key] = None
    st.session_state['last_budget'] = BUDGET

st.divider()

WATCHLIST = ['SOFI', 'PLTR', 'F', 'NIO', 'RIVN', 'LCID', 'AAL', 'CCL', 'NCLH',
             'PLUG', 'RIOT', 'MARA', 'HOOD', 'SNAP', 'PFE', 'T', 'VZ', 'INTC',
             'BAC', 'GRAB', 'CHPT', 'OPEN', 'DKNG', 'UPST', 'AFRM']

# Higher-priced liquid stocks added when budget allows
WATCHLIST_LARGE = ['AAPL', 'AMD', 'GOOGL', 'AMZN', 'MSFT', 'NVDA', 'TSLA', 'META',
                   'NFLX', 'COIN', 'MSTR', 'SMCI', 'CRM', 'DIS', 'BA', 'SPY', 'QQQ']

if BUDGET >= 100:
    WATCHLIST = WATCHLIST + WATCHLIST_LARGE

OPTIONS_UNDERLYINGS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMD', 'F', 'SOFI', 'PLTR']


def load_yf():
    try:
        import yfinance as yf
        import pandas as pd
        return yf, pd
    except Exception:
        return None, None


def rsi(series, period=14):
    try:
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        val = 100 - (100 / (1 + gain / loss))
        v = float(val.iloc[-1])
        return None if v != v else v
    except Exception:
        return None


def fetch_hist(yf, ticker, period='30d', interval='1d'):
    try:
        h = yf.Ticker(ticker).history(period=period, interval=interval)
        return h if h is not None and len(h) >= 10 else None
    except Exception:
        return None


def scan_overnight(yf, pd, progress):
    results = []
    for i, t in enumerate(WATCHLIST):
        progress.progress((i + 1) / len(WATCHLIST))
        h = fetch_hist(yf, t)
        if h is None:
            continue
        price = float(h['Close'].iloc[-1])
        if price > BUDGET or price < 1:
            continue
        shares = int(BUDGET / price)
        if shares < 1:
            continue
        r = rsi(h['Close'])
        avg_vol = float(h['Volume'].iloc[-11:-1].mean())
        vol_ratio = float(h['Volume'].iloc[-1]) / avg_vol if avg_vol > 0 else 0
        try:
            gaps = (h['Open'].iloc[1:].values - h['Close'].iloc[:-1].values)
            avg_gap = float(pd.Series(gaps[-10:]).mean())
        except Exception:
            avg_gap = 0
        needed_move = PROFIT_TARGET / shares
        avg_range = float((h['High'] - h['Low']).tail(10).mean())
        if r is None or r < 45 or r > 68:
            continue
        if avg_range < needed_move:
            continue
        score = vol_ratio + (avg_gap / price * 100) + (r - 45) / 20
        results.append({
            'ticker': t, 'price': round(price, 2), 'shares': shares,
            'needed_move': round(needed_move, 3),
            'sell_target': round(price + needed_move, 2),
            'stop': round(price - needed_move / 2, 2),
            'rsi': round(r, 1), 'vol': round(vol_ratio, 2),
            'avg_range': round(avg_range, 2), 'score': score
        })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def scan_intraday(yf, pd, progress):
    results = []
    for i, t in enumerate(WATCHLIST):
        progress.progress((i + 1) / len(WATCHLIST))
        h = fetch_hist(yf, t, period='5d', interval='15m')
        d = fetch_hist(yf, t)
        if h is None or d is None:
            continue
        price = float(h['Close'].iloc[-1])
        if price > BUDGET or price < 1:
            continue
        shares = int(BUDGET / price)
        if shares < 1:
            continue
        needed_move = PROFIT_TARGET / shares
        recent = h['Close'].tail(5)
        mom = float(recent.iloc[-1] - recent.iloc[0])
        r = rsi(d['Close'])
        avg_range = float((d['High'] - d['Low']).tail(5).mean())
        remaining_range = avg_range - abs(float(d['High'].iloc[-1] - d['Low'].iloc[-1]))
        if r is None or r < 40 or r > 70:
            continue
        if avg_range < needed_move * 1.5:
            continue
        score = (mom / price * 100) + max(remaining_range, 0) / price * 50
        results.append({
            'ticker': t, 'price': round(price, 2), 'shares': shares,
            'sell_target': round(price + needed_move, 2),
            'stop': round(price - needed_move / 2, 2),
            'needed_move': round(needed_move, 3),
            'momentum': round(mom, 3), 'rsi': round(r, 1),
            'avg_range': round(avg_range, 2), 'score': score
        })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def scan_options(yf, pd, progress, same_day_expiry=False):
    plays = []
    today = datetime.now(pytz.timezone('US/Central')).date()
    for i, t in enumerate(OPTIONS_UNDERLYINGS):
        progress.progress((i + 1) / len(OPTIONS_UNDERLYINGS))
        try:
            tk = yf.Ticker(t)
            expiries = tk.options
            if not expiries:
                continue
            expiry = None
            for e in expiries:
                ed = datetime.strptime(e, '%Y-%m-%d').date()
                if same_day_expiry and ed == today:
                    expiry = e
                    break
                if not same_day_expiry and ed >= today:
                    expiry = e
                    break
            if expiry is None:
                continue
            hist = tk.history(period='15d')
            if hist is None or len(hist) < 10:
                continue
            spot = float(hist['Close'].iloc[-1])
            r = rsi(hist['Close'])
            if r is None:
                continue
            direction = 'CALL' if r <= 50 else 'PUT'
            chain = tk.option_chain(expiry)
            table = chain.calls if direction == 'CALL' else chain.puts
            aff = table[(table['lastPrice'] > 0.03) & (table['lastPrice'] <= BUDGET / 100)]
            aff = aff[aff['volume'].fillna(0) > 50]
            if len(aff) == 0:
                continue
            aff = aff.copy()
            aff['dist'] = (aff['strike'] - spot).abs()
            best = aff.sort_values('dist').iloc[0]
            cost = float(best['lastPrice']) * 100
            plays.append({
                'ticker': t, 'type': direction, 'strike': float(best['strike']),
                'premium': round(float(best['lastPrice']), 2),
                'cost': round(cost, 2), 'spot': round(spot, 2),
                'expiry': expiry, 'rsi': round(r, 1),
                'volume': int(best['volume']) if best['volume'] == best['volume'] else 0,
                'breakeven': round(float(best['strike']) + float(best['lastPrice']), 2) if direction == 'CALL'
                             else round(float(best['strike']) - float(best['lastPrice']), 2)
            })
        except Exception:
            continue
    plays.sort(key=lambda x: x['volume'], reverse=True)
    return plays


def show_stock_pick(best, hold_text):
    st.success(f"✅ **{best['ticker']}** — TOP PICK")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Buy At (approx)", f"${best['price']}")
        st.metric("Stop Loss", f"${best['stop']}")
    with c2:
        st.metric(f"Sell Target (+${PROFIT_TARGET})", f"${best['sell_target']}")
        st.metric("Shares", best['shares'])
    st.markdown(f"""
    <div class='metric success'>
    <strong>📊 Setup</strong><br>
    Capital: ${best['price'] * best['shares']:.2f} of ${BUDGET:.0f}<br>
    Move needed for +${PROFIT_TARGET} ({PROFIT_PCT:.0f}%): ${best['needed_move']}/share (avg daily range ${best['avg_range']})<br>
    RSI: {best['rsi']} | {hold_text}
    </div>
    """, unsafe_allow_html=True)


def show_runners(results, fmt):
    if len(results) > 1:
        st.caption("Runner-ups:")
        for r in results[1:4]:
            st.write(fmt(r))


def show_option_pick(p, sell_note):
    color = 'success' if p['type'] == 'CALL' else 'danger'
    st.success(f"✅ **{p['ticker']} {p['type']}** — Strike ${p['strike']} — Exp {p['expiry']}")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Contract Cost", f"${p['cost']}")
        st.metric("Premium", f"${p['premium']}")
    with c2:
        st.metric("Stock Price Now", f"${p['spot']}")
        st.metric("Breakeven", f"${p['breakeven']}")
    st.markdown(f"""
    <div class='metric {color}'>
    <strong>📊 Why this pick</strong><br>
    RSI {p['rsi']} → {'oversold lean, betting on bounce UP' if p['type']=='CALL' else 'overbought lean, betting on pullback DOWN'}<br>
    Contract volume today: {p['volume']}<br>
    {sell_note}
    </div>
    """, unsafe_allow_html=True)
    st.warning("🔴 Options can go to $0. Sell the moment you're happy with profit.")


def run_scan(scan_fn, *args, **kwargs):
    yf, pd = load_yf()
    if yf is None:
        st.error("Data library failed to load. Refresh and try again.")
        return None
    progress = st.progress(0)
    with st.spinner("Scanning live market data (20-60 sec)..."):
        results = scan_fn(yf, pd, progress, *args, **kwargs)
    progress.empty()
    return results if results else []


# ============================================================================
# UI — EACH SCANNER IN ITS OWN COLLAPSIBLE EXPANDER
# ============================================================================

tab1, tab2 = st.tabs(["📊 Stocks", "⚡ Options"])

with tab1:
    st.subheader(f"Stock Scanners (${BUDGET} budget)")

    with st.expander(f"1️⃣ 🌙 Overnight Swing — buy today, sell tomorrow (+${PROFIT_TARGET})", expanded=False):
        if st.button("🔍 SCAN NOW", key="b1"):
            st.session_state.res_overnight = run_scan(scan_overnight)
        res = st.session_state.res_overnight
        if res == []:
            st.warning("❌ No setups passed filters. Try closer to market close.")
        elif res:
            show_stock_pick(res[0], "Hold: overnight | Sell: tomorrow 9:30-10:30 AM ET")
            show_runners(res, lambda r: f"**{r['ticker']}** ${r['price']} → ${r['sell_target']} | RSI {r['rsi']} | Vol {r['vol']}x")

    with st.expander("2️⃣ ☀️ Same-Day Trade — buy now, sell before close", expanded=False):
        if st.button("🔍 SCAN NOW", key="b2"):
            st.session_state.res_intraday = run_scan(scan_intraday)
        res = st.session_state.res_intraday
        if res == []:
            st.warning("❌ No intraday setups right now. Best: 9:30 AM - 2 PM ET.")
        elif res:
            show_stock_pick(res[0], "Hold: hours | Sell: at target or before 3:55 PM ET")
            show_runners(res, lambda r: f"**{r['ticker']}** ${r['price']} → ${r['sell_target']} | momentum {r['momentum']:+.3f}")

with tab2:
    st.subheader(f"Options Scanners (contract ≤ ${BUDGET})")
    st.caption(f"${BUDGET} buys premium ≤ ${BUDGET/100:.2f}/share. Cheaper premiums = further out-of-the-money = higher risk of expiring worthless.")

    with st.expander("3️⃣ ⚡ Any-Day Option — buy & sell today", expanded=False):
        if st.button("🔍 SCAN NOW", key="b3"):
            st.session_state.res_opt_any = run_scan(scan_options, same_day_expiry=False)
        res = st.session_state.res_opt_any
        if res == []:
            st.warning(f"❌ No liquid contracts under ${BUDGET} found right now.")
        elif res:
            show_option_pick(res[0], "Plan: buy now, sell TODAY at any profit you like.")
            show_runners(res, lambda p: f"**{p['ticker']} {p['type']}** ${p['strike']} exp {p['expiry']} — ${p['cost']}, vol {p['volume']}")

    with st.expander("4️⃣ 📅 Friday 0DTE — expires today, sell when green", expanded=False):
        if st.button("🔍 SCAN NOW", key="b4"):
            if now.weekday() != 4:
                st.info(f"Today is {now.strftime('%A')} — SPY/QQQ have daily expiries, scanning anyway...")
            st.session_state.res_opt_0dte = run_scan(scan_options, same_day_expiry=True)
        res = st.session_state.res_opt_0dte
        if res == []:
            st.warning(f"❌ No same-day-expiry contracts under ${BUDGET} with liquidity.")
        elif res:
            show_option_pick(res[0], "Buy 9:30-10:00 AM ET, sell when YOU see profit. NEVER hold past 3 PM.")
            show_runners(res, lambda p: f"**{p['ticker']} {p['type']}** ${p['strike']} — ${p['cost']}, vol {p['volume']}")

st.divider()
st.markdown("""
<div style='font-size:12px;color:#999;text-align:center'>
⚠️ Heuristic screens, not profit guarantees. Data delayed 15-20 min. Options risk 100% loss. Trade responsibly. 📈
</div>
""", unsafe_allow_html=True)
