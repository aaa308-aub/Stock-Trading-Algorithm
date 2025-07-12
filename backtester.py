import pathlib

import matplotlib.pyplot as plt
import pandas

def backtest(ticker, csv_path, balance_allocated, term, risk_control):

    def findATR(): # Average True Range
        df["Prev. Close"] = df["Close"].shift(1)
        df["TR"] = df[["High", "Low", "Prev. Close"]].apply(
            lambda row: max(
                row["High"] - row["Low"],
                abs(row["High"] - row["Prev. Close"]),
                abs(row["Low"] - row["Prev. Close"])
            ),
            axis=1
        )
        df["ATR"] = df["TR"].rolling(14).mean()

    def findSA(): # Slippage Adjustment (in %)
        df["Prop. Range"] = (df["High"] - df["Low"]) / df["Close"]
        df["Avg. Volume"] = df["Volume"].rolling(30).mean()
        df["Norm. Volume"] =  df[["Volume", "Avg. Volume"]].apply(
            lambda row: row["Volume"] / max(row["Avg. Volume"], 1), axis=1) 

        control_bias = 0.1
        df["SA"] = df[["Prop. Range", "Norm. Volume"]].apply(
            lambda row: control_bias * row["Prop. Range"] / row["Norm. Volume"], axis=1)
        df["SA"] = df["SA"].apply(lambda sa: max(0.2, min(sa, 2)))

    # Receive all data needed
    df = pandas.read_csv(csv_path, parse_dates=["Date"], index_col="Date")
    df = df[~df.index.duplicated(keep='first')]
    short = 20 if term == "short" else 50
    long = 50 if term == "short" else 200
    shortSMA_label = f"SMA {short}"
    longSMA_label = f"SMA {long}"
    df[shortSMA_label] = df["Close"].rolling(short).mean()
    df[longSMA_label] = df["Close"].rolling(long).mean()
    if risk_control: findATR()
    findSA()
    df = df[long:]

    # Simulate buying and selling stocks with 1-cent fee per share bought and slippage
    net_change = 0
    yesterday = df.index[0]
    buyDate, matchDate = None, []
    for today in df.index[1:]:

        today_shortSMA = df.loc[today, shortSMA_label]
        today_longSMA = df.loc[today, longSMA_label]
        yesterday_shortSMA = df.loc[yesterday, shortSMA_label]
        yesterday_longSMA = df.loc[yesterday, longSMA_label]

        if (not buyDate) and today_shortSMA > today_longSMA and yesterday_shortSMA <= yesterday_longSMA:
            buyPrice = df.loc[today, "Close"] * (1 + df.loc[today, "SA"] / 100) + 0.01
            buyVolume = balance_allocated // buyPrice
            if buyVolume != 0:
                buyDate = today

        elif (
            (buyDate and risk_control and df.loc[today, "Close"] < (df.loc[buyDate, "Close"] - (2 * df.loc[today, "ATR"])))
            or (buyDate and today_shortSMA < today_longSMA and yesterday_shortSMA >= yesterday_longSMA)
        ):
            matchDate.append((buyDate, today))
            buyDate = None
            sellPrice = df.loc[today, "Close"]*(1 - df.loc[today, "SA"] / 100)
            net_change += (sellPrice - buyPrice) * buyVolume

        yesterday = today

    # Start plotting
    plt.figure(figsize=(14, 7))

    # Price and SMA lines
    plt.plot(df.index, df["Close"], label="Close Price", color="black", linewidth=1)
    plt.plot(df.index, df[shortSMA_label], label=shortSMA_label, color="orange", linestyle="--")
    plt.plot(df.index, df[longSMA_label], label=longSMA_label, color="purple", linestyle="--")

    # Buy/sell and win/loss labels
    for buy, sell in matchDate:

        buy_price, sell_price = df.loc[buy, "Close"], df.loc[sell, "Close"]
        net_change_percent = ((sell_price - buy_price) / buy_price) * 100
        plt.scatter(buy, buy_price, marker="^", color="green", label="Buy")
        plt.scatter(sell, sell_price, marker="^", color="red", label="Sell")

        mid_date = buy + (sell - buy) / 2
        mid_price = (buy_price + sell_price) / 2
        label = f"{net_change_percent:+.2f}%"
        plt.text(
            mid_date,
            mid_price,
            label,
            ha='center',
            va='center',
            fontsize=8,
            color='white',
            fontweight='bold',
            bbox=dict(
                boxstyle='round,pad=0.2',
                facecolor='green' if net_change_percent >= 0 else 'red',
                edgecolor='none',
                alpha=0.6
            )
        )

    # Buy/Sell labels in legend are duplicated. Must un-duplicate.
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles)) # Dictionary entries must be unique
    plt.legend(by_label.values(), by_label.keys()) # Dictionaries are ordered since Python v3.7

    # Polish graph
    plt.title(f"{term.capitalize()}-Term SMA Crossover Strategy for {ticker} ({("RISK-CONTROLLED" if risk_control else "NO RISK CONTROL")})")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Return result
    return round(net_change, 3)

# FOR TESTING OUTSIDE OF TERMINAL.PY:
# HOW-TO:
# work-around for downloading .csv files manually:
# run terminal.py and use ticker.add for the tickers you want to add
# remove single quotes of block you want to test
# defaults: balance_allocated = $1000, term = long, risk_control = True

# for testing short-term vs long-term.
'''
data_folder = pathlib.Path("Data")
net_change_short = 0
net_change_long = 0
for file in data_folder.iterdir():
    if file.name in ["tickerdata.json", "portfolio.json"]: continue
    net_change_short += backtest(file.stem, pathlib.Path('Data') / file.name, 1000, "short", True)
    net_change_long += backtest(file.stem, pathlib.Path('Data') / file.name, 1000, "long", True)
print(f"SHORT: {net_change_short:+.3f}")
print(f"LONG: {net_change_long:+.3f}")
'''

# for testing risk-control.
'''
data_folder = pathlib.Path("Data")
net_change = 0
net_change_controlled = 0
for file in data_folder.iterdir():
    if file.name in ["tickerdata.json", "portfolio.json"]: continue
    net_change += backtest(file.stem, pathlib.Path('Data') / file.name, 1000, "long", False)
    net_change_controlled += backtest(file.stem, pathlib.Path('Data') / file.name, 1000, "long", True)
print(f"NO RISK CONTROL: {net_change:+.3f}")
print(f"CONTROLLED: {net_change_controlled:+.3f}")
'''