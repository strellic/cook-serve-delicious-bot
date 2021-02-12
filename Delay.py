import time

class Delay:
	active = []
	
	def __init__(self, delay):
		self.inital = time.time()
		self.target = time.time() + delay
		self.freezetime = 0

		Delay.active.append(self)
		Delay.update()

	def target(self): # target time
		Delay.update()
		return self.target + self.freezetime

	def time_until(self): # time until target time
		Delay.update()
		return (self.target + self.freezetime) - time.time()

	def time_since(self): # time since target time has finished
		Delay.update()
		return time.time() - (self.target + self.freezetime)

	def time_elapsed(self): # time since delay has been created
		Delay.update()
		return time.time() - self.initial

	def is_ready(self): # has target time been reached
		Delay.update()
		return self.time_until() <= 0

	@staticmethod
	def add_freezetime(delay):
		if not Delay.active:
			return

		print(f"[!] Adding delay {delay} to {len(Delay.active)} delays!")
		for a in Delay.active:
			a.freezetime += delay
		
		Delay.update()

	@staticmethod
	def update():
		for d in Delay.active:
			if (d.target + d.freezetime) - time.time() < -10:
				Delay.active.remove(d)