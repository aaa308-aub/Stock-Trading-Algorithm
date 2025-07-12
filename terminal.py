import os, json, pathlib, sys

import pandas, yfinance

from backtester import backtest

def init_initialBalance():
    while True:
        initialBalance = input("Please enter your initial balance in USD (or enter \"exit\" to exit the program):\n\n>> ")
        if initialBalance == "exit":
            sys.exit()
        try:
            initialBalance = float(initialBalance)
            if initialBalance < 10000:
                print("Sorry, the minimum initial balance is $10000.00")
            else: return round(initialBalance, 3)
        except ValueError:
            print("Please enter a valid initial balance.")

def commands_help(initialBalance):
    print(f"""\
COMMANDS:
1. help
  Show this list of commands again.
2. ticker.add <ticker symbol>
  Add stock data of user's input ticker to memory.
  If the ticker symbol is invalid or ticker data already added, raise the appropriate flag.
3. ticker.remove <ticker symbol>
  Remove stock data of user's input ticker to memory.
  If the ticker not in memory, raise the appropriate flag.
  If backtested on, changes to portfolio WILL be reverted.
4. ticker.backtest <ticker symbol>
  Backtest on stock data of user's input ticker. Must be added via command ticker.add first.
  If ticker's stock data not in memory, raise the appropriate flag.
  If ticker already backtested on, prompt the user whether to show the results of that backtest.
  Once validated and the backtest is done, prompt the user whether to apply changes to portfolio.
5. ticker.list
  Show all backtested and non-backtested tickers currently in memory.
6. portfolio
  Show portfolio.
7. reset
  Start over with the same initial balance of ${initialBalance:.2f}. All tickers will be wiped from memory.
8. reset.hard
  Start over completely with a new initial balance. All tickers will be wiped from memory.
  NOTE: Current initial balance is ${initialBalance:.2f}
9. exit
  Exit the program. All user data (tickers, stock data, portfolio, etc.) are saved in memory.
""")

