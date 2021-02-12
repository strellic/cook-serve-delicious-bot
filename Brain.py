import threading
import itertools
import win32gui
import keyboard
import json
import time
import re

from ChefBot import ChefBot
from Delay import Delay

class Brain:
	def __init__(self):
		with open('recipes.json') as f:
			self.recipes = json.load(f)

		self.threads = []
		self.memory = []
		self.waiting = {}

		self.chef = ChefBot()

		self.lastUnknown = None
		self.lastFetch = None
		self.slot = -1

		keyboard.on_press(self.key_hook)

	def is_cooking(self):
		return len(self.threads) > 0

	def key_hook(self, e):
		if e.name and e.name.isnumeric():
			self.slot = int(e.name)

	def send_keypress(self, key, downTime = 0.05, callback = lambda: None):
		t = threading.Thread(target=self.chef.keypress, args=(key,downTime,callback), daemon=True)
		self.threads.append(t)
		t.start()

	def send_emulate(self, recipe, callback = lambda: None):
		t = threading.Thread(target=self.chef.emulate, args=(recipe,callback), daemon=True)
		self.threads.append(t)
		t.start()

	def fetch(self, food):
		key = food.lower().replace(" ", "_")

		recipe = None
		name = food

		if key in self.recipes:
			recipe = self.recipes[key]
		elif key[:-1] in self.recipes:
			recipe = self.recipes[key[:-1]]
			name = food[:-1]
		elif key[1:] in self.recipes:
			recipe = self.recipes[key[1:]]
			name = food[1:]
		else:
			subsets = []
			for l in range(0, len(food.split(" ")) + 1):
				for subset in itertools.permutations(food.split(" "), l):
					subsets.append(subset)

			for word in subsets[::-1]:
				key = '_'.join(word).lower()
				if key in self.recipes:
					recipe = self.recipes[key]
					name = ' '.join(word)
					break

		if recipe:
			print(f"[!] Recipe found for \"{food}\" -> \"{name}\" -> \"{key}\" -> {recipe['keys']}")
			self.lastFetch = name
			return recipe

		print(f"[!] No recipe found for \"{food}\"")
		self.lastUnknown = food.lower().replace(" ", "_")
		return None

	def save(self, keys):
		if self.lastUnknown:
			self.recipes[self.lastUnknown] = {
				"type": "standard",
				"keys": keys
			}

			with open('recipes.json', 'w') as outfile:
				json.dump(self.recipes, outfile)

	def robber(self, text):
		hairs = ["-select hair-", ["bald hair", "bald guy", "bald"], "sexy hair", "spiked hair", "poofy hair"] # H
		eyes = ["-select eyes-", "normal eyes", "crazy eyes", "sexy eyes", "beady eyes"] # Y
		ears = ["-select ears-", "normal ears", "round ears", "long ears", "tiny ears"] # E
		nose = ["-select nose-", "crooked nose", "normal nose", "fancy nose"] # N
		lips = ["-select lips-", "long lips", "small lips", "sexy lips"] # L
		facial_hair = ["-select facial hair-", "mustache", "beard", "fuzz", ["beard and mustache", "beard/mustache"]] # F

		text = text.replace("ting", "tiny")
		text = text.replace("lookin'", "")
		text = text.replace("lookin’", "")
		text = text.replace("  ", " ")

		COMBO1 = r'(\w+) (\w+)\/(\w+)'
		COMBO2 = r'(\w+) (\w+), (\w+) and (\w+)'
		if re.search(COMBO1, text):
			s = re.search(COMBO1, text)
			if s.group(2) != "beard":
				text = re.sub(COMBO1, f"{s.group(1)} {s.group(2)} and {s.group(1)} {s.group(3)}", text)
		if re.search(COMBO2, text):
			s = re.search(COMBO2, text)
			text = re.sub(COMBO2, f"{s.group(1)} {s.group(2)} and {s.group(1)} {s.group(3)} and {s.group(1)} {s.group(4)}", text)

		print(text)

		descriptions = [hairs, eyes, ears, nose, lips, facial_hair]
		choices = [-1] * len(descriptions)
		chars = ["h", "y", "e", "n", "l", "f"]

		for l in range(len(descriptions)):
			for i in range(len(descriptions[l])):
				if isinstance(descriptions[l][i], list) and any(ele in text for ele in descriptions[l][i]):
					choices[l] = i
				elif not isinstance(descriptions[l][i], list) and descriptions[l][i] in text:
					choices[l] = i

		keys = []
		for i in range(len(choices)):
			while choices[i] > 0:
				keys.append(chars[i])
				choices[i] -= 1
		keys.append("enter")

		self.send_emulate({"keys": keys, "sleepAfter": 1.5})

	def process(self, text):
		if self.is_cooking():
			return

		text = text.replace("iovers", "lovers") # manual fix for meatlovers pizza :(
		text = text.replace("ilovers", "lovers")

		recipe = self.fetch(text)
		if recipe:
			if recipe["type"] == "standard":
				self.send_emulate(recipe)
			elif recipe["type"] == "async" and self.slot != -1:
				def closure(slot):
					def cb():
						self.memory.append({	
							"type": "async",
							"delay": Delay(recipe["cookTime"]),
							"index": str(slot)
						})
					return cb
				self.send_emulate(recipe, closure(self.slot))
			elif recipe["type"] == "complex" and self.slot != -1:
				def closure(slot):
					def cb():
						self.memory.append({
							"type": "complex",
							"delay": Delay(recipe["cookTime"]),
							"recipe": recipe.copy(),
							"index": str(slot)
						})
					return cb
				self.send_emulate(recipe, closure(self.slot))
			else:
				print(f"[X] Recipe type {recipe['type']} not implemented yet...")

	def update(self, active):
		print(self.full_status())

		for i in range(len(active)):
			if active[i] and i in self.waiting:
				if self.waiting[i] == float('inf'):
					self.waiting[i] = time.time()
			else:
				self.waiting[i] = float('inf')

		not_cooking = {k: v for k, v in self.waiting.items() if k not in [int(m['index'])-1 for m in self.memory] and v != float('inf')}
		next_slot = None
		next_time = None
		if not_cooking:
			next_slot = min(not_cooking, key=not_cooking.get) + 1
			next_time = not_cooking[next_slot - 1]

		for mem in sorted(self.memory, key=lambda m: m["delay"].time_until()):
			if mem["delay"].is_ready():
				if mem["type"] == "async":
					print(f"[!] Finished async recipe on slot #{mem['index']}...")
					self.send_keypress(mem["index"])
					self.memory.remove(mem)
				elif mem["type"] == "complex":
					if not self.is_cooking() and (not next_time or (time.time() - next_time)/2 < mem["delay"].time_since()):
						def closure(mem):
							def cb():
								new_recipe = mem["recipe"]
								new_recipe["keys"] = new_recipe["keys2"]

								self.send_emulate(new_recipe)

								self.memory.remove(mem)
							return cb

						print(f"[!] Finishing complex recipe on slot #{mem['index']} -> {mem['recipe']['keys2']}")
						self.send_keypress(mem["index"], 0.1, closure(mem))
					else:
						print(f"[!] Waiting for better opportunity to finish complex recipe in slot #{mem['index']}...")
				else:
					print(f"[X] Memory type {mem['type']} not implemented yet...")

		if not self.is_cooking():
			if not_cooking:
				self.slot = next_slot
				self.send_keypress(str(self.slot), 0.1)

		for t in self.threads:
			if not t.is_alive():
				self.threads.remove(t)		

	def full_status(self):
		msg = "Status:\n"
		msg += f"\tCooking: {self.is_cooking()}\n"
		msg += f"\tActive Slot: {self.slot}\n"
		msg += f"\tMemory: {len(self.memory)}\n"
		for mem in sorted(self.memory, key = lambda v: v["index"]):
			msg += f"\t\tSlot #{mem['index']}: {mem['delay'].time_until()}s remaining... ({mem['type']})\n"
		msg += f"\tActive Threads: {len(self.threads)}\n"
		msg += f"\tPending Actions:\n"

		not_cooking = {k: v for k, v in self.waiting.items() if k not in [int(m['index'])-1 for m in self.memory] and v != float('inf')}
		msg += f"\t\t{[v+1 for v in sorted(not_cooking, key=not_cooking.get)]}"
		return msg

	def status(self):
		msg = ""
		if len(self.memory) != 0 and len(list(set(self.waiting))) > 1:
			msg += " ~"

		if len(self.memory) != 0:
			msg += " Cooking: "
			mems = []
			for mem in sorted(self.memory, key = lambda v: v["index"]):
				mems.append(f"{mem['index']}: {'{:.2f}'.format(max(mem['delay'].time_until(), 0.0))}s")
			msg += ', '.join(mems)

		'''
		if len(list(set(self.waiting))) > 1:
			msg += " Next: "
			waits = []
			s = self.waiting[:]
			print(self.waiting)
			s.sort()
			for t in s:	
				i = self.waiting.index(t)

				if t != float('inf') and str(i + 1) not in [m["index"] for m in self.memory]:
					waits.append(str(i + 1))

			msg += ', '.join(waits) 
		'''

		return msg