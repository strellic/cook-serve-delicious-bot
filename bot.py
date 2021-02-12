import win32gui, win32con, ctypes  
import keyboard
import time
import sys
import re

from AnalysisEngine import AnalysisEngine
from OCREngine import OCREngine
from Brain import Brain
from Delay import Delay

class Bot:
	def __init__(self, GUI):
		self.is_terminated = False
		self.GUI = GUI

		self.hwnd = self.hook_window()
		self.OCR = OCREngine()
		self.AnalysisEngine = AnalysisEngine()
		self.Brain = Brain()

		self.last_ss_time = time.time_ns()
		self.last_ss = None
		self.active = []

		self.last_cook_time = None
		self.last_food = ""

		self.is_paused = False

		self.is_editing = False
		self.edit_stack = []

		keyboard.on_press(self.key_hook)
		keyboard.add_hotkey("enter", self.end_edit)

	def key_hook(self, e):
		if e.name == "f1":
			self.terminate()
		elif e.name == "f2":
			self.pause()
		elif e.name == "f3":
			self.edit()
		elif self.is_editing and not keyboard.is_pressed("ctrl"):
			self.edit_stack.append(e.name)

	def hook_window(self):
		windows = []
		def enum_handler(hwnd, lParam):
			title = win32gui.GetWindowText(hwnd)
			if title == 'Cook, Serve, Delicious!' or 'CSDBot:' in title:
				windows.append(hwnd)

		win32gui.EnumWindows(enum_handler, None)
		
		if len(windows) == 0:
			input("Error! Game not detected. Press [ENTER] when the game is loaded. ")
			return self.hook_window()

		return windows[0]

	def terminate(self):
		self.is_terminated = True

	def edit(self):
		self.is_editing = True

	def pause(self):
		self.is_paused = not self.is_paused
		keyboard.press_and_release("esc")

	def end_edit(self):
		if not self.is_editing:
			return

		self.is_editing = False

		if len(self.edit_stack) > 0 and self.edit_stack[-1] != "enter":
			self.edit_stack.append("enter")

		self.Brain.save(self.edit_stack)

		self.edit_stack = []

	def title(self):
		base = "CSDBot: [F1 - QUIT / F2 - PAUSE / F3 - EDIT]"
		if self.is_terminated:
			print(f"[!] Bye!")
			win32gui.SetWindowText(self.hwnd, "Cook, Serve, Delicious!")
			sys.exit(0)
		elif self.is_paused:
			win32gui.SetWindowText(self.hwnd, f"{base} ~ Paused")
		elif self.is_editing:
			win32gui.SetWindowText(self.hwnd, f"{base} ~ {self.Brain.lastUnknown}: {self.edit_stack}")
		else:
			win32gui.SetWindowText(self.hwnd, f"{base}{self.Brain.status()}")

	def update(self):
		while True:
			self.title()

			if self.is_paused:
				continue

			if time.time_ns() - self.last_ss_time > 100000000:
				delta = (time.time_ns() - self.last_ss_time) / 1000000000
				self.last_ss_time = time.time_ns()

				image = self.AnalysisEngine.normalize(self.GUI.screenshot(self.hwnd))

				if self.last_ss and self.AnalysisEngine.image_equal(image, self.last_ss):
					Delay.add_freezetime(delta)
				elif delta > 1.2:
					Delay.add_freezetime(delta - 0.5)

				self.last_ss = image
				self.active = self.AnalysisEngine.get_active(image)

				self.Brain.update(self.active)

				if not self.Brain.is_cooking():
					text = self.OCR.text(self.AnalysisEngine.crop_order(image))

					text = text.split("\n")[0].split("  ")[0]
					text = re.sub(r'[^a-zA-Z ]', "", text).strip()

					if text:
						if text == "Robbery Witness Criminal Description":
							desc = self.OCR.text(self.AnalysisEngine.crop_desc(image))
							desc = re.sub(r'\n', " ", desc).strip()
							desc = desc.lower()				
							self.Brain.robber(desc)
						else:
							if text == self.last_food and time.time_ns() - self.last_ss_time < 100000000:
								continue # make sure the same food doesn't get parsed twice!

							self.Brain.process(text)
							self.last_food = text
							self.last_cook_time = time.time_ns()