import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

class OCREngine:
	def __init__(self):
		pass

	def text(self, img):
		try:
			return pytesseract.image_to_string(img, timeout=1.0).replace("\\n", "\n")
		except:
			return ""