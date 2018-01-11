# from indicators import Indicators
from api_conn import APIConn
import time
import pandas as pd
import calendar


class Strategy(object):
	def __init__(self):
		self.trades = {}
		self.new_trades = {}
		self.num_trades = 0
		self.conn = APIConn("poloniex", live=False, read_only=True)  # Strategy independent
		self.tx_fee = 0.9975  # poloniex specific transaction fee
		
		#  Strategy parameters
		self.sleep = 5
		self.trade_size = 0.01  # Trade size ETH ~~ 10 USD as of jan '18
		self.spread_mult = 0.2  # Pct in decimal
		self.n_open_trades = 0
		self.freq = 300
		self.pairs = ["BTC_ETH", "ETH_ETC", "BTC_ETC"]
		self.directions = ["buy", "buy", "sell"]
		self.bid_ask = self.get_bid_ask_from_direction()
		self.price_target = 1.01

		self.initialize()
		
	def tick(self, new_prices=None):
		self.new_trades = {}
		prices = []
		
		if new_prices:
			for pairs in self.pairs:
				prices.append(new_prices.loc[pairs])
		else:
			for i in range(len(self.pairs)):
				prices.append(float(self.conn.get_price_data(self.pairs[i])[self.bid_ask[i]]))
				
		# *** STRATEGY GOES HERE *** #
		triangle_price = prices[0]*prices[1]*(1/prices[2])
		
		if triangle_price >= self.price_target:
			price_0 = prices[0] * (1 + self.spread_mult)
			amt_0 = self.trade_size
			
			price_1 = prices[1] * (1 + self.spread_mult)
			amt_1 = amt_0 / prices[1] * self.tx_fee
			
			price_2 = prices[2] * (1 - self.spread_mult)
			amt_2 = amt_1 * self.tx_fee
			
			self.add_trade(self.directions[0], self.pairs[0], price_0, amt_0)  # Buy 0.001 ETH ~~ 1 USD (from BTC)
			self.add_trade(self.directions[1], self.pairs[1], price_1, amt_1)  # Buy ~~ 1 USD worth of ETC (from BTC)
			self.add_trade(self.directions[2], self.pairs[2], price_2, amt_2)  # sell ~~ 1 USD worth of ETC (to BTC)
		
		print(time.ctime(), round(triangle_price, 6))
		return self.new_trades
	
	@staticmethod
	def initialize(start=0):
		init_time = 3600  # 1 hour -- STRATEGY SPECIFIC!!
		if not start:
			start = int(time.time())
	
	def add_trade(self, direction, pair, rate, amount):
		self.new_trades[self.num_trades] = (direction, pair, rate, amount)
		self.trades.update(self.new_trades)
		self.num_trades += 1

	def get_data(self, start, end):
		data = {}
		for pair in self.pairs:
			print("Importing %s data" % pair)
			data[pair] = self.conn.get_data(pair, start, end, self.freq)
			
		idx = data[self.pairs[0]].index
		result = pd.DataFrame(index=idx)
		
		for key in data.keys():
			result[key] = data[key]
		
		return result
	
	def get_bid_ask_from_direction(self):
		hilo = []
		for i in range(len(self.pairs)):
			if self.directions[i] == "buy":
				hilo.append("lowestAsk")
			elif self.directions[i] == "sell":
				hilo.append("highestBid")
			else:
				raise ValueError("WARNING: TYPO IN TRADE DIRECTIONS")
			
		return hilo
