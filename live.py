from strategy import Strategy
from api_conn import APIConn
import time
from summary import Summary

conn = APIConn("poloniex", True, False)
strat = Strategy()

runtime = 300  # iterations

while runtime:
	trades = strat.tick()
	for trade_key in trades.keys():
		conn.execute_trade(trades[trade_key])
	
	
	time.sleep(strat.sleep)
	runtime -= 1
	
#  Summary(conn.trades).print()
