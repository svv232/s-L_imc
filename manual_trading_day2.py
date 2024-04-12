from collections import defaultdict

available_sea_shells = 2000

rates_table = [
    [1, .48, 1.52, 0.71],
    [2.05, 1, 3.26, 1.56],
    [0.64, .3, 1, .46],
    [1.41, 0.61, 2.08, 1]
]

currencies = [
    "pizza_slice",
    "wasabi_root",
    "snowball",
    "shells"
]

start_currency = "shells"
goal_currency = "shells"

graph = defaultdict(dict)
paths = []
best_path = ([],0)

def generate_graph():
    for i in range(len(rates_table)):
        currency = currencies[i]
        for r in range(len(rates_table[i])):
            adjacent_currency = currencies[r]
            rate = rates_table[i][r]
            if rate != 1 and adjacent_currency != currency:
                graph[currency][adjacent_currency] = rate
            
def find_optimal_trade_path(graph, currency=start_currency, path = None, cumm_rate = None, seen = None):
    global best_path
    
    if path is None:
        path = []
        cumm_rate = 1
        seen = set()
        
    for c in graph[currency]:
        if c == goal_currency:
            path.append(c)
            final_rate = cumm_rate * graph[currency][c]
            paths.append((path, final_rate))
            if final_rate > best_path[1]:
                best_path = (path, final_rate)
            
        else:
            rate = graph[currency][c]
            # this works because all rates are unique, in reality we want to track edges
            if rate not in seen:
                new_seen = seen.copy()
                new_seen.add(rate)
                find_optimal_trade_path(graph, c, path + [c], cumm_rate * rate, new_seen)
            
if __name__ == "__main__":
    generate_graph()
    for k,v in graph.items():
        print(k,v)
        
    find_optimal_trade_path(graph)
    for p in paths:
        print(p)
    
    print(best_path)