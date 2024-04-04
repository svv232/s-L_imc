from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
from collections import defaultdict

import numpy as np
import jsonpickle
    
def linear_regression(x, y):
    try:
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
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
        _, slope = linear_regression(x_axis, y_axis)
        return slope
    
class Trader:
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = wap(order_depth)
            trader_data = TraderData(state.traderData)
            trader_data.add_point(product, acceptable_price)
            slope = trader_data.slope(product)
            
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            
            
            buy_acceptable_price = acceptable_price + (.5 * slope)
            
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < buy_acceptable_price:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
                    
            
            sell_acceptable_price = acceptable_price - (.5 * slope)
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > sell_acceptable_price:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
            
            result[product] = orders
            state.traderData = str(trader_data)
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        conversions = 0
        return result, conversions, state.traderData

# class OrderDepth:
#     def __init__(self):
#         self.buy_orders: Dict[int, int] = {}
#         self.sell_orders: Dict[int, int] = {}

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