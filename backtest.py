from strategy import Strategy
from api_conn import APIConn
from summary import Summary


conn = APIConn("poloniex", False, False)
strat = Strategy()

test_start = 1512086400  # Unix date -- December 1st '17
test_end = 1512691200  # Unix date -- December 8th '17

data = strat.get_data(test_start, test_end)

strat.initialize(start=test_start)

for time in data.index:
	trades = strat.tick(data.loc[time])
	
	for trade_key in trades.keys():
		conn.execute_trade(trades[trade_key])

#  Summary(conn.trades).print()


