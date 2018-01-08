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
		
		#  Strategy parameters
		self.max_trades = 1
		self.sleep = 1
		self.n_open_trades = 0
		self.freq = 300
		self.pairs = ["ETH_BTC", "ETC_ETH", "ETC_BTC"]

		self.initialize()
		
	def tick(self, new_prices):
		self.new_trades = {}
		
		# *** STRATEGY GOES HERE *** #
		
		return self.new_trades
	
	@staticmethod
	def initialize(start=0):
		init_time = 3600  # 1 hour
		if not start:
			start = int(time.time())
	
	def add_trade(self, direction, pair, rate, amount):
		self.new_trades[self.num_trades] = (direction, pair, rate, amount)
		self.trades.update(self.new_trades)
		self.num_trades += 1

	def get_data(self, start, end):
		data = {}
		for pair in self.pairs:
			data[pair] = self.conn.get_data(pair, start, end, self.freq)
		return data
	