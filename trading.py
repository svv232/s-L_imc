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
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))
        
        result = {}
        for product in state.order_depths:
            print("######### Product: " + product + " #########")
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = wap(order_depth)
            trader_data = TraderData(state.traderData)
            trader_data.add_point(product, acceptable_price)
            slope = trader_data.slope(product)
            position = state.position.get(product, 0)
            print("Acceptable price : " + str(acceptable_price))
            
            orders = order_volume_optimizer(product, acceptable_price, order_depth, slope, position)
            
            expected_position = position
            for order in orders:
                expected_position -= order.quantity
            print("Expected position: ", expected_position)
            result[product] = orders
            state.traderData = str(trader_data)
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        conversions = 0
        print(result)
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
  product,
  acceptable_price: float,
  order_depth: OrderDepth,
  slope: float,
  position: int,
):
  orders = []
  buy_acceptable_price = acceptable_price + (.5 * slope)
  sell_acceptable_price = acceptable_price - (.5 * slope)
  # we need to negate the amount of the sell orders to make them positive, 
  # because they're negative in the order depth
  # this is just because they're easier to work with as positive numbers
  acceptable_asks = sorted([(price, -1 * amount) for price, amount in order_depth.sell_orders.items() if price < buy_acceptable_price], key=lambda x: x[0])
  acceptable_bids = sorted([(price, amount) for price, amount in order_depth.buy_orders.items() if price > sell_acceptable_price], key=lambda x: x[0], reverse=True)
  
  print("Slope: ", slope)
  print("Buy acceptable price: ", buy_acceptable_price)
  print("Asks: ", order_depth.sell_orders)
  print("Acceptable asks: ", acceptable_asks)
  print("Sell acceptable price: ", sell_acceptable_price)
  print("Bids: ", order_depth.buy_orders)
  print("Acceptable bids: ", acceptable_bids)

  ask_order_capacity = sum([amount for _, amount in acceptable_asks])
  bid_order_capacity = sum([amount for _, amount in acceptable_bids])
  
  order_diff = ask_order_capacity - bid_order_capacity
  n_ask = 0
  n_bid = 0
  if order_diff > 0:
    n_ask = ask_order_capacity - order_diff
    n_bid = bid_order_capacity
  else:
    n_ask = ask_order_capacity
    n_bid = bid_order_capacity + order_diff

  potential_position = position + order_diff


  print("Potential position delta: ", potential_position)

  n_ask_orders_to_place = n_ask
  n_bid_orders_to_place = n_bid

  print("Position: ", position)
  print("Number of ask orders to place: ", n_ask_orders_to_place)
  print("Number of bid orders to place: ", n_bid_orders_to_place)
  for price, amount in acceptable_asks:
    if n_ask_orders_to_place == 0:
      break
    if amount > n_ask_orders_to_place:
      orders.append(Order(product, price, -1 * n_ask_orders_to_place))
      n_ask_orders_to_place = 0
    else:
      orders.append(Order(product, price, amount))
      n_ask_orders_to_place -= amount

  for price, amount in acceptable_bids:
    if n_bid_orders_to_place == 0:
      break
    if amount > n_bid_orders_to_place:
      orders.append(Order(product, price, n_bid_orders_to_place))
      n_bid_orders_to_place = 0
    else:
      orders.append(Order(product, price, -amount))
      n_bid_orders_to_place -= amount

  return orders