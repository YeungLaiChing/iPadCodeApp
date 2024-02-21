import matplotlib.pyplot as plt
import yfinance as yf

data = yf.download("0005.HK", start="2020-01-01", end="2021-01-01")
data['Close'].plot()
plt.title("HSBC Stock Prices")
plt.show()
data = yf.download("0005.HK", start="2020-01-01", end="2021-01-01", auto_adjust=True)
print(data['Close'])  # This will show the adjusted close prices
