from tkinter import *


class FirstFrame(Frame):
	def __init__(self, root, controller):
		super(FirstFrame, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root

		self.runmode_selection = IntVar()
		self.runmode_selection.set(value=0)

		runmodes = ["Retrieve phams from selected Hosts",
					"Retrieve phams from selected Clusters",
					"Retrieve phams from selected Phages",
					"Retrieve phams from all phages",
					"Retrieve phams from random phages"]

		self.viewer = Frame(self)

		self.prompt_frame = Frame(self.viewer)
		self.prompt_label = Label(self.prompt_frame, text="1. Which type of "
														  "pham data do you "
														  "want to retrieve?")
		self.prompt_label.pack(side=TOP, anchor=W, fill=None, expand=True)

		for i in range(len(runmodes)):
			temp_radio = Radiobutton(master=self.prompt_frame,
									 variable=self.runmode_selection,
									 value=i, text=runmodes[i])
			temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

		self.prompt_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

		self.button_frame = Frame(self.viewer)
		self.next_button = Button(self.button_frame, text="Next",
								  command=self.next)
		self.next_button.pack(side=BOTTOM, anchor=SE, fill=None, expand=True)
		self.button_frame.pack(side=TOP, anchor=N, fill=BOTH, expand=True)

		self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

	def next(self):
		self.controller.runmode_selection = self.runmode_selection.get()
		self.controller.redraw(frame=2)
