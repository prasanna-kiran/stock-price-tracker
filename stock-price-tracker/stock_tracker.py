import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def calculate_rsi(data, period=14):
    delta = data.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

def main():
    symbol = input("Enter stock symbol (e.g., AAPL, TSLA, MSFT): ").strip().upper()

    period = "60d"
    interval = "1d"

    df = yf.download(symbol, period=period, interval=interval)

    if df.empty:
        print("No data found for symbol:", symbol)
        return

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = calculate_rsi(df["Close"])

    latest_price = float(df["Close"].iloc[-1])
    latest_rsi = float(df["RSI"].iloc[-1])

    if latest_rsi < 30:
        signal = "BUY"
        reason = "Stock is oversold"
    elif latest_rsi > 70:
        signal = "SELL"
        reason = "Stock is overbought"
    else:
        signal = "HOLD"
        reason = "Market is neutral"

    print("\n========== STOCK ANALYSIS ==========")
    print(f"Stock: {symbol}")
    print(f"Current Price: ${latest_price:.2f}")
    print(f"RSI: {latest_rsi:.2f}")
    print(f"Recommendation: {signal}")
    print(f"Reason: {reason}")
    print("====================================")

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

    fig.update_layout(
        title=f"{symbol} Stock Analysis Dashboard",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=700
    )

    fig.show()

if __name__ == "__main__":
    main()