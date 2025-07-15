# GOAL:
The purpose of this project is to apply and test the Simple Moving Average (SMA) Crossover Method on stock data. The stock data used is "historical," meaning the test will be applied on recent (~5 years timeframe) stock data. This methodology is known as "backtesting."

# METHOD:
The method is simple and well-known. Use 2 types of moving averages of "Close" prices. A "Close" price is the price of the share at the end of the trading day, specifically the last trade. The Moving Average (MA) is the average of the "Close" prices over the last N-days, where N is a fixed number of days. When "today's" Close price is more than yesterday's moving average, it signals an upward momentum, or a downward momentum if it's less. The program gives the user a choice of either the short-term method (20 SMA & 50 SMA) or the long-term one (50 SMA & 200 SMA). SMA stands for "Simple Moving Average," where none of the days' Close prices computed in the MA are weighed more than the others. In contrast, the Exponential Moving Average (EMA) weighs the latest days' Close prices in the average's interval as more impactful, and the earliest less impactful. Although EMA is considered "better and more responsive" than SMA, it is out of this project's scope. We will be using SMA only.

Once the short SMA and long SMA are computed, we plot them on a graph alongside the Close price in the stock data. Note that the Close price is considered the most stable price that reflects most accurately the interpreted value of the shares. If the short SMA passes above the long SMA on the graph, this signals there is momentum for the price increasing. Sometimes this momentum is short-term, but sometimes it lasts for months or even years. We buy at this crossover, and when the short SMA crosses below the long SMA, this signals the momentum is fading and that we should sell.

# PROGRAM HOW-TO-USE AND FEATURES:
1. Install dependencies with this command in your terminal:
pip install -r requirements.txt

2. Run the program using:
python main.py

3. Your portfolio is initially at $10,000. You can change it by pressing "NEW BALANCE".

4. Add your desired ticker in the entry box below the portfolio box and hit "ADD TICKER". The program will download the ticker's historical stock data through Yahoo Finance, which covers a very large portion of the US Market, but may lack data for small-cap markets. Note that the ticker must have a minimum history of data of 2 years, or the program will raise the error "NOT ENOUGH DATA".

5. Select your desired ticker from the dropmenu that lists all your added tickers. Backtest the selected ticker and apply your desired settings: how much balance you'd like to allocate (between 5 and 40 percent of your current balance), apply risk control (method: Average True Range) to mitigate losses, and the method: short-term or long-term.

6. An interactive graph will pop-up on your screen. Your tools are on the bottom-left. HINT: Press the magnifying glass icon and hold left-click to draw a box on what part of the graph you'd like to see closer. hold right-click to zoom out (it's a bit unintuitive but it works).

7. Once the backtest is complete, you can see some basic results at the bottom of the main window: the company name, the backtest settings, the balance allocated, the final balance after backtesting, the net-change, and the highest win and loss. Note that the net-change is immediately applied to your portfolio. The "Net (%)" you see in your portfolio box is simply the relation between your balance and initial balance, while the "Net Change" you see in the backtest results box below is between the balance you've allocated and the final balance.

8. Press the "REMOVE TICKER" button to remove the selected ticker. For consistency reasons, this WILL revert the net-change of its backtest (if backtested) that has been applied on the portfolio.

9. The "RESET" button will reset your initial balance and remove all your tickers (!). The "NEW BALANCE" does the same, but let you enter a new balance instead of reverting to the initial.


# OBSTACLES AND LIMITATIONS:
On paper, the method sounds simple to implement. But there are obstacles that limit the accuracy of the data we try to reproduce.

Stocks are bought or sold via a broker (an intermediary that carries out your trades). Brokers typically charge fees, and these fees vary: some brokers offer commission-free trades (but they take some of your profits), others charge static fees or fees that differ by the type of stock, the volume of shares per buy/sell order, etc. These fees are usually tiny, but they can add-up. As a compromise to all this variance, my program simply adds 1 cent to the price of the stock being bought (i.e. 1 cent per share) to reflect these broker fees.

Using the crossover method incurs possibly losing heaps of money due to no risk control. A risk control method called "Average True Range" is applied to mitigate these losses. With this method, we essentially check whether there is a strong downward momentum on a given day's Close price, relative to the volume and volatility of the past 2 weeks. If there is, we sell to not risk losing more money. This "Risk Control" setting is decided by the user.

When stock is ordered for buying/selling, the price you get per share bought/sold is usually just shy of the price you expect (i.e. the price you see on the graph). This is known as "Slippage" and is due to many reasons. To name a few:
1. The Close price does not reflect the best bidder or buyer, let alone the case for ALL the shares you are buying/selling.
2. Your order is in a queue with other orders. In other words, you are usually waiting in a line for the other orders to be processed, and by the time they are, the price you receive may be different than the one you ordered for. Even if the stock is not "volatile", stocks inherently carry noise and volatility.
3. Elaborating on point #2, many things contribute to the change in market data. The news, the politics, the company's performance, whether that company plays a pivotal role in its industry (like Nvidia's role in AI)... or even just emotional impulses that push people to buy or sell.

Unfortunately, due to the close-guarding of accurate market data brokers have, and the sheer costs of reproducing and maintaining this data, brokers charge very large fees for such accuracy, which is still attenuated. For this reason, accurately calculating the slippage is practically impossible. I learned this the hard way when i tried to pivot to a broker's trading API to calculate slippage.

Instead, my program estimates the slippage through calculating ranges between highs and lows, and the normalized volume on a given day (similar to moving average, but instead it's the moving average of the volume of shares, and the volume of shares bought on a given day is divided over this "moving volume" to give us the normalized volume). The high-to-low ranges give us an idea of how volatile the stock market is, and are therefore proportional to slippage. The normalized volume gives us an estimate of liquidity, and is therefore inversely proportional to slippage. I have biased this slippage with a control bias and a limit between 0.05% and 5%. That's the best we can do without intraday data.

# OBSERVATIONS:
Both the short-term approach (20 & 50 SMA) and the long-term (50 & 200 SMA) have their merits and limitations.

The most immediate and unsurprising observation is that the long-term approach typically outperforms the short-term in large-cap stocks that you should probably hold for long periods of time. For example, Netflix (ticker: NFLX) and Nvidia (ticker: NVDA) stocks have been on the rise for a very long time, and the long-term approach shines in this type of market.

Another unsurprising result is that the long-term approach performs very poorly in stocks that have high day-to-day volatility. For example, the Tesla stock (ticker: TSLA) has formed, over the last 5 years, very thin and sharp "icycles" both high and low. The long-term approach simply fails in such cases. Although the short-term approach doesn't guarantee success in such stock market climates, it usually performs better than the long-term.

The short-term approach performs well in less volatile stock markets with high liquidity, but results can vary.

The method used is not perfect (what is?). I had great results, but again they widely vary, and sometimes the losses are tragically high. The risk-control algorithm set in place does work, though not as effectively as I'd hoped. Perhaps its performance shows best in volatile stocks. Regardless, the method being ineffective in a lot of cases is not unexpected, because the method lacks context about the stock market, as well as the political climate, the news, the company's performance, its controversies, etc. Context is important; there is no clear-cut and closed method that works consistently without the proper context.