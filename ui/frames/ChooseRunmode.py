from tkinter import *


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

		runmodes = ["Retrieve phams from selected Hosts",
					"Retrieve phams from selected Clusters",
					"Retrieve phams from selected Phages",
					"Retrieve phams from all phages",
					"Retrieve phams from random phages"]

		self.viewer = Frame(self)

		self.prompt_frame = Frame(self.viewer)
		self.prompt_label = Label(self.prompt_frame,
								  text="1. Which type of pham data do you "
									   "want to retrieve?",
								  font=self.controller.font)
		self.prompt_label.pack(side=TOP, anchor=W, fill=None, expand=True)

		for i in range(len(runmodes)):
			temp_radio = Radiobutton(master=self.prompt_frame,
									 variable=self.runmode_selection,
									 value=i, text=runmodes[i],
									 font=self.controller.font)
			temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

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
		self.controller.runmode = self.runmode_selection.get()
		self.controller.final_status = self.final_only.get()
		self.controller.redraw_window(frame=2)
