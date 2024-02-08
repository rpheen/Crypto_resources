import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Fetch historical INTC data with 5-minute intervals
# Note: 5-minute interval data might only be available for the last 60 days
# Adjust the start and end dates accordingly
start_date = '2024-01-05'
end_date = '2024-01-08'  # Example for a short period; adjust as needed
intc_data = yf.download('INTC', start=start_date, end=end_date, interval='5m')

# Calculate EMAs for the ribbon
intc_data['EMA_5'] = intc_data['Close'].ewm(span=5, adjust=False).mean()
intc_data['EMA_21'] = intc_data['Close'].ewm(span=21, adjust=False).mean()

# Determine Buy and Sell signals
intc_data['Signal'] = 0
intc_data['Signal'][5:] = np.where(intc_data['EMA_5'][5:] > intc_data['EMA_21'][5:], 1, 0)
intc_data['Position'] = intc_data['Signal'].diff()

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(intc_data['Close'], label='INTC Price', color='black', alpha=0.3)

# Plot EMAs
plt.plot(intc_data['EMA_5'], label='EMA 5', color='cyan')
plt.plot(intc_data['EMA_21'], label='EMA 21', color='magenta')

# Plot Buy signals
plt.plot(intc_data[intc_data['Position'] == 1].index, 
         intc_data['EMA_5'][intc_data['Position'] == 1], 
         '^', markersize=10, color='g', lw=0, label='Buy Signal')

# Plot Sell signals
plt.plot(intc_data[intc_data['Position'] == -1].index, 
         intc_data['EMA_5'][intc_data['Position'] == -1], 
         'v', markersize=10, color='r', lw=0, label='Sell Signal')

plt.title('INTC Price, EMA Ribbon, Buy & Sell Signals')
plt.legend(loc='upper left')
plt.show()
