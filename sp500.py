# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 16:04:44 2021

@author: ZhangQi
"""
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import altair as alt
import os

#path = os.path.dirname(__file__)
#my_file = path+"\\Datasets\\SP500.csv"

#snp500 = pd.read_csv(my_file)
#symbols = snp500['Symbol'].sort_values().tolist()


symbols = ["NET","AAPL","MMM","A"]
ticker = st.sidebar.selectbox(
    'Choose a S&P 500 Stock',
     symbols)     

stock = yf.Ticker(ticker)
info = stock.info



st.title(info['longName'])
st.image(info['logo_url'])
#subheader() 
st.markdown('** Sector **: ' + info['sector'])
st.markdown('** Industry **: ' + info['industry'])
st.markdown('** Phone **: ' + info['phone'])
st.markdown('** Address **: ' + info['address1'] + ', ' + info['city'] + ', ' + info['zip'] + ', '  +  info['country'])
st.markdown('** Website **: ' + info['website'])
st.markdown('** Business Summary **')


text = info['longBusinessSummary']
#result = translator.translate(text,lang_src="en", lang_tgt="zh")
st.info(text)

# Set the timeframe you are interested in viewing.
stock_historical = stock.history(start="2018-01-2", end="2020-12-11", interval="1d")
# Create a new DataFrame called signals, keeping only the 'Date' & 'Close' columns.
signals_df = stock_historical.drop(columns=['Open', 'High', 'Low', 'Volume','Dividends', 'Stock Splits'])
# Set the short window and long windows
short_window = 50
long_window = 100
# Generate the short and long moving averages (50 and 100 days, respectively)
signals_df['SMA50'] = signals_df['Close'].rolling(window=short_window).mean()
signals_df['SMA100'] = signals_df['Close'].rolling(window=long_window).mean()
signals_df['Signal'] = 0.0
# Generate the trading signal 0 or 1,
# where 0 is when the SMA50 is under the SMA100, and
# where 1 is when the SMA50 is higher (or crosses over) the SMA100
signals_df['Signal'][short_window:] = np.where(
    signals_df['SMA50'][short_window:] > signals_df['SMA100'][short_window:], 1.0, 0.0
)
# Calculate the points in time at which a position should be taken, 1 or -1
signals_df['Entry_Exit'] = signals_df['Signal'].diff()
# Print the DataFrame
signals_df =signals_df.reset_index()


close = alt.Chart(signals_df).mark_line(color="lightgray").encode(
    x="Date:T",
    y="Close:Q",

)

moving_avgs = alt.Chart(signals_df).mark_line().transform_fold(
    fold=["SMA50","SMA100"],
    as_ =["average","y"]
).encode(
    x="Date:T",
    y="y:Q",
    color="average:N"
)

exit_ = alt.Chart(signals_df).mark_circle(color="red",).encode(
    x="Date:T",
    y="Close:Q",
    opacity= alt.condition(
        alt.datum.Entry_Exit == -1, 
        alt.value(1.0),
        alt.value(0.0))
)
    
entry_ = alt.Chart(signals_df).mark_circle(color="green").encode(
    x="Date:T",
    y="Close:Q",
    opacity= alt.condition(
        alt.datum.Entry_Exit == 1, 
        alt.value(1.0),
        alt.value(0.0))
) 

plot_1 = close+entry_ + exit_+moving_avgs

plot_1.properties(width=1000,height=400)

st.markdown('Find Buy and Sell Signal: Green to buy, Red to sell' )
st.altair_chart(plot_1, use_container_width=True)



# Set initial capital
initial_capital = float(100000)
# Set the share size
share_size = 500
# Take a 500 share position where the dual moving average crossover is 1 (SMA50 is greater than SMA100)
signals_df['Position'] = share_size * signals_df['Signal']
# Find the points in time where a 500 share position is bought or sold
signals_df['Entry/Exit Position'] = signals_df['Position'].diff()
# Multiply share price by entry/exit positions and get the cumulatively sum
signals_df['Portfolio Holdings'] = signals_df['Close'] * signals_df['Entry/Exit Position'].cumsum()
# Subtract the initial capital by the portfolio holdings to get the amount of liquid cash in the portfolio
signals_df['Portfolio Cash'] = initial_capital - (signals_df['Close'] * signals_df['Entry/Exit Position']).cumsum()
# Get the total portfolio value by adding the cash amount by the portfolio holdings (or investments)
signals_df['Portfolio Total'] = signals_df['Portfolio Cash'] + signals_df['Portfolio Holdings']
# Calculate the portfolio daily returns
signals_df['Portfolio Daily Returns'] = signals_df['Portfolio Total'].pct_change()
# Calculate the cumulative returns
signals_df['Portfolio Cumulative Returns'] = (1 + signals_df['Portfolio Daily Returns']).cumprod() - 1
# Print the DataFrame
signals_df.tail(10)


total_portfolio_value = alt.Chart(signals_df).mark_line(color="lightgray").encode(
    x="Date:T",
    y="Portfolio Total:Q",

)

exit_2 = alt.Chart(signals_df).mark_circle(color="red",).encode(
    x="Date:T",
    y="Portfolio Total:Q",
    opacity= alt.condition(
        alt.datum.Entry_Exit == -1, 
        alt.value(1.0),
        alt.value(0.0))
)
    
entry_2 = alt.Chart(signals_df).mark_circle(color="green").encode(
    x="Date:T",
    y="Portfolio Total:Q",
    opacity= alt.condition(
        alt.datum.Entry_Exit == 1, 
        alt.value(1.0),
        alt.value(0.0))
) 

plot_2 = total_portfolio_value + entry_2 + exit_2

plot_2.properties(width=1000,height=400)
st.markdown('Your Strategy performance' )
st.altair_chart(plot_2, use_container_width=True)
