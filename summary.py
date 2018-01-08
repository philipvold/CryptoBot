class Summary(object):
	def __init__(self, trades):
		self.num_trades = len(trades)
		
	def print(self):
		print(self.num_trades)
