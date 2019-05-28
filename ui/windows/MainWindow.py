from tkinter import *

from ui.frames.RunmodeFrame import RunmodeFrame
from ui.frames.DatabaseFrame import DatabaseFrame
# from ui.frames.HostFrame import HostFrame
# from ui.frames.ClusterFrame import ClusterFrame
from ui.frames.PhageFrame import PhageFrame


class MainWindow:
	def __init__(self, controller):
		self.controller = controller

		self.root = Tk()
		self.root.wm_title("PhameratorNexusBuilder")
		self.root.protocol("WM_DELETE_WINDOW", self.controller.quit)

		width, height = int(self.root.winfo_screenwidth() * 0.75), \
						int(self.root.winfo_screenheight() * 0.75)
		x_offset = int((self.root.winfo_screenwidth() - width) / 2)
		y_offset = int((self.root.winfo_screenheight() - height) / 2)

		self.root.wm_geometry("{}x{}+{}+{}".format(width, height, x_offset,
												   y_offset))

		# Create menu bar
		self.menu_bar = Menu(self.root, tearoff=0)
		self.root.config(menu=self.menu_bar)

		# Create file menu
		self.file = Menu(self.menu_bar, tearoff=0)
		self.file.add_command(label="Preferences",
							  command=None)
		# self.controller.edit_preferences)
		self.file.add_separator()
		self.file.add_command(label="Quit", command=self.controller.quit)
		self.menu_bar.add_cascade(menu=self.file, label="File")

		# Create help menu
		self.help = Menu(self.menu_bar, tearoff=0)
		self.help.add_command(label="Documentation",
							  command=self.controller.documentation)
		self.help.add_command(label="Report a Bug",
							  command=self.controller.report_bug)
		self.help.add_command(label="Check for Updates",
							  command=self.controller.check_updates)
		self.menu_bar.add_cascade(menu=self.help, label="Help")

		self.layout = RunmodeFrame(root=self.root, controller=self.controller)

	def redraw(self, frame):
		self.layout.destroy()
		if frame == 1:
			self.layout = RunmodeFrame(root=self.root,
									 controller=self.controller)
		if frame == 2:
			self.controller.get_mysql_dbs()
			self.layout = DatabaseFrame(root=self.root,
									  controller=self.controller)
		if frame == 3:
			self.layout = PhageFrame(root=self.root,
									 controller=self.controller)
		if frame == 4:
			self.layout = PhageFrame(root=self.root,
									 controller=self.controller)

	def launch(self):
		self.root.mainloop()

	def destroy(self):
		self.root.destroy()
