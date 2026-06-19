import feedparser
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(
    page_title="AI Stock Analytics Dashboard",
    page_icon="📈",
    layout="wide"
)

def calculate_rsi(data, period=14):
    delta = data.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

st.sidebar.title("📈 AI Stock Analytics Dashboard")

st.sidebar.markdown("""
### Features

✅ Real-Time Stock Data

✅ Candlestick Charts

✅ RSI Analysis

✅ Buy/Sell/Hold Signals

✅ Portfolio Tracker

✅ Stock Comparison

✅ Latest Stock News

✅ Download Reports
""")

st.markdown("""
# 🚀 AI-Powered Stock Market Intelligence Platform

### Real-Time Analytics • Portfolio Tracking • Technical Indicators • Market Insights
""")

symbol = st.text_input(
    "Enter Stock Symbol",
    "AAPL"
).upper()

if symbol:

    try:
        df = yf.download(
            symbol,
            period="6mo",
            interval="1d",
            auto_adjust=True
        )

        if df.empty:
            st.error("No data found.")
            st.stop()

        close_prices = df["Close"].squeeze()

        df["MA20"] = close_prices.rolling(20).mean()
        df["MA50"] = close_prices.rolling(50).mean()
        df["RSI"] = calculate_rsi(close_prices)

        # Bollinger Bands
        df["STD20"] = close_prices.rolling(20).std()
        df["Upper_Band"] = df["MA20"] + (df["STD20"] * 2)
        df["Lower_Band"] = df["MA20"] - (df["STD20"] * 2)

        latest_price = float(close_prices.iloc[-1])
        latest_rsi = float(df["RSI"].iloc[-1])
        # Risk Analysis
        returns = close_prices.pct_change().dropna()
        volatility = returns.std() * 100

        if volatility < 2:
            risk_level = "🟢 Low"
        elif volatility < 4:
            risk_level = "🟡 Medium"
        else:
            risk_level = "🔴 High"

        # AI Price Prediction
        prices = close_prices.dropna().values.reshape(-1, 1)

        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices

        model = LinearRegression()
        model.fit(X, y)

        next_day = np.array([[len(prices)]])
        predicted_price = float(model.predict(next_day)[0][0])

        predicted_change = (
            (predicted_price - latest_price)
            / latest_price
        ) * 100

        day_change = (
            (close_prices.iloc[-1] - close_prices.iloc[-2])
            / close_prices.iloc[-2]
        ) * 100

        if latest_rsi < 30:
            signal = "BUY"
            signal_color = "🟢"
            reason = "Stock appears oversold"
        elif latest_rsi > 70:
            signal = "SELL"
            signal_color = "🔴"
            reason = "Stock appears overbought"
        else:
            signal = "HOLD"
            signal_color = "🟡"
            reason = "Market is neutral"

        ticker = yf.Ticker(symbol)
        bollinger_signal = "Neutral"

        if latest_price > df["Upper_Band"].iloc[-1]:
            bollinger_signal = "Potential Overbought"
        elif latest_price < df["Lower_Band"].iloc[-1]:
            bollinger_signal = "Potential Oversold"

        try:
            info = ticker.info
        except:
            info = {}
        
        st.subheader("📌 Key Statistics")

        s1, s2, s3 = st.columns(3)

        s1.metric(
            "52 Week High",
            f"${info.get('fiftyTwoWeekHigh', 'N/A')}"
        )

        s2.metric(
            "52 Week Low",
            f"${info.get('fiftyTwoWeekLow', 'N/A')}"
        )

        market_cap = info.get("marketCap")

        if market_cap:
            s3.metric(
                "Market Cap",
                f"${market_cap/1e9:.2f}B"
            )
        else:
            s3.metric(
                "Market Cap",
                "N/A"
            )

        st.subheader("🏢 Company Information")

        col_a, col_b = st.columns(2)

        with col_a:
            st.write(
                f"**Company:** {info.get('longName', 'N/A')}"
            )
            st.write(
                f"**Sector:** {info.get('sector', 'N/A')}"
            )

        with col_b:
            st.write(
                f"**Industry:** {info.get('industry', 'N/A')}"
            )
            st.write(
                f"**Country:** {info.get('country', 'N/A')}"
            )

        st.subheader("📊 Market Overview")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
        "Current Price",
        f"${latest_price:.2f}",
        f"{day_change:.2f}%"
        )

        col2.metric(
            "RSI",
            f"{latest_rsi:.2f}"
        )

        col3.metric(
            "Signal",
            f"{signal_color} {signal}"
        )

        col4.metric(
            "Predicted Price",
            f"${predicted_price:.2f}",
            f"{predicted_change:.2f}%"
        )

        col5.metric(
            "Risk Level",
            risk_level
        )
        if predicted_change > 0:
            trend = "📈 Uptrend"
        else:
            trend = "📉 Downtrend"

        st.info(f"AI Trend Forecast: {trend}")

        st.info(reason)
        st.success(f"Bollinger Signal: {bollinger_signal}")
        if signal == "BUY" and predicted_change > 0:
            sentiment = "😊 Bullish"
        elif signal == "SELL" and predicted_change < 0:
             sentiment = "☹️ Bearish"
        else:
            sentiment = "😐 Neutral"

        st.info(f"Market Sentiment: {sentiment}")

        st.subheader("💼 Portfolio Tracker")

        quantity = st.number_input(
            "Number of Shares",
            min_value=1,
            value=10
        )

        buy_price = st.number_input(
            "Purchase Price ($)",
            min_value=0.0,
            value=latest_price
        )

        investment = quantity * buy_price
        current_value = quantity * latest_price
        profit_loss = current_value - investment

        if investment > 0:
            return_pct = (
                profit_loss / investment
            ) * 100
        else:
            return_pct = 0

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Investment",
            f"${investment:.2f}"
        )

        c2.metric(
            "Current Value",
            f"${current_value:.2f}"
        )

        c3.metric(
            "Profit/Loss",
            f"${profit_loss:.2f}"
        )

        c4.metric(
            "Return %",
            f"{return_pct:.2f}%"
        )
        st.subheader("🚨 Price Alert")

        target_price = st.number_input(
            "Set Target Price ($)",
            min_value=0.0,
            value=latest_price + 10
        )

        if latest_price >= target_price:
            st.error(
                f"🚨 ALERT! {symbol} has reached your target price of ${target_price:.2f}"
            )
        else:
            st.success(
                f"Current Price: ${latest_price:.2f} | Waiting for Target: ${target_price:.2f}"
            )

        st.subheader("📈 Candlestick Chart")

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MA20"],
                mode="lines",
                name="20-Day MA"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MA50"],
                mode="lines",
                name="50-Day MA"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Upper_Band"],
                mode="lines",
                name="Upper Bollinger Band"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Lower_Band"],
                mode="lines",
                name="Lower Bollinger Band"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("📊 Stock Comparison")

        st.subheader("⭐ Watchlist")

        watchlist = ["AAPL", "MSFT", "NVDA", "TSLA"]

        watchlist_data = []

        for stock in watchlist:
            try:
                stock_info = yf.download(
                    stock,
                    period="5d",
                    auto_adjust=True,
                    progress=False
                )

                if not stock_info.empty:
                    current = float(stock_info["Close"].iloc[-1])
                    previous = float(stock_info["Close"].iloc[-2])

                    change = ((current - previous) / previous) * 100

                    watchlist_data.append({
                        "Stock": stock,
                        "Price": round(current, 2),
                        "Change %": round(change, 2)
                    })

            except:
                pass

        watchlist_df = pd.DataFrame(watchlist_data)

        st.dataframe(
            watchlist_df,
            use_container_width=True
        )

        compare_stocks = st.multiselect(
            "Select Stocks",
            ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL"],
            default=["AAPL", "MSFT"]
        )

        comparison_fig = go.Figure()

        for stock in compare_stocks:

            stock_df = yf.download(
                stock,
                period="6mo",
                auto_adjust=True
            )

            if not stock_df.empty:

                comparison_fig.add_trace(
                    go.Scatter(
                        x=stock_df.index,
                        y=stock_df["Close"],
                        mode="lines",
                        name=stock
                    )
                )

        comparison_fig.update_layout(
            template="plotly_dark",
            height=500,
            title="Multi Stock Comparison"
        )

        st.plotly_chart(
            comparison_fig,
            use_container_width=True
        )

        st.subheader("📰 Latest Stock News")

        feed = feedparser.parse(
            f"https://news.google.com/rss/search?q={symbol}+stock"
        )

        if feed.entries:

            for entry in feed.entries[:5]:

                st.markdown(
                    f"• [{entry.title}]({entry.link})"
                )

        report = f"""
AI Stock Analytics Report

Stock: {symbol}

Current Price: ${latest_price:.2f}

RSI: {latest_rsi:.2f}

Signal: {signal}

Reason: {reason}

Investment: ${investment:.2f}

Current Value: ${current_value:.2f}

Profit/Loss: ${profit_loss:.2f}

Return Percentage: {return_pct:.2f}

Predicted Price: ${predicted_price:.2f}

Predicted Change: {predicted_change:.2f}%

Risk Level: {risk_level}
"""

        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"{symbol}_analysis_report.txt",
            mime="text/plain"
        )
    
        st.markdown("---")
        st.caption(
            "Built with Streamlit • Yahoo Finance • Plotly • Scikit-Learn"
        )

    except Exception as e:
        st.error(f"Error: {e}")