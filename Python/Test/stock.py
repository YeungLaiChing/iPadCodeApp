import yfinance as yf

data = yf.download("0005.HK", start="2020-01-01", end="2021-01-01")
print(data.head())


hsbc = yf.Ticker("0005.HK")
print(hsbc.info)  # General information about Apple Inc.

print(hsbc.info['currentPrice'])  # General information about Apple Inc.

apple = yf.Ticker("0005.HK")
print(apple.history(period="1d"))
