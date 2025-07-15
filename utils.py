_libs = {}

def save_tickerData(tickerData):
    with open(ticker_data_path, 'w') as f:
        json.dump(tickerData, f, indent=2)

def save_portfolio(portfolio):
    with open(portfolio_path, 'w') as f:
        json.dump(portfolio, f, indent=2)

def init():
    # import libraries dynamically and assign global references to them for top-level access.
    import importlib
    for lib in ["os", "json", "pathlib", "pandas", "yfinance", "backtester"]:
        _libs[lib] = importlib.import_module(lib)

    global os, json, pl, pd, yf, backtest
    os = _libs["os"]
    json = _libs["json"]
    pl = _libs["pathlib"]
    pd = _libs["pandas"]
    yf = _libs["yfinance"]
    backtest = _libs["backtester"].backtest

    global data_folder, ticker_data_path, tickerData, portfolio_path, portfolio
    data_folder = pl.Path("Data")
    os.makedirs(data_folder, exist_ok=True)

    ticker_data_path = data_folder / "tickerdata.json"
    if not ticker_data_path.exists():
        save_tickerData({})
    with open(ticker_data_path, 'r') as f:
        tickerData = json.load(f)

    portfolio_path = data_folder / "portfolio.json"
    if not portfolio_path.exists():
        portfolio = {"balance": 10000, "initial-balance": 10000, "net": 0}
        save_portfolio(portfolio)
    with open(portfolio_path, 'r') as f:
        portfolio = json.load(f)

def ticker_add(ticker):
    ticker = ticker.upper()
    if ticker == '' or ' ' in ticker:
        raise Exception("INVALID TICKER")

    csv_path = data_folder / f"{ticker}.csv"
    if csv_path.exists():
        raise Exception("ALREADY IN MEMORY")
    
    # Sometimes the DataFrame downloaded from yfinance is multiindexed.
    # To circumvent this, we force multiindexing by inputting the ticker as a list.
    # Then, we can slice the DataFrame.
    df = yf.download([ticker], period='5y', interval='1d', auto_adjust=True)
    if df.empty:
        raise Exception(f"NO DATA FOUND")
    if len(df) < 500: # I set the minimum to 2 years (= ~500 trading days). TEST TICKER: ZONE
        raise Exception(f"NOT ENOUGH DATA")
    df = df.xs(ticker, level="Ticker", axis=1)
    df.to_csv(csv_path)

    ticker_info = yf.Ticker(ticker).get_info()
    # Sometimes the company name is missing.
    companyName = (ticker_info.get("longName") or ticker_info.get("shortName") or "UNKNOWN COMPANY")

    tickerData[ticker] = {
        "company-name": companyName,
        "backtested": False,
        "term": None,
        "risk-control": None,
        "balance-allocated": None,
        "final-balance": None,
        "net-change": None,
        "highest-win": None,
        "highest-loss": None
    }
    save_tickerData(tickerData)

def ticker_remove(ticker):
    ticker = ticker.upper()
    if ticker == '' or ' ' in ticker:
        raise Exception("INVALID TICKER")

    csv_path = data_folder / f"{ticker}.csv"
    if not csv_path.exists():
        raise Exception("NOT IN MEMORY")

    csv_path.unlink()
    inputTickerData = tickerData.pop(ticker)
    save_tickerData(tickerData)

    if inputTickerData["backtested"]:
        net = inputTickerData["final-balance"] - inputTickerData["balance-allocated"]
        portfolio["balance"] -= net
        save_portfolio(portfolio)

def reset_portfolio(newBalance=None):
    for file in data_folder.iterdir():
        file.unlink()
    tickerData.clear()
    save_tickerData(tickerData)
    if not newBalance:
        portfolio["balance"] = portfolio["initial-balance"]
        portfolio["net"] = 0
    else:
        portfolio["initial-balance"] = newBalance
        portfolio["balance"] = newBalance
        portfolio["net"] = 0
    save_portfolio(portfolio)

def ticker_backtest(ticker, balance_allocated, term, risk_control):
    ticker = ticker.upper()
    if ticker == '' or ' ' in ticker:
        raise Exception("INVALID TICKER")

    csv_path = data_folder / f"{ticker}.csv"
    if not csv_path.exists():
        raise Exception("NOT IN MEMORY")

    stats = backtest(ticker, csv_path, balance_allocated, term, risk_control)

    net = stats["final-balance"] - stats["balance-allocated"]
    portfolio["balance"] = round(portfolio["balance"] + net, 3)
    tickerData[ticker]["backtested"] = True
    tickerData[ticker]["term"] = stats["term"]
    tickerData[ticker]["risk-control"] = stats["risk-control"]
    tickerData[ticker]["balance-allocated"] = stats["balance-allocated"]
    tickerData[ticker]["final-balance"] = stats["final-balance"]
    tickerData[ticker]["net-change"] = stats["net-change"]
    tickerData[ticker]["highest-win"] = stats["highest-win"]
    tickerData[ticker]["highest-loss"] = stats["highest-loss"]
    save_portfolio(portfolio)
    save_tickerData(tickerData)