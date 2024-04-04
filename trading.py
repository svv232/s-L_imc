from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
from collections import defaultdict

import numpy as np
import jsonpickle
    
def linear_regression(x, y):
    try:
        xs = np.vstack([np.ones(len(x)), x]).T
        m, c = np.linalg.lstsq(xs, np.array(y), rcond=None)[0]
        return m, c
    except:
        raise  np.linalg.LinAlgError(f'{x.shape}, {y.shape} something went wrong with the shape')

class TraderData:
    def __init__(self, data : str = ""):
        if data == "":
            self.regression_model = defaultdict(list)
            self.tick_delta = 100
        else:
            data = jsonpickle.decode(data)
            self.regression_model = data.regression_model
            self.tick_delta = data.tick_delta
        
    def __str__(self):
        return jsonpickle.encode(self)
    
    def add_point(self,product : str,  y : float):
        self.regression_model[product].append(y)
        
    def slope(self, product : str):
        x_axis = np.array([x * self.tick_delta for x in range(len(self.regression_model[product]))])
        y_axis = np.array(self.regression_model[product])   

        # print("X axis: ", x_axis)
        # print("Y axis: ", y_axis)
        _, slope = linear_regression(x_axis, y_axis)
        return slope
    
class Trader:
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        
        result = {}
        for product in state.order_depths:
            print("\n")
            print("######### Product: " + product + " #########")
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = wap(order_depth)
            trader_data = TraderData(state.traderData)
            trader_data.add_point(product, acceptable_price)
            slope = trader_data.slope(product)
            
            print("Acceptable price : " + str(acceptable_price))
            
            orders = order_volume_optimizer(acceptable_price, order_depth, slope, state.position.get(product, 0))
            
            result[product] = orders
            state.traderData = str(trader_data)
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        conversions = 0
        return result, conversions, state.traderData

def wap(o: OrderDepth):
    total = 0
    volume = 0
    for price, amount in o.buy_orders.items():
        total += price * amount
        volume += amount
    for price, neg_amount in o.sell_orders.items():
        amount = neg_amount * -1
        total += price * amount
        volume += amount
    return total / volume if volume != 0 else 0
  

buy_position_limit = 20
sell_position_limit = -20
# We need to make sure we stay within our position limits while maximizing the # amount of volume we can trade.
# This means balancing the orders we submit to the exchange.
def order_volume_optimizer(
  acceptable_price: float,
  order_depth: OrderDepth,
  slope: float,
  position: int,
):
  orders = []
  buy_acceptable_price = acceptable_price + (.5 * slope)
  sell_acceptable_price = acceptable_price - (.5 * slope)
  acceptable_asks = sorted([(price, amount) for price, amount in order_depth.sell_orders.items() if price < buy_acceptable_price], key=lambda x: x[0])
  acceptable_bids = sorted([(price, amount) for price, amount in order_depth.buy_orders.items() if price > sell_acceptable_price], key=lambda x: x[0], reverse=True)
  
  print("Slope: ", slope)
  print("Buy acceptable price: ", buy_acceptable_price)
  print("Asks: ", order_depth.sell_orders)
  print("Acceptable asks: ", acceptable_asks)
  print("Sell acceptable price: ", sell_acceptable_price)
  print("Bids: ", order_depth.buy_orders)
  print("Acceptable bids: ", acceptable_bids)

  return []