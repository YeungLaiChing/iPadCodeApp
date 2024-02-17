import pandas as pd

# Create a sample dataframe (replace with your actual data)
data = {
    'price': [180000, 384000, 342000, 1154000, 421300, 1210000, 1062500, 1878000, 876000, 925000],
    'quantity': [34.2, 37.8, 39.715, 44.375, 44.375, 45.295, 45.295, 46.653, 46.653, 53.476]
}

df = pd.DataFrame(data)

# Sort by price in ascending order
df.sort_values(by='price', inplace=True)

# Calculate cumulative weights
cumulative_weights = df['quantity'].cumsum()

# Find the 50th percentile weight (P)
total_weight = df['quantity'].sum()
P = total_weight * 0.5

# Locate the index where cumulative weight exceeds P
index = cumulative_weights[cumulative_weights >= P].index[0]

# Get the weighted median price
weighted_median = df.loc[index, 'price']

print(f"Weighted Median Price: ${weighted_median:.2f}")
