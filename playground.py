import jsonpickle
import numpy as np 
from collections import defaultdict
from typing import List

def linear_regression(x, y):
    try:
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        return m, c
    except np.linalg.LinAlgError:
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
    
    
if __name__ == "__main__":
    data = TraderData()
    data.add_point("BTCUSD", 10000)
    data.add_point("BTCUSD", 10001)
    data.add_point("BTCUSD", 10002)
    data.add_point("BTCUSD", 10003)
    data.add_point("BTCUSD", 10004)
    td = str(data)
    data = TraderData(td)
    print(data.regression_model)
    print(data.slope("BTCUSD"))
    