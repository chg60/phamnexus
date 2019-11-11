from tkinter import *

from data.constants import *


class ChooseRunmode(Frame):
	def __init__(self, root, controller):
		super(ChooseRunmode, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root

		self.runmode_selection = IntVar()
		self.runmode_selection.set(value=0)

		self.final_only = IntVar()
		self.final_only.set(value=0)

		self.viewer = Frame(self)
		self.labels = LABELS["RunmodeFrame"]

		self.prompt_frame = Frame(self.viewer)
		self.prompt_label = Label(self.prompt_frame,
								  text=self.labels["Instruct"][0],
								  font=self.controller.font)
		self.prompt_label.pack(side=TOP, anchor=W, fill=None, expand=True)

		for i in range(len(self.labels["Runmodes"])):
			radio = Radiobutton(master=self.prompt_frame,
								font=self.controller.font,
								variable=self.runmode_selection,
								text=self.labels["Runmodes"][i],
								value=i)
			radio.pack(side=TOP, anchor=W, fill=None, expand=True)

		self.prompt_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

		self.final_only_frame = Frame(self.viewer)
		self.final_only_checkbox = Checkbutton(master=self.final_only_frame,
											   variable=self.final_only,
											   text="Exclude draft genomes",
											   font=self.controller.font)
		self.final_only_checkbox.pack(side=TOP, anchor=NW, fill=None,
									  expand=True)
		self.final_only_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

		self.button_frame = Frame(self.viewer)
		self.next_button = Button(self.button_frame, text="Next",
								  font=self.controller.font,
								  command=self.next)
		self.next_button.pack(side=BOTTOM, anchor=SE, fill=None, expand=True)
		self.button_frame.pack(side=TOP, anchor=N, fill=BOTH, expand=True)

		self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

	def next(self):
		runmode = self.runmode_selection.get()
		print("Runmode selected: {}".format(runmode))
		self.controller.runmode = self.runmode_selection.get()
		self.controller.exclude_draft = self.final_only.get()
		self.controller.redraw_window(frame=2)
