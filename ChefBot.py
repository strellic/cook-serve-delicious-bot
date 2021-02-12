import keyboard
import time

class ChefBot:
	def __init__(self):
		pass

	def keypress(self, key, downTime = 0.05, callback = lambda: None):
		print(f"[!] Pressing: {key}")
		keyboard.press(key)
		time.sleep(downTime)
		keyboard.release(key)

		callback()

	def emulate(self, recipe, callback = lambda: None):
		sleepTime = 0.05
		sleepAfter = 0.1

		if "sleep" in recipe:
			sleepTime = recipe["sleep"]

		if "sleepAfter" in recipe:
			sleepAfter = recipe["sleepAfter"]

		keys = recipe["keys"]
		for item in keys:
			if isinstance(item, str):
				self.keypress(item)
			else:
				self.keypress(item["key"], item["downTime"])

			time.sleep(sleepTime)

		time.sleep(sleepAfter)

		callback()