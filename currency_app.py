import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Page setup
st.set_page_config(page_title="World Currency Exchange", layout="centered")
st.title("World Currency Exchange")
st.markdown("Real-time currency conversion and historical exchange rate analysis")

API_KEY = st.secrets["CURRENCY_API_KEY"]

# Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Exchange Rates")
    currency = st.text_input("Currency Code", "EUR", help="Enter 3-letter code like EUR, JPY, GBP").upper()
    days = st.selectbox("Time Range", [5, 10, 20, 30], index=0)
    
    if st.button("Get Current Rate", type="primary"):
        # Current rate API call
        url = 'https://api.currencylayer.com/live'
        params = {'access_key': API_KEY, 'currencies': currency, 'source': 'USD'}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('success', False):
                rate = data['quotes'][f'USD{currency}']
                st.success(f"**Current USD to {currency} rate:** {rate:.4f}")
            else:
                st.error("Failed to get current rate. Check API key.")
        except:
            st.error("Network error. Please try again.")

with col2:
    st.subheader("💵 Amount Conversion")
    amount = st.number_input("USD Amount", min_value=0.0, value=100.0, step=10.0)
    target_currency = st.selectbox("Convert to", ["EUR", "JPY", "GBP", "CAD", "AUD", "CNY", "RUB"])
    
    if st.button("Convert Amount", type="primary"):
        # Conversion API call
        url = 'https://api.currencylayer.com/live'
        params = {'access_key': API_KEY, 'currencies': target_currency, 'source': 'USD'}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('success', False):
                rate = data['quotes'][f'USD{target_currency}']
                converted = amount * rate
                st.success(f"**${amount:.2f} USD = {converted:.2f} {target_currency}**")
                st.info(f"Exchange rate: 1 USD = {rate:.4f} {target_currency}")
            else:
                st.error("Conversion failed. Check API key.")
        except:
            st.error("Network error. Please try again.")

# Historical data section
st.subheader("📈 Historical Data")
if st.button("Generate Historical Chart", type="primary"):
    with st.spinner("Loading historical data..."):
        dates, rates = [], []
        
        for i in range(days, 0, -1):
            date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            url = 'https://api.currencylayer.com/historical'
            params = {'access_key': API_KEY, 'date': date_str, 'currencies': currency, 'source': 'USD'}
            
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get('success', False):
                    rate = data['quotes'][f'USD{currency}']
                    rates.append(rate)
                    dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            except:
                continue
        
        if len(dates) > 0:
            # Create and display plot
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(dates, rates, marker='o', linestyle='-', linewidth=2, markersize=4)
            ax.set_title(f"USD to {currency} Exchange Rate ({days} Days)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Exchange Rate")
            ax.grid(True, linestyle='--', alpha=0.7)
            
            date_format = plt.matplotlib.dates.DateFormatter('%m-%d')
            ax.xaxis.set_major_formatter(date_format)
            fig.autofmt_xdate()
            
            st.pyplot(fig)
            
            # Show data summary
            df = pd.DataFrame({'Date': dates, 'Rate': rates})
            st.write("**Data Summary:**")
            st.write(f"Period: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
            st.write(f"Average rate: {df['Rate'].mean():.4f}")
            st.write(f"Minimum rate: {df['Rate'].min():.4f}")
            st.write(f"Maximum rate: {df['Rate'].max():.4f}")
        else:
            st.error("No historical data available. Check API key or try again.")

# Footer
st.markdown("---")
st.caption("Data from CurrencyLayer")
