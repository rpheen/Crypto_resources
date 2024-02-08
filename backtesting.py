import backtrader as bt

# Placeholder for the RibbonIndicator - Implement based on your ribbon's specifications
class RibbonIndicator(bt.Indicator):
    lines = ('green', 'outer_bands_spread',)

# Ribbon Scalp Strategy
class RibbonScalpStrategy(bt.Strategy):
    params = (
        ('exit_on_spread', True),
        ('yellow_ma_period1', 10),
        ('yellow_ma_period2', 20),
    )
    
    def __init__(self):
        self.ribbon = RibbonIndicator(self.data)
        self.yellow_ma1 = bt.indicators.MovingAverageSimple(self.data, period=self.p.yellow_ma_period1)
        self.yellow_ma2 = bt.indicators.MovingAverageSimple(self.data, period=self.p.yellow_ma_period2)
        self.in_position = False
        self.cumulative_profit = 0  # To track cumulative profit/loss

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def next(self):
        if self.ribbon.green[0] and not self.in_position:
            self.log('Ribbon turned green, BUY CREATE, %.2f' % self.data.close[0])
            self.buy()
            self.in_position = True

        if self.in_position and self.params.exit_on_spread and self.ribbon.outer_bands_spread[0]:
            self.log('Outer bands spreading, SELL CREATE, %.2f' % self.data.close[0])
            self.close()
            self.in_position = False

        if self.in_position:
            if self.data.close[0] > self.yellow_ma1[0] or self.data.close[0] > self.yellow_ma2[0]:
                self.log('Price bouncing off yellow MA, stay in position')
            elif self.data.close[0] < self.yellow_ma1[0] and self.data.close[0] < self.yellow_ma2[0]:
                self.log('Price crossed below yellow MA, SELL CREATE, %.2f' % self.data.close[0])
                self.close()
                self.in_position = False

    def notify_trade(self, trade):
        if trade.isclosed:
            profit = trade.pnl  # pnl is profit and loss for the trade
            self.cumulative_profit += profit
            self.log(f'Trade Profit: {profit:.2f}, Cumulative Profit: {self.cumulative_profit:.2f}')

# Data Feed
data = bt.feeds.GenericCSVData(
    dataname='/home/rpheen/Documents/Crypto-trade/Crypto_resources/data/btc-15m-2020-random.csv',
    timeframe=bt.TimeFrame.Minutes,
    compression=15,
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1
)

# Initialize Cerebro Engine
cerebro = bt.Cerebro()
cerebro.addstrategy(RibbonScalpStrategy)
cerebro.adddata(data)

# Set initial capital
initial_capital = 10000
cerebro.broker.setcash(initial_capital)

# Print starting capital
print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')

# Run the backtest
results = cerebro.run()

# Print final capital and profit/loss
final_capital = cerebro.broker.getvalue()
print(f'Final Portfolio Value: {final_capital:.2f}')
profit_loss = final_capital - initial_capital
print(f'Profit/Loss: {profit_loss:.2f}')

# Plot the results (if tkinter is installed and working)
cerebro.plot()
