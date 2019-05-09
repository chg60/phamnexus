from tkinter import *

from ui.frames.FirstFrame import FirstFrame
from ui.frames.SecondFrame import SecondFrame
from ui.frames.ThirdFrame import ThirdFrame


class MainWindow:
	def __init__(self, controller):
		self.controller = controller

		self.root = Tk()
		self.root.wm_title("PhameratorNexusBuilder")

		width, height = int(self.root.winfo_screenwidth() * 0.75), \
						int(self.root.winfo_screenheight() * 0.75)
		x_offset = int((self.root.winfo_screenwidth() - width) / 2)
		y_offset = int((self.root.winfo_screenheight() - height) / 2)

		self.root.wm_geometry("{}x{}+{}+{}".format(width, height, x_offset,
												   y_offset))

		self.menu_bar = Menu(self.root, tearoff=0)
		self.root.config(menu=self.menu_bar)

		self.file = Menu(self.menu_bar, tearoff=0)
		self.file.add_command(label="Quit", command=self.controller.quit)
		self.menu_bar.add_cascade(menu=self.file, label="File")

		self.help = Menu(self.menu_bar, tearoff=0)
		self.help.add_command(label="Documentation",
							  command=self.controller.documentation)
		self.help.add_command(label="Report a Bug",
							  command=self.controller.report_bug)
		self.help.add_command(label="Check for Updates",
							  command=self.controller.check_updates)
		self.menu_bar.add_cascade(menu=self.help, label="Help")

		self.layout = FirstFrame(root=self.root, controller=self.controller)

	def redraw(self, frame):
		self.layout.destroy()
		if frame == 1:
			self.layout = FirstFrame(root=self.root,
									 controller=self.controller)
		if frame == 2:
			self.controller.get_mysql_dbs()
			self.layout = SecondFrame(root=self.root,
									  controller=self.controller)
		if frame == 3:
			self.layout = ThirdFrame(root=self.root,
									 controller=self.controller)


	def launch(self):
		self.root.mainloop()

	def destroy(self):
		self.root.destroy()
