import pandas as pd
import feedparser
import streamlit as st
import yfinance as yf
import base64
# Add here 👇
@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="1y")

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64("background.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: rgba(0,0,0,0.4);
    }}
    </style>
    """,
    unsafe_allow_html=True
)
import plotly.express as px
import plotly.graph_objects as go



# Page Config
st.set_page_config(
    page_title="StockVision",
    page_icon="📈",
    layout="wide"
)

# Title
st.markdown("""
            <style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}

header {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
<div style="text-align:center;">

<h1 style="font-size:60px; color:white;">
📈 StockVision
</h1>

<h3 style="color:#FFD6A5;">
Real-Time Stock Analysis Dashboard
</h3>
            
<span style="color:#FFD54F;">📊 Track</span>
<span style="color:#FFD54F;">🔍 Analyze</span>
<span style="color:#FFD54F;">📈 Compare Stocks</span>

</div>
""", unsafe_allow_html=True)

# Stock List
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "WIPRO.NS",
    "LT.NS",
    "TATAMOTORS.NS",
    "ADANIENT.NS"
]

# Main Stock Selection
ticker = st.selectbox(
    "Select Stock",
    stocks
)

# Time Period
period_options = {
    "Today": "1d",
    "Last 5 Days": "5d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "3 Years": "3y",
    "5 Years": "5y",
    "All Time": "max"
}

selected_period = st.selectbox(
    "Select Time Period",
    list(period_options.keys())
)

period = period_options[selected_period]
# Fetch Data
stock = yf.Ticker(ticker)
change_percent = 0
current_price = 0

try:
    data = stock.history(period=period)

    if data.empty:
        st.warning("Stock data temporarily unavailable.")
        st.stop()

except Exception:
    st.warning(
        "Yahoo Finance rate limit reached. Please try again in a few minutes."
    )
    st.stop()

if not data.empty:

    current_price = data["Close"].iloc[-1]

    if len(data) > 1:
        previous_price = data["Close"].iloc[-2]

        change_percent = (
            (current_price - previous_price)
            / previous_price
        ) * 100

    # Live Price
    st.metric(
        "💰 Live Stock Price",
        f"₹{current_price:.2f}",
        f"{change_percent:.2f}%"
    )

    # Company Information
    try:
        info = stock.fast_info
    except:
         info = {}    

    st.markdown("---")
    st.header("🏢 Company Information")
    st.write("**Current Price:**", f"₹{current_price:.2f}")  
    # Statistics
    st.markdown("---")
    st.header("📊 Key Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "High",
        f"₹{data['High'].max():.2f}"
    )

    col2.metric(
        "Low",
        f"₹{data['Low'].min():.2f}"
    )

    col3.metric(
        "Volume",
        f"{data['Volume'].iloc[-1]:,.0f}"
    )

    # Stock Trend Chart
    st.markdown("---")
    st.header("📈 Stock Price Trend")

    fig = px.line(
        data,
        x=data.index,
        y="Close",
        title=f"{ticker} Closing Price",
        markers=True
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
    # Compare Stocks
    st.markdown("---")
    st.header("📊 Compare Two Stocks")

    col1, col2 = st.columns(2)

    stock1 = col1.selectbox(
        "Select First Stock",
        stocks,
        key="stock1"
    )

    stock2 = col2.selectbox(
        "Select Second Stock",
        stocks,
        index=1,
        key="stock2"
    )

    data1 = yf.Ticker(stock1).history(period=period)
    data2 = yf.Ticker(stock2).history(period=period)

    compare_fig = go.Figure()

    compare_fig.add_trace(
        go.Scatter(
            x=data1.index,
            y=data1["Close"],
            mode="lines",
            name=stock1
        )
    )

    compare_fig.add_trace(
        go.Scatter(
            x=data2.index,
            y=data2["Close"],
            mode="lines",
            name=stock2
        )
    )

    compare_fig.update_layout(
        title=f"{stock1} vs {stock2}",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        height=500
    )

    st.plotly_chart(
        compare_fig,
        use_container_width=True
    )
    # Comparison Metrics
    p1 = data1["Close"].iloc[-1]
    p2 = data2["Close"].iloc[-1]

    c1, c2 = st.columns(2)

    c1.metric(
        stock1,
        f"₹{p1:.2f}"
    )

    c2.metric(
        stock2,
        f"₹{p2:.2f}"
    )
else:
    st.error("No data found.")
    # ==========================================
# Portfolio Tracker
# ==========================================

st.markdown("---")
st.header("📊 Portfolio Overview")

portfolio_stock = st.selectbox(
    "Select Stock for Portfolio",
    stocks,
    key="portfolio_stock"
)

quantity = st.number_input(
    "Quantity",
    min_value=1,
    value=1
)

buy_price = st.number_input(
    "Buy Price (₹)",
    min_value=0.0,
    value=100.0
)

if st.button("Add to Portfolio"):

    current_stock = yf.Ticker(portfolio_stock)
    current_data = current_stock.history(period="1d")

    if not current_data.empty:

        current_price = current_data["Close"].iloc[-1]

        invested = quantity * buy_price
        current_value = quantity * current_price
        profit_loss = current_value - invested

        portfolio_df = pd.DataFrame({
            "Stock": [portfolio_stock],
            "Quantity": [quantity],
            "Buy Price": [round(buy_price,2)],
            "Current Price": [round(current_price,2)],
            "Invested Amount": [round(invested,2)],
            "Current Value": [round(current_value,2)],
            "Profit/Loss": [round(profit_loss,2)]
        })

        st.success("Stock Added Successfully!")

        st.dataframe(portfolio_df, use_container_width=True)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Invested",
            f"₹{invested:,.2f}"
        )

        col2.metric(
            "Current Value",
            f"₹{current_value:,.2f}"
        )

        col3.metric(
            "Profit / Loss",
            f"₹{profit_loss:,.2f}"
        )
# ==========================================
# BUY / SELL SIMULATOR
# ==========================================

st.markdown("---")
st.header("📈 Buy / Sell Simulator")

if "cash" not in st.session_state:
    st.session_state.cash = 100000

if "holdings" not in st.session_state:
    st.session_state.holdings = {}

trade_stock = st.selectbox(
    "Choose Stock",
    stocks,
    key="trade_stock"
)

trade_qty = st.number_input(
    "Quantity",
    min_value=1,
    value=1,
    key="trade_qty"
)

trade_price = yf.Ticker(
    trade_stock
).history(period="1d")["Close"].iloc[-1]

st.metric(
    "Current Price",
    f"₹{trade_price:.2f}"
)

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 Buy"):

        cost = trade_qty * trade_price

        if cost <= st.session_state.cash:

            st.session_state.cash -= cost

            st.session_state.holdings[trade_stock] = (
                st.session_state.holdings.get(
                    trade_stock, 0
                ) + trade_qty
            )

            st.success("Stock Purchased!")

            st.write(
                "After Buy:",
                st.session_state.holdings
            )
with col2:
    if st.button("🔴 Sell"):

        owned = st.session_state.holdings.get(
            trade_stock, 0
        )

        if owned >= trade_qty:

            st.session_state.cash += (
                trade_qty * trade_price
            )

            st.session_state.holdings[
                trade_stock
            ] -= trade_qty

            st.success("Stock Sold!")

        else:
            st.error(
                f"You only own {owned} shares."
            )
            st.write("DEBUG Holdings:", st.session_state.holdings)
# ==========================================
# TRADING ACCOUNT SUMMARY
# ==========================================

st.markdown("---")
st.subheader("💰 Trading Account")

st.metric(
    "Available Cash",
    f"₹{st.session_state.cash:,.2f}"
)

st.write("### Holdings")

portfolio_data = []

for stock, qty in st.session_state.holdings.items():

    if qty > 0:
        portfolio_data.append([stock, qty])

if portfolio_data:

    holdings_df = pd.DataFrame(
        portfolio_data,
        columns=["Stock", "Quantity"]
    )

    st.dataframe(
        holdings_df,
        use_container_width=True
    )

else:
    st.info("No holdings yet.")  
    # ==========================================
# LATEST STOCK NEWS
# ==========================================

st.markdown("---")
st.subheader("📰 Latest Stock News")

try:
    rss_url = (
        f"https://news.google.com/rss/search?q=RELIANCE"
    )

    feed = feedparser.parse(rss_url)

    if feed.entries:

        for article in feed.entries[:5]:

            st.markdown(
                f"### [{article.title}]({article.link})"
            )

            st.caption(
                article.published
                if hasattr(article, "published")
                else ""
            )

            st.write("---")

    else:
        st.info("No news found.")

except Exception as e:
    st.error(f"News unavailable: {e}")   
    
