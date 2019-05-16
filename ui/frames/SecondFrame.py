from tkinter import *

from tools.objects.DatabaseUpdater import DatabaseUpdater


class SecondFrame(Frame):
	def __init__(self, root, controller):
		super(SecondFrame, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root

		dbs = self.controller.available_databases
		self.db_selection = IntVar()
		self.db_selection.set(value=0)

		self.viewer = Frame(self)

		self.prompt_frame = Frame(self.viewer)
		self.prompt_label = Label(self.prompt_frame, text="2. Which database "
														  "would you like to "
														  "retrieve pham data "
														  "from?")
		self.prompt_label.pack(side=TOP, anchor=W, fill=None, expand=True)

		for i in range(len(dbs)):
			temp_radio = Radiobutton(master=self.prompt_frame,
									 variable=self.db_selection,
									 value=i, text=dbs[i])
			temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

		self.prompt_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

		self.button_frame = Frame(self.viewer)
		self.back_button = Button(self.button_frame, text="Back",
								  command=self.back)
		self.back_button.pack(side=LEFT, anchor=SW, fill=None, expand=True)
		self.next_button = Button(self.button_frame, text="Next",
								  command=self.next)
		self.next_button.pack(side=LEFT, anchor=SE, fill=None, expand=True)
		self.button_frame.pack(side=BOTTOM, anchor=N, fill=BOTH, expand=True)

		self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

	def next(self):
		self.controller.selected_database = \
			self.controller.available_databases[self.db_selection.get()]
		updater = DatabaseUpdater(controller=self.controller,
								  database=self.controller.selected_database)
		updater.update_db()

		self.controller.redraw(frame=3)

	def back(self):
		self.controller.redraw(frame=1)
