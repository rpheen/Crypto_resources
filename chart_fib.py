import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Fetch historical BTC data with 5-minute intervals
btc_data = yf.download('DOGE-USD', start='2024-01-07', end='2024-01-08', interval='5m')

# Calculate EMAs for the ribbon
ema_periods = [5, 8, 13, 21, 34, 55, 89, 144]  # Example periods
btc_data['EMA_5'] = btc_data['Close'].ewm(span=5, adjust=False).mean()
btc_data['EMA_21'] = btc_data['Close'].ewm(span=21, adjust=False).mean()

# Determine Buy and Sell signals
btc_data['Signal'] = 0
btc_data['Signal'][5:] = np.where(btc_data['EMA_5'][5:] > btc_data['EMA_21'][5:], 1, 0)
btc_data['Position'] = btc_data['Signal'].diff()

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(btc_data['Close'], label='BTC Price', color='black', alpha=0.3)

# Plot EMAs
plt.plot(btc_data['EMA_5'], label='EMA 5', color='cyan')
plt.plot(btc_data['EMA_21'], label='EMA 21', color='magenta')

# Plot Buy signals
plt.plot(btc_data[btc_data['Position'] == 1].index, 
         btc_data['EMA_5'][btc_data['Position'] == 1], 
         '^', markersize=10, color='g', lw=0, label='Buy Signal')

# Plot Sell signals
plt.plot(btc_data[btc_data['Position'] == -1].index, 
         btc_data['EMA_5'][btc_data['Position'] == -1], 
         'v', markersize=10, color='r', lw=0, label='Sell Signal')

plt.title('BTC Price, EMA Ribbon, Buy & Sell Signals')
plt.legend(loc='upper left')
plt.show()
