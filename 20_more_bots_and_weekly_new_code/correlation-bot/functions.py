from pdb import Restart
import pandas as pd
from datetime import datetime, time
from pytz import timezone
import pandas_ta as ta
from time import sleep
import numpy as np 



def get_candle_df(coinbase,symbol,timeframe,limit=20):
    '''
    returns a pandas dataframe of the last n candles (n is limit variable)
    
    '''
    ohlcv = pd.DataFrame(coinbase.get_product_historic_rates(symbol,granularity=timeframe),columns=['time','low','high','open','close','volume']).set_index('time')
    return ohlcv.tail(limit)





def calc_tr(df):
    '''
    calculate and add the sma to the input dataframe. Returns the most recent sma
    '''

    #use pandas_ta to calculate the true range
    df['True_Range'] = df.ta.atr()

    return df['True_Range'].iloc[-1]




def calc_sup_res(df,length=20):
    '''
    calculate and add the support/resistance levels to the input dataframe
    '''
    df['support'] = df['low'].rolling(window=length).min()
    df['resistance'] = df['high'].rolling(window=length).max()


    return df['support'].iloc[-1], df['resistance'].iloc[-1]




def get_position(phemex,symbol):
    '''
    get the info of your position for the given symbol.
    '''
    params = {'type':'swap', 'code':'USD'}
    phe_bal = phemex.fetch_balance(params=params)
    #get your position for the provided symbol
    position_info = [pos for pos in phe_bal['info']['data']['positions'] if pos['symbol'] == symbol][0]

    #if there is a position (side is none when no current position)
    if position_info['side'] != 'None':
        in_position = True
        long = True if position_info['side'] == 'Buy' else False

    #if not in position currently
    else:
        in_position = False
        long = None 

    return position_info, in_position, long





def close_position(phemex,symbol):
    '''
    close your position for the given symbol
    '''

    #close all pending orders
    phemex.cancel_all_orders(symbol)

    #get your current position information (position is a dict of position information)
    position,in_position,long = get_position(phemex,symbol)
    

    #keep trying to close position every 30 seconds until sucessfully closed
    while in_position:

        #if position is a long create an equal size short to close. 
            #use reduceOnly to make sure you dont create a trade in the opposite direction
            #sleep for 30 seconds to give order a chance to fill
        if long:
            bid = phemex.fetch_ticker(symbol)['bid'] #get current bid price
            order = phemex.create_limit_sell_order(symbol, position['size'], bid, {'reduceOnly':True})
            print(f'just made a BUY to CLOSE order of {position["size"]} {symbol} at ${bid}')
            sleep(30)

        #if position is a short create an equal size long to close. 
            #use reduceOnly to make sure you dont create a trade in the opposite direction
            #sleep for 30 seconds to give order a chance to fill
        else:
            ask = phemex.fetch_ticker(symbol)['ask'] #get current ask price
            order = phemex.create_limit_buy_order(symbol, position['size'], ask, {'reduceOnly':True})
            print(f'just made a SELL to CLOSE order of {position["size"]} {symbol} at ${ask}')
            sleep(30)

        position,in_position,long = get_position(phemex,symbol)


    #cancel all outstanding orders
    phemex.cancel_all_orders(symbol)

    #sleep for a minute to avoid running twice
    sleep(60)


