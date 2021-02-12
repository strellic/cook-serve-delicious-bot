import win32gui, win32con, ctypes  
from PIL import ImageGrab

TITLE_BAR_HEIGHT = 38

class GUI:
	def __init__(self):
		pass

	def dimensions(self, hwnd):
		ctypes.windll.user32.SetProcessDPIAware()

		win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST,0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
		win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
		win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST,0,0,0,0, win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

		rect = ctypes.wintypes.RECT()

		ctypes.windll.dwmapi.DwmGetWindowAttribute(ctypes.wintypes.HWND(hwnd),
		  ctypes.wintypes.DWORD(9),
		  ctypes.byref(rect),
		  ctypes.sizeof(rect)
		)

		return (rect.left, rect.top + TITLE_BAR_HEIGHT, rect.right, rect.bottom)

	def screenshot(self, hwnd):
		dims = self.dimensions(hwnd)
		return ImageGrab.grab(dims)