from trading import Trader
from datamodel import OrderDepth, TradingState
import json, sys
import pandas as pd
import matplotlib.pyplot as plt

def main():
  trader = Trader()
  traderData = ""
  position = {}
  currentSeashells = 0
  dps = []
  with open("./tradingData.json", 'r') as f:
    for line in f:
      data = json.loads(line)

      order_depths = {}
      for product in data["order_depths"]:
        order_depth = OrderDepth()
        order_depth.buy_orders = {}
        for price, amount in data["order_depths"][product]["buy_orders"].items():
          order_depth.buy_orders[int(price)] = amount
        
        order_depth.sell_orders = {}
        for price, amount in data["order_depths"][product]["sell_orders"].items():
          order_depth.sell_orders[int(price)] = amount
        order_depths[product] = order_depth

      state = TradingState(
        traderData,
        data["timestamp"],
        data["listings"],
        order_depths,
        data["own_trades"],
        data["market_trades"],
        position,
        data["observations"],
      )

      results, c, traderData = trader.run(state)
      # print("results", results)

      n_orders = 0
      for product in results:
        for order in results[product]:
          n_orders += 1
          if product not in position:
            position[product] = 0
          position[product] += order.quantity
          currentSeashells -= order.quantity * order.price
        
        if position.get(product, 0) > 20:
          print("Position limit exceeded for product: ", product)
          exit(1)
        elif position.get(product, 0) < -20:
          print("Position limit exceeded for product: ", product)
          exit(1)


      print("Current seashells: ", currentSeashells)
      dps.append(currentSeashells)
      if n_orders > 0:
        sys.stdin.readline()
        pass

  print("Final seashells: ", currentSeashells)
  s = pd.Series(dps)
  s.plot.line()
  plt.show()

  


if __name__ == "__main__":
  main()
