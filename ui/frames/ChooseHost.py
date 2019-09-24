from tkinter import *


class ChooseHost(Frame):
	def __init__(self, root, controller):
		super(ChooseHost, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root

		self.viewer = Frame(self)

		self.instruction_frame = Frame(self.viewer)
		self.instruction_label = Label(self.instruction_frame,
									   text="3. Choose the hosts whose "
											"phages will be included in "
											"the splistree diagram, then "
											"click 'Next'.",
									   font=self.controller.font)
		self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
									expand=True)
		self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
									expand=True)

		self.selection_frame = Frame(self.viewer)

		self.available_frame = Frame(self.selection_frame)
		self.available_label = Label(self.available_frame,
									 text="Available Hosts",
									 font=self.controller.font)
		self.available_label.pack(side=TOP, anchor=N, fill=None,
								  expand=True)
		self.available_list = Listbox(self.available_frame, width=30,
									  height=30,
									  font=self.controller.font,
									  selectmode=EXTENDED)
		for host in self.controller.available_hosts:
			self.available_list.insert(END, host)

		self.available_list.pack(side=LEFT, anchor=N, fill=None,
								 expand=True)
		self.available_frame.pack(side=LEFT, anchor=N, fill=None,
								  expand=True)

		self.middle_button_frame = Frame(self.selection_frame)

		self.add_button = Button(self.middle_button_frame,
								 text="Add to Selection >>",
								 font=self.controller.font,
								 command=self.add)
		self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
							 expand=True)
		self.remove_button = Button(self.middle_button_frame,
									text="<< Remove from Selection",
									font=self.controller.font,
									command=self.remove)
		self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
								expand=True)

		self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
									  fill=None, expand=True)

		self.selected_frame = Frame(self.selection_frame)
		self.selected_label = Label(self.selected_frame,
									text="Selected Hosts",
									font=self.controller.font)
		self.selected_label.pack(side=TOP, anchor=N, fill=None,
								 expand=True)
		self.selected_list = Listbox(self.selected_frame, width=30,
									 height=30, selectmode=EXTENDED,
									 font=self.controller.font)
		self.selected_list.pack(side=LEFT, anchor=N, fill=None,
								expand=True)
		self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
								 expand=True)

		self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
								  expand=True)

		self.bottom_button_frame = Frame(self.viewer)
		self.back_button = Button(self.bottom_button_frame, text="Back",
								  font=self.controller.font,
								  command=self.back)
		self.back_button.pack(side=LEFT, anchor=SW, fill=None, expand=True)
		self.next_button = Button(self.bottom_button_frame,
								  text="Next",
								  font=self.controller.font,
								  command=self.next)
		self.next_button.pack(side=LEFT, anchor=SE, fill=None, expand=True)
		self.bottom_button_frame.pack(side=BOTTOM, anchor=S, fill=X,
									  expand=True)

		self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

	def add(self):
		sel = self.available_list.curselection()
		for i in sel:
			add_name = self.controller.available_hosts[i]
			if add_name not in self.selected_list.get(0, END):
				self.selected_list.insert(END, add_name)
		return

	def remove(self):
		sel = self.selected_list.curselection()

		# need to delete in reverse order because indices shift otherwise
		for i in list(reversed(sel)):
			self.selected_list.delete(i)
		return

	def back(self):
		self.controller.redraw_window(frame=2)
		return

	def next(self):
		selection = self.selected_list.get(0, END)
		print(selection)
		self.controller.selected_hosts = list(selection)

		self.controller.redraw_window(frame=5)
		return
