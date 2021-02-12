import win32gui, win32con, ctypes  

from GUI import GUI
from bot import Bot

if __name__== "__main__":
	print("Initiating bot...")
	
	gui = GUI()
	bot = Bot(gui)

	bot.update()
	