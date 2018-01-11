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
		self.sleep = 2
		self.trade_size = 0.001  # Trade size ETH ~~ 10 USD as of jan '18
		self.spread_mult = 0.2  # Pct in decimal
		self.n_open_trades = 0
		self.freq = 300
		self.pairs = ["USDT_BTC", "USDT_BCH", "BTC_BCH"]
		self.directions = self.get_directions(self.pairs)
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
		triangle = self.arbitrage_indicator(prices)
		if triangle >= self.price_target:
			multipliers = self.get_trade_mult()
			trade_prices = []
			
			for i in range(len(self.pairs)):
				trade_prices.append(prices[i]*multipliers[i])
			
			trade_amounts = self.get_trade_amnt(prices)
			
			for i in range(len(self.directions)):
				self.add_trade(self.directions[i], self.pairs[i], trade_prices[i], trade_amounts[i])
		
		print(time.ctime(), round(triangle, 5))
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
	
	@staticmethod
	def get_base_currency(pairs):
		if "BTC" in pairs[0]:
			base_curr = "BTC"
		elif "USDT" in pairs[0]:
			base_curr = "USDT"
		elif "ETH" in pairs[0]:
			base_curr = "ETH"
		else:
			raise ValueError("WARNING: CANNOT IDENTIFY BASE CURRENCY")
		return base_curr
	
	def get_directions(self, pairs):
		base = self.get_base_currency(pairs)
		directions = []
		
		for pair in pairs:
			pair_lst = pair.split("_")
			if pair_lst[0] == base:
				directions.append("buy")
				base = pair_lst[1]
			else:
				directions.append("sell")
				base = pair_lst[0]
				
		return directions
	
	def get_trade_mult(self):
		pp = []
		
		for d in self.directions:
			if d == "buy":
				pp.append(1 + self.spread_mult)
			else:
				pp.append(1 - self.spread_mult)
		return pp
	
	def get_trade_amnt(self, new_prices):
		base = self.get_base_currency(self.pairs)
		amounts = []
		
		if base == "BTC":
			trade_size = 0.0005  # BTC
		elif base == "USDT":
			trade_size = 10  # USDT
		else:
			trade_size = 0.01  # ETH
			
		for i in range(len(self.directions)):
			if self.directions[i] == "buy":
				trade_size = trade_size/new_prices[i]*self.tx_fee
				amounts.append(trade_size)
			else:
				trade_size *= self.tx_fee
				amounts.append(trade_size)
		
		return amounts
	
	def arbitrage_indicator(self, prices):
		arbi = 1.0
		for i in range(len(self.directions)):
			if self.directions[i] == "buy":
				arbi /= prices[i]
			else:
				arbi *= prices[i]
		return arbi
		