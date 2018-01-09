from APIs.Poloniexlib import Poloniex
import pickle

class APIConn(object):
	def __init__(self, exchange, live=False, read_only=True):
		
		self.live = live
		self.read_only = read_only
		self.trades = {}
		self.num_trades = 0
		
		if exchange == "poloniex":
			with open(r"poloniex.pickle", "rb") as key_file:
				keys = pickle.load(key_file)
			if self.read_only:
				_public = keys["reader_public"]
				_secret = keys["reader_secret"]
			else:
				_public = keys["trader_public"]
				_secret = keys["trader_secret"]
			self.conn = Poloniex(_public, _secret)

	def get_last_price(self, pair):
		current_values = self.conn.api_query("returnTicker")
		last_price = current_values[pair]["last"]  # This is specific for Poloniex -- Needs fix
		return last_price
	
	def execute_trade(self, trade):  # BUY amount of BASE/last at rate
		if self.read_only:
			raise ValueError("WARNING: THIS CONNECTION IS NOT SUPPOSED TO EXECUTE TRADES!")
		
		if self.live:
			direction = trade(0)
			pair = trade(1)
			rate = trade(2)
			amount = trade(3)
			
			# poloniex specific!
			return self.conn.api_query(direction, {"currencyPair": pair, "rate": rate, "amount": amount})
	
	def get_data(self, pair, start, end, frequency):
		""" Returns a list of prices """
		data = self.conn.api_query("returnChartData", {"currencyPair": pair, "start": start, "end": end, "period": frequency})
		return data
	
	def return_balance(self, ccy):
		out = self.conn.api_query("returnBalances")  # Poloniex specific -- Needs fix
		return float(out[ccy])
