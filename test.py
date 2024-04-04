from trading import Trader
from datamodel import OrderDepth, TradingState
import json, sys

def main():
  trader = Trader()
  traderData = ""
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
        data["position"],
        data["observations"],
      )

      results, c, traderData = trader.run(state)
      print("results", results)

      sys.stdin.readline()


if __name__ == "__main__":
  main()
