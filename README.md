# GOAL:
The purpose of this project is to apply and test the Simple Moving Average (SMA) Crossover Method on stock data using
"tickers". Tickers are symbols that represent the stock, like "MSFT" for Microsoft stock or "NVDA" for Nvidia stock.
The stock data being used is historical, meaning the test will be applied on recent (5> years) stock data. This method
is known as "backtesting."

# METHOD:
The method is simple and quite well-known. Use 2 types of moving averages, which are defined as averages over the last
N-days, where N is a fixed number of days. One of the moving averages, or MA for short, must be "short-term" while the
other is "long-term". The program gives the user a choice of a short-term approach (20 SMA and 50 SMA) and a long-term
one (50 SMA and 200 SMA). SMA stands for "Simple Moving Average," where none of the days computed in the MA is
"weighed" more than the other. EMA (Exponential Moving Average) weighs the latest days in the moving average's
interval as more impactful, and the earliest days in the interval less. Although EMA is considered "better and more
responsive", it is out of this project's scope. We will be using SMA only.

Once the short-term SMA and long-term SMA are computed, we plot them on a graph alongside the "Close" price in the
stock data (the most stable price that reflects most accurately the viewed price of the stock). If the short-term SMA
passes above the long-term SMA on the graph, this signals that there is short-term momentum for the price increasing,
which usually lasts for a few days (sometimes not for long, sometimes for months or even years). This is the time to
buy. In contrast, when the short-term SMA passes below the long-term SMA, this signals that the momentum is fading,
and that's when we sell.

# OBSTACLES AND LIMITATIONS:
On paper, the method sounds simple. In practice, there are many obstacles we must try to overcome, or mention here
at the very least.

When stock is bought or sold using a broker (an intermediary that carries out these trades), the broker typically
charges fees. These fees vary widely between different brokers. Some of them are commission free (though they take
some of your profits). Others charge static fees, or fees that differ by the type of stock, the volume of shares
you buy/sell, etc. These fees are usually not large (on paper; they can add up quickly). My program simply adds
1 cent to the price of the stock being bought, and sees how many shares you can buy given the balance allocated.
This is a good compromise between wildly different types of broker fees.

Using this method, there is always the possibility of losing heaps of money due to no risk control. A risk
control method called "Average True Range" is applied to mitigate these losses. Results may vary.

When stock is ordered for buying/selling, the price you get is usually shy of the price you expect (i.e., the
price you see on the graph). This is known as "Slippage" and is due to many reasons. To name a few:
1. The Close price does not reflect the best bidder or buyer, let alone the case for ALL the shares you trade with.
2. Your order is in a queue with other orders. In other words, you are usually waiting in a line for the order to
   be processed, and by the time it is, the price you receive may be different then what you'd expect. Even if the
   stock is not "volatile," stocks inherently carry a lot of "noise" and "volatility."
3. Elaborating on point #2, many things contribute to the change in market data. The news, the politics, the company's
   performance, whether that company is a pioneer in an industry (like Nvidia's pivotal role in Artificial Intelligence)
   or even just emotional impulses that push people to buy or sell.

Unfortunately, due to the close-guarding of accurate market data and the sheer costs of maintaining the infrastructure of
the programs and algorithms that get this data, brokers charge large fees for such accuracy (and it's still attenuated).
For this reason, accurately calculating the slippage is practically impossible. I learned this the hard way when I tried
to pivot to a broker's trading API to calculate slippage as accurately as possible. So instead, my program estimates the
slippage in a biased yet realistic fashion, through calculating ranges between highs and lows (proportional to slippage)
and the normalized volume (similar to moving average, but instead it's the moving average of the volume of shares) and
the ratio of the volume of shares over this normalized volume (inversely proportional to slippage).

# HOW TO USE THIS PROGRAM:
1. Install dependencies with this command in your terminal:
pip install -r requirements.txt
2. Run the program using:
python terminal.py
3. Make your portfolio when prompted and read the commands list.
4. Backtested tickers will pop-up the graph that contains the relevant data, and the total profit/loss will be added.
5. If you'd like to see more, there are also some tests in the backtester.py script.
6. Enjoy!

# FEATURES:
1. Data is plotted in an interactive graph using the matplotlib library in Python for clarity and readability.
2. A small and modest portfolio, and tracking of stock data and backtested tickers.
3. Support for most of large-cap US market stocks. DOES NOT (or atleast should not) support small volume stocks,
   OTC (Over-The-Counter) stocks, etc.
4. Choice of applying risk control.
5. Choice of applying the short-term or long-term approach.
6. Somewhat realistic simulation of fees and slippage.

# OBSERVATIONS:
Both the short-term approach (20 and 50 SMA) and the long-term (50 and 200 SMA) have their merits and limitations.

The most immediate and unsurprising observation is that the long-term approach typically outperforms the short-term in
stocks that you probably should typically hold for long periods of time, such as Netflix (ticker: NFLX) that has been on
the rise for over 5 years in terms of stock price, and Nvidia (ticker: NVDA) for pioneering in the AI industry for a long time.

Another unsurprising result is that the long-term approach performs very poorly in stocks that have high day-to-day
volatility. For example, the Tesla stock (ticker: TSLA) has, over the last 5 years, very thin, sharp "icycles" both low and
high. The long-term approach simply fails in such cases, though the short-term may or may not perform much better.

The method used is not perfect (what is?), and although there can be some great results, results can still vary, and sometimes the
losses can be tragically high. The risk-control algorithm set in place does work, though not as effectively as I'd hoped. Perhaps its performance shows best in volatile stocks.

Both the short-term and long-term approach have varying results in "sideways stocks." The short-term noticeably outperforms in
downtrending stocks. The long-term, again, outperforms the short-term in the uptrending, especially the uptrends that last very long.