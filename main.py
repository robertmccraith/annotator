from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.graphics import Color, Ellipse, Line
from kivy.config import Config

import numpy as np
import cv2
import glob


im_list = glob.glob("*.png")

im=cv2.imread(im_list[0])
img_dim = im.shape
img = 0

annotations = []
mode = 0 #0 = draw, 1 = erase





Config.set('graphics', 'width', int(img_dim[1]*1.25))
Config.set('graphics', 'height', int(img_dim[0]))
Config.set('graphics', 'resizable', 0)

Builder.load_string('''
<PaintWidget>
	id: 'PaintWidget'
	size_x: 0.8
	size_y:1
	Image:
		source: root.parent.parent.img_src
		opacity: 0.5



<RootWidget>
	BoxLayout:
		orientation: 'horizontal'
		
		PaintWidget:

		StackLayout:
			size_hint: 0.2, 1
			orientation: 'lr-bt'
			Button:
				text: 'Clear'
				size_hint: 1, None
				on_press: root.clear()
			Button:
				text: 'Next'
				size_hint: 1, None
				on_press: root.change(+1)
			Button:
				text: 'Previous'
				size_hint: 1, None
				on_press: root.change(-1)
			Button:
				text: 'Undo'
				size_hint: 1, None
				on_press: root.changeMode()
''')



class PaintWidget(BoxLayout):


	def on_touch_down(self, touch):


		if self.collide_point(*touch.pos):
			if mode == 1:
				return

			color = (0, 1, 0)
			with self.canvas:
				Color(*color, mode='rgb')
				d = 15
				touch.ud['line'] = Line(points=(touch.x, touch.y), close=True, joint='round')
				global annotations
				#annotations = np.array([touch.x, touch.y])

	def on_touch_move(self, touch):


		if self.collide_point(*touch.pos):

			if mode == 0:#check if draw or delete, will make this work later

				if not touch.ud:
					color = (0, 1, 0)
					with self.canvas:
						Color(*color, mode='rgb')
						d = 15
						touch.ud['line'] = Line(points=(touch.x, touch.y),close = True, joint='round')

				else:	
					touch.ud['line'].points += [touch.x, touch.y]
			else:
				for x in annotations:
					print "ann", x
					print "touch", [touch.x, touch.y]

					if [touch.x, touch.y] in x.tolist():
						del x
						print "deletion"
						continue

				for x in self.canvas.children:
					print x
					if type(x) is Line:
						xs = np.reshape(x.points, (-1, 2))
						print xs
						del x



	def on_touch_up(self, touch):
		try:
			if len(touch.ud)>0:
				global annotations

				anns = np.reshape(np.asarray(touch.ud['line'].points), (-1, 2))
				annotations.append(anns)

		except Exception, e:
			None

		
	


class RootWidget(FloatLayout):

	img_src = StringProperty(im_list[img])
	
	def clear(self):
		self.children[0].children[1].canvas.children = self.children[0].children[1].canvas.children[:1]

		global annotations
		annotations = []

	def change(self, c):
		image = np.zeros((480, 640))
		cv2.fillPoly(image, [a.astype(int) for a in annotations ], 255)
		im_name = im_list[img].split("/")[-1]
		filename = im_list[img].replace(im_name , "annotated-"+im_name)

		cv2.imwrite(filename, np.flipud(image))

		self.clear()
		global img
		img = (img + c)%len(im_list)
		self.img_src = im_list[img]


	def changeMode(self):
		if len(self.children[0].children[1].canvas.children) > 3:
			self.children[0].children[1].canvas.children = self.children[0].children[1].canvas.children[:-3]
		global annotations
		annotations = annotations[:-1]

class AnnotatorApp(App):

	def build(self):
		return RootWidget()



if __name__ == '__main__':
	AnnotatorApp().run()