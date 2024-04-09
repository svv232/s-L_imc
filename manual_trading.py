import numpy as np

min_price, max_price = 900, 1000
min_vol, max_vol = 1, 100
final_liquidation_price = 1000 # the island buys at 1000 at the end, always


print("manual trading started")

"""
Since distribution is linear, we want to calculate our maximum profit given two bids, the lower one going first.
"""


curr_vol = 1
offers = []
for price in range(min_price, max_price + 1):
  for i in range(curr_vol):
    offers.append(price)
  curr_vol += 1

print(len(offers))

profits = []
for low_bid in range(min_price, max_price):
  for high_bid in range(low_bid + 1, max_price + 1):
    profit = 0
    low_bid_prof = final_liquidation_price - low_bid
    high_bid_prof = final_liquidation_price - high_bid

    for offer in offers:
      if offer <= low_bid:
        profit += low_bid_prof
      elif offer <= high_bid:
        profit += high_bid_prof
    print(f"Low bid: {low_bid}, High bid: {high_bid}, Profit: {profit}")
    profits.append((profit, (low_bid, high_bid)))
  
print(max(profits, key=lambda x: x[0]))