def main():

    def save_tickerData(tickerData):
        with open(ticker_data_path, 'w') as f:
            json.dump(tickerData, f, indent=2)

    def save_portfolio(portfolio):
        with open(portfolio_path, 'w') as f:
            json.dump(portfolio, f, indent=2)

    def init_portfolio(first_time_message = True):
        if first_time_message: print("""\
We have detected that you do not have a portfolio.
Let's start by making your portfolio with an initial balance.
""")

        initialBalance = init_initialBalance()
        portfolio = {"balance": initialBalance, "initial-balance": initialBalance}
        save_portfolio(portfolio)
        if first_time_message: commands_help(initialBalance)

    data_folder = pathlib.Path("Data")
    os.makedirs(data_folder, exist_ok=True)

    ticker_data_path = data_folder / "tickerdata.json"
    if not ticker_data_path.exists():
        save_tickerData({})
    with open(ticker_data_path, 'r') as f:
        tickerData = json.load(f)

    print("Welcome to your personal Stock Trading Algorithm (STA)", end='\n\n')

    portfolio_path = data_folder / "portfolio.json"
    if not portfolio_path.exists():
        init_portfolio()
    with open(portfolio_path, 'r') as f:
        portfolio = json.load(f)

    while True:
        command = input(">> ")

        if command == "help":
            commands_help(portfolio["initial-balance"])

        elif command == "exit":
            sys.exit()

        elif command.startswith("ticker.add"):
            ticker = command[11:].upper()
            if ticker == '' or ' ' in ticker:
                print("Please enter a valid ticker after the command as one word. Example: \"ticker.add AAPL\"", end='\n\n')
                continue

            csv_path = data_folder / f"{ticker}.csv"
            if csv_path.exists():
                print(f"Ticker \"{ticker}\" is already in memory", end='\n\n')
                continue

            df = yfinance.download(ticker, period='5y', interval='1d', auto_adjust=True)
            if df.empty:
                print(f"ERROR: Could not fetch stock data for ticker \"{ticker}\", likely due to invalid ticker, unavailable data, or network issues", end='\n\n')
                continue
            if len(df) < 500: # in 730 days (2 years), there are 500 trading days
                print(f"ERROR: Not enough stock data for ticker \"{ticker}\". Please enter a ticker that has been registered for at least 2 years", end='\n\n')
                continue
            df = df.xs(ticker, level="Ticker", axis=1) # df is multi-indexed, even for 1 ticker downloaded. Must slice.
            df.to_csv(csv_path)

            ticker_info = yfinance.Ticker(ticker).get_info()
            # sometimes data is missing; even company name
            companyName = (ticker_info.get("longName") or ticker_info.get("shortName") or "UNKNOWN COMPANY")
            tickerData[ticker] = {"company-name": companyName, "backtested": False, "net-change": 0.0}
            save_tickerData(tickerData)

            if companyName == "UNKNOWN COMPANY":
                print(f"Stock data for ticker \"{ticker}\" successfully downloaded. NOTE: Company name could not be fetched, likely missing from stock data.", end='\n\n')
            else:
                print(f"Stock data for ticker \"{ticker}\" / company named \"{companyName}\" successfully downloaded.", end='\n\n')

        elif command.startswith("ticker.remove"):
            ticker = command[14:].upper()
            if ticker == '' or ' ' in ticker:
                print("Please enter a valid ticker after the command as one word. Example: \"ticker.remove AAPL\"", end='\n\n')
                continue

            csv_path = data_folder / f"{ticker}.csv"
            if not csv_path.exists():
                print(f"Cannot remove ticker \"{ticker}\" because it is not in memory.", end='\n\n')
                continue

            csv_path.unlink()
            inputTickerData = tickerData.pop(ticker)
            save_tickerData(tickerData)
            print(f"Data for ticker \"{ticker}\" successfully removed.")
            if inputTickerData["backtested"]:
                portfolio["balance"] -= inputTickerData["net-change"]
                save_portfolio(portfolio)
                print(f"NOTE: This ticker was backtested on. Its net-change of {inputTickerData["net-change"]:+.2f} has been reverted and your balance is now ${portfolio["balance"]:.2f}", end='\n\n')
            else: print('')

        elif command.startswith("ticker.backtest"):
            ticker = command[16:].upper()
            if ticker == '' or ' ' in ticker:
                print("Please enter a valid ticker after the command as one word. Example: \"ticker.backtest AAPL\"", end='\n\n')
                continue
            csv_path = data_folder / f"{ticker}.csv"
            if not csv_path.exists():
                print(f"Data of ticker \"{ticker}\" not in memory. Please add the ticker first using the ticker.add command.", end='\n\n')
                continue
            if tickerData[ticker]["backtested"] == True:
                print(f"The input ticker \"{ticker}\" has already been backtested on. Its net-change is {tickerData[ticker]["net-change"]:+.3f}", end='\n\n')
                continue
            
            while True:
                balance_allocated = input("How much of your balance (in %%) would you like to allocate to this backtest? (input between 5%% and 40%%): " )
                try:
                    balance_allocated = float(balance_allocated[:-1]) if balance_allocated[-1]=='%' else float(balance_allocated)
                    if balance_allocated < 5 or balance_allocated > 40:
                        print("Please enter valid inputs only.", end='\n\n')
                        continue
                    balance_allocated = portfolio["balance"] * balance_allocated / 100
                    break
                except ValueError:
                    print("Please enter valid inputs only.", end='\n\n')
                    continue

            while True:
                term = input("Do you want to apply SMA cross-over method in the short-term 20 & 50 moving-average or the long-term 50 & 200? (input \"short\" or \"long\"):" )
                if not (term == 'short' or term == 'long'):
                    print("Please enter valid inputs only.", end='\n\n')
                    continue
                break
            
            while True:
                risk_control = input("Apply risk control (method: Average True Range (ATR))? (yes/no): ")
                if not (risk_control == "yes" or risk_control == "no"):
                    print("Please enter valid inputs only.", end='\n\n')
                    continue
                risk_control = (risk_control == "yes")
                break

            net_change = backtest(ticker, csv_path, balance_allocated, term, risk_control)
            portfolio["balance"] = round(portfolio["balance"] + net_change, 3)
            tickerData[ticker]["backtested"] = True
            tickerData[ticker]["net-change"] = net_change
            save_portfolio(portfolio)
            save_tickerData(tickerData)
            print(f"Backtest successful. The net-change is {net_change:+.2f}. Your balance is now ${portfolio["balance"]:+.2f}.", end = '\n\n')

        elif command == "ticker.list":
            listTickers_backtested = []
            listTickers_notBacktested = []
            for ticker in tickerData:
                if tickerData[ticker]["backtested"]:
                    listTickers_backtested.append(ticker)
                else: listTickers_notBacktested.append(ticker)
            if not (listTickers_backtested or listTickers_notBacktested):
                print("No tickers have been added yet to memory.", end='\n\n')
                continue
            print(f"List of backtested tickers: {(listTickers_backtested if listTickers_backtested else None)}")
            print(f"List of tickers not backtested yet: {(listTickers_notBacktested if listTickers_notBacktested else None)}", end='\n\n')

        elif command == "portfolio":
            print(f"Balance: ${portfolio["balance"]:.2f}")
            print(f"Initial Balance: ${portfolio["initial-balance"]:.2f}", end='\n\n')

        elif command == "reset":
            initialBalance = portfolio["initial-balance"]
            for file in data_folder.iterdir():
                file.unlink()
            tickerData = {}
            save_tickerData(tickerData)
            portfolio = {"balance": initialBalance, "initial-balance": initialBalance}
            save_portfolio(portfolio)
            print(f"Your portfolio has been reset. Your balance is now ${initialBalance:.2f}", end='\n\n')

        elif command == "reset.hard":
            for file in data_folder.iterdir():
                file.unlink()
            tickerData = {}
            save_tickerData(tickerData)
            init_portfolio(first_time_message=False)
            with open(portfolio_path, 'r') as f:
                portfolio = json.load(f)
            print(f"Your portfolio has been reset. Your balance is now ${portfolio["initial-balance"]:.2f}", end='\n\n')

        else:
            print("Please enter a valid command. Enter \"help\" to show list of commands.", end='\n\n')

if __name__ == "__main__":
    main()