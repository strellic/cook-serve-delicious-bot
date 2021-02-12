from PIL import Image, ImageChops, ImageDraw, ImageStat
import math

ORIGINAL = (1282, 721)
TICKET_NO = (912, 570, 1009, 605)

SLOTS = [
	(27, 98),
	(31, 151),
	(32, 223),
	(32, 280),
	(32, 344),
	(33, 404),
	(29, 455)
]

class AnalysisEngine:
	def __init__(self):
		pass

	def crop_order(self, im):
		width, height = im.size

		newLeft = width//5
		newRight = width - width//4

		newTop = height-(height//5) - 10
		newBot = ((newTop + height) // 2) - 40
		cropped = im.crop((newLeft, newTop, newRight, newBot))

		return cropped

	def crop_desc(self, im):
		width, height = im.size

		newLeft = width//5
		newRight = width - width//5

		newTop = height-(height//5) + 20
		newBot = ((newTop + height) // 2) + 20
		cropped = im.crop((newLeft, newTop, newRight, newBot))

		cropped.save("desc.png")

		return cropped

	def normalize(self, im):
		bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
		diff = ImageChops.difference(im, bg)
		diff = ImageChops.add(diff, diff, 2.0, -100)
		bbox = diff.getbbox()
		im = im.crop(bbox)
		return im.resize(ORIGINAL)

	def image_equal(self, im1, im2):
		diff_img = ImageChops.difference(im1, im2)
		stat = ImageStat.Stat(diff_img)
		diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)
		return diff_ratio * 100 < 0.0003

	def get_num(self, image):
		im = image.crop(TICKET_NO)
		return im

	def get_active(self, image):
		active = []
		for coord in SLOTS:
			color = image.getpixel(coord)
			active.append(sum(color)/3 >= 250)
		return active
