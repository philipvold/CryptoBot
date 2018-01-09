from strategy import Strategy
from api_conn import APIConn
from summary import Summary


conn = APIConn("poloniex", True, False)
strat = Strategy()

test_start = 1512086400  # Unix date -- December 1st '17
test_end = 1512691200  # Unix date -- December 8th '17

prices = strat.get_data(test_start, test_end)

strat.initialize(start=test_start)

for price in prices:
	trades = strat.tick(price)
	
	for trade_key in trades.keys():
		with trades[trade_key] as trade:
				conn.execute_trade(trade)

#  Summary(conn.trades).print()
print("Hello Git 2")

