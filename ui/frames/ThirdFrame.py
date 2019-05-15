from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo
from tools.scripts.misc_functions import *
import random


class ThirdFrame(Frame):
	def __init__(self, root, controller):
		super(ThirdFrame, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root
		self.runmode = self.controller.runmode
		username = self.controller.username
		password = self.controller.password
		database = self.controller.selected_database
		status = self.controller.final_status

		self.viewer = Frame(self)

		if self.runmode == 0:
			self.controller.available_hosts = get_database_hosts(username,
																 password,
																 database)

			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="3. Choose the hosts whose "
												"phages will be included in "
												"the splistree diagram, then "
												"click 'Make Nexus File'.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.selection_frame = Frame(self.viewer)

			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Hosts")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=30,
										  height=30,
										  selectmode=MULTIPLE)
			for host in self.controller.available_hosts:
				self.available_list.insert(END, host)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			self.middle_button_frame = Frame(self.selection_frame)

			self.add_button = Button(self.middle_button_frame,
									 text="Add to Selection >>",
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Hosts")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=30,
										 height=30, selectmode=MULTIPLE)
			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 1:
			self.controller.available_clusters = get_database_clusters(
				username, password, database)
			self.controller.available_clusters.sort()

			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="3. Choose the clusters whose "
												"phages will be included "
												"in the splistree diagram, "
												"then click 'Make Nexus "
												"File'.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.selection_frame = Frame(self.viewer)

			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Clusters")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=30,
										  height=30,
										  selectmode=MULTIPLE)
			for host in self.controller.available_clusters:
				self.available_list.insert(END, host)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			self.middle_button_frame = Frame(self.selection_frame)

			self.add_button = Button(self.middle_button_frame,
									 text="Add to Selection >>",
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Clusters")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=30,
										 height=30, selectmode=MULTIPLE)
			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 2:
			self.controller.available_phages = get_database_phages(username,
																   password,
																   database,
																   status)
			self.controller.available_phages.sort()

			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="3. Choose the phages to be "
												"included in the splistree "
												"diagram, then click 'Make "
												"Nexus File'.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.selection_frame = Frame(self.viewer)

			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=30,
										  height=30,
										  selectmode=MULTIPLE)
			for host in self.controller.available_phages:
				self.available_list.insert(END, host)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			self.middle_button_frame = Frame(self.selection_frame)

			self.add_button = Button(self.middle_button_frame,
									 text="Add to Selection >>",
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=30,
										 height=30, selectmode=MULTIPLE)
			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 3:
			self.viewer = Frame(self)

			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="3. All phages have been "
												"selected. Just click 'Make "
												"Nexus File' to use all "
												"phages, or select phages "
												"you wish to exclude, and "
												"remove them from the "
												"selection first.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.controller.available_phages = get_database_phages(username,
																   password,
																   database,
																   status)
			self.controller.available_phages.sort()

			self.selection_frame = Frame(self.viewer)

			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=30,
										  height=30,
										  selectmode=MULTIPLE)
			for host in self.controller.available_phages:
				self.available_list.insert(END, host)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			self.middle_button_frame = Frame(self.selection_frame)

			self.add_button = Button(self.middle_button_frame,
									 text="Add to Selection >>",
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=30,
										 height=30, selectmode=MULTIPLE)
			for host in self.controller.available_phages:
				self.selected_list.insert(END, host)

			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)


		elif self.runmode == 4:
			self.viewer = Frame(self)

			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="3. Random phages have been "
												"selected.  Just click 'Make "
												"Nexus File' to use these "
												"phages, or you can modify "
												"the selected list first.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.controller.available_phages = get_database_phages(username,
																   password,
																   database,
																   status)
			self.controller.available_phages.sort()

			self.selection_frame = Frame(self.viewer)

			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=30,
										  height=30,
										  selectmode=MULTIPLE)

			for phage in self.controller.available_phages:
				self.available_list.insert(END, phage)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			self.middle_button_frame = Frame(self.selection_frame)

			self.add_button = Button(self.middle_button_frame,
									 text="Add to Selection >>",
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=30,
										 height=30, selectmode=MULTIPLE)

			available_indices = range(0, len(self.controller.available_phages))
			indices = random.sample(available_indices, int(len(
				available_indices)/5))
			indices.sort()
			for index in indices:
				phage = self.controller.available_phages[index]
				self.selected_list.insert(END, phage)

			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		self.bottom_button_frame = Frame(self.viewer)
		self.back_button = Button(self.bottom_button_frame, text="Back",
								  command=self.back)
		self.back_button.pack(side=LEFT, anchor=SW, fill=None, expand=True)
		self.next_button = Button(self.bottom_button_frame,
								  text="Make Nexus File",
								  command=self.make_nexus)
		self.next_button.pack(side=LEFT, anchor=SE, fill=None, expand=True)
		self.bottom_button_frame.pack(side=BOTTOM, anchor=S, fill=X,
									  expand=True)

		self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

	def add(self):
		sel = self.available_list.curselection()
		for i in sel:
			if self.runmode == 0:
				add_name = self.controller.available_hosts[i]
				if add_name not in self.selected_list.get(0, END):
					self.selected_list.insert(END, add_name)
			elif self.runmode == 1:
				add_name = self.controller.available_clusters[i]
				if add_name not in self.selected_list.get(0, END):
					self.selected_list.insert(END, add_name)
			elif self.runmode == 2:
				add_name = self.controller.available_phages[i]
				if add_name not in self.selected_list.get(0, END):
					self.selected_list.insert(END, add_name)
		return

	def remove(self):
		sel = self.selected_list.curselection()
		print(sel)
		# need to delete in reverse order because indices shift otherwise
		for i in list(reversed(sel)):
			print("Deleting {}".format(i))
			self.selected_list.delete(i)

	def back(self):
		self.controller.redraw(frame=2)

	def make_nexus(self):
		selection = self.selected_list.get(0, END)
		result = asksaveasfilename(initialdir="~",
								   title="Choose save filename",
								   filetypes=(("Nexus", "*.nex *.nxs "
														"*.nexus"),))
		if len(result) == 0 or result == "":
			showinfo(message="Program can't continue without a save "
							 "filename. Please click 'Make Nexus File' "
							 "again, and this time indicate a save filename.")
			return

		if self.runmode == 0:
			self.controller.selected_hosts = list(selection)
		elif self.runmode == 1:
			self.controller.selected_clusters = list(selection)
		elif self.runmode == 2 or self.runmode == 3 or self.runmode == 4:
			self.controller.selected_phages = list(selection)

		self.controller.make_nexus(filename=result)
		self.controller.redraw(frame=1)
