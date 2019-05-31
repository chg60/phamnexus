from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo
import random


class FinalizePhage(Frame):
	def __init__(self, root, controller):
		super(FinalizePhage, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root

		# Get selection data from
		self.runmode = self.controller.runmode
		self.metadata = self.controller.metadata
		self.username = self.controller.username
		self.password = self.controller.password
		self.database = self.controller.selected_database
		self.status = self.controller.final_status

		self.available_phages = self.controller.available_phages
		self.available_hosts = self.controller.available_hosts
		self.available_clusters = self.controller.available_clusters

		self.phage_index = dict()
		self.host_to_phage = dict()
		self.cluster_to_phage = dict()

		for phage in self.available_phages:
			# phages are unique, so only one index can be returned
			self.phage_index[phage] = self.metadata["PhageID"].index(phage)

			# Get host data and add this phage to that host's list of phages
			# for easier list sorting
			host = self.metadata["HostStrain"][self.phage_index[phage]]
			host_phages = self.host_to_phage.get(host, [])
			host_phages.append(phage)
			self.host_to_phage[host] = host_phages

			# Get cluster data and add this phage to that cluster's list of
			# phages for easier list sorting
			cluster = self.metadata["Cluster"][self.phage_index[phage]]
			cluster_phages = self.cluster_to_phage.get(cluster, [])
			cluster_phages.append(phage)
			self.cluster_to_phage[cluster] = cluster_phages

		# List of ways that the PhageIDs can be sorted
		self.sort_mode = IntVar()
		self.sort_mode.set(value=0)
		sort_modes = ["Sort by PhageID",
					  "Sort by Host, PhageID",
					  "Sort by Cluster, PhageID"]

		# Viewer frame to hold all runmode-specific widgets
		self.viewer = Frame(self)

		if self.runmode == 0:
			# Build a frame that will house the instructions and sort
			# selection buttons
			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="4. Phage selection has been "
												"auto-filled based on your "
												"Host and status selections. "
												"You may add or remove "
												"additional phages.")

			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30,
										  selectmode=EXTENDED)
			for phage in self.available_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), add])
				self.available_list.insert(END, display)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			# Build a frame in the middle that will house buttons to aid in
			# phage selection/deselection
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

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on chosen host(s) and status
			auto_chosen_phages = list()
			chosen_hosts = self.controller.selected_hosts
			if self.status == 1:
				for phage in self.available_phages:
					host = self.metadata["HostStrain"][self.phage_index[phage]]
					status = self.metadata["Status"][self.phage_index[phage]]
					if host in chosen_hosts and status != "draft":
						auto_chosen_phages.append(phage)
			else:
				for phage in self.available_phages:
					host = self.metadata["HostStrain"][self.phage_index[phage]]
					if host in chosen_hosts:
						auto_chosen_phages.append(phage)

			# Populate auto_chosen_phages into selected list
			for phage in auto_chosen_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)

			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 1:
			# Build a frame that will house the instructions and sort
			# selection buttons
			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="4. Phage selection has been "
												"auto-filled based on your "
												"Cluster and status "
												"selections. You may add or "
												"remove additional phages "
												"(matching your status "
												"selection).")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Clusters")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30,
										  selectmode=EXTENDED)
			for phage in self.available_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), add])
				self.available_list.insert(END, display)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			# Build a frame in the middle that will house buttons to aid in
			# phage selection/deselection
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

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on chosen host(s) and status
			auto_chosen_phages = list()
			chosen_clusters = self.controller.selected_clusters
			if self.status == 1:
				for phage in self.available_phages:
					cluster = self.metadata["Cluster"][self.phage_index[phage]]
					status = self.metadata["Status"][self.phage_index[phage]]
					if cluster in chosen_clusters and status != "draft":
						auto_chosen_phages.append(phage)
			else:
				for phage in self.available_phages:
					cluster = self.metadata["Cluster"][self.phage_index[phage]]
					if cluster in chosen_clusters:
						auto_chosen_phages.append(phage)

			# Populate auto_chosen_phages into selected list
			for phage in auto_chosen_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)

			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 2:
			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="4. Choose the phages to be "
												"included in the splistree "
												"diagram, then click 'Make "
												"Nexus File'.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30,
										  selectmode=EXTENDED)
			for phage in self.available_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), add])
				self.available_list.insert(END, display)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			# Build a frame in the middle that will house buttons to aid in
			# phage selection/deselection
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

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 height=30, selectmode=EXTENDED)

			# Don't auto-select phages
			auto_chosen_phages = list()

			# Populate auto_chosen_phages into selected list
			for phage in auto_chosen_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)

			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 3:
			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="4. All phages have been "
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

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30,
										  selectmode=EXTENDED)

			# Auto-select phages based on status
			for phage in self.available_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), add])
				self.available_list.insert(END, display)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			# Build a frame in the middle that will house buttons to aid in
			# phage selection/deselection
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

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on chosen status
			auto_chosen_phages = list()
			if self.status == 1:
				for phage in self.available_phages:
					status = self.metadata["Status"][self.phage_index[phage]]
					if status != "draft":
						auto_chosen_phages.append(phage)
			else:
				for phage in self.available_phages:
						auto_chosen_phages.append(phage)

			# Populate auto_chosen_phages into selected list
			for phage in auto_chosen_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)

			self.selected_list.pack(side=LEFT, anchor=N, fill=None,
									expand=True)
			self.selected_frame.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)

			self.selection_frame.pack(side=TOP, anchor=CENTER, fill=BOTH,
									  expand=True)

		elif self.runmode == 4:
			self.instruction_frame = Frame(self.viewer)
			self.instruction_label = Label(self.instruction_frame,
										   text="4. Random phages have been "
												"selected.  Just click 'Make "
												"Nexus File' to use these "
												"phages, or you can modify "
												"the selected list first.")
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages")
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30,
										  selectmode=EXTENDED)
			for phage in self.available_phages:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), add])
				self.available_list.insert(END, display)

			self.available_list.pack(side=LEFT, anchor=N, fill=None,
									 expand=True)
			self.available_frame.pack(side=LEFT, anchor=N, fill=None,
									  expand=True)

			# Build a frame in the middle that will house buttons to aid in
			# phage selection/deselection
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

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages")
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on random and chosen status
			auto_chosen_phages = list()
			if self.status == 1:
				for phage in self.available_phages:
					status = self.metadata["Status"][self.phage_index[phage]]
					if status != "draft":
						auto_chosen_phages.append(phage)
			else:
				for phage in self.available_phages:
						auto_chosen_phages.append(phage)

			available_indices = range(0, len(auto_chosen_phages))
			indices = random.sample(available_indices, int(len(
				available_indices)/5))
			indices.sort()
			for index in indices:
				phage = auto_chosen_phages[index]
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)

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

	def sort(self, mode):
		# Empty the available list
		available = self.available_phages
		while len(self.available_list.get(0, END)) > 0:
			self.available_list.delete(END)

		# Get selected list and then empty it
		selected_phages = list()
		selected_hosts = list()
		selected_clusters = list()
		selection = self.selected_list.get(0, END)
		for select in selection:
			selected_phages.append(select.split()[0])
			selected_hosts.append(select.split()[1].lstrip("(").rstrip(","))
			selected_clusters.append(select.split()[2].rstrip(","))
		while len(self.selected_list.get(0, END)) > 0:
			self.selected_list.delete(END)

		# Sort by PhageID
		if mode == 0:
			available = sorted(available)
			selected = sorted(selected_phages)

			for phage in available:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.available_list.insert(END, display)

			for phage in selected:
				host = self.metadata["HostStrain"][self.phage_index[phage]]
				cluster = self.metadata["Cluster"][self.phage_index[phage]]
				status = self.metadata["Status"][self.phage_index[phage]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phage), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)

		elif mode == 1:
			available_hosts = self.available_hosts
			for host in available_hosts:
				host_phages = sorted(self.host_to_phage[host])
				for phage in host_phages:
					cluster = self.metadata["Cluster"][self.phage_index[phage]]
					status = self.metadata["Status"][self.phage_index[phage]]
					add = "\t({}, {}, {})".format(host, cluster, status)
					display = "".join(["{:<20}".format(phage), "{:<40}".format(
						add)])
					self.available_list.insert(END, display)

			selected_hosts = sorted(list(set(selected_hosts)))
			for host in selected_hosts:
				host_phages = sorted(self.host_to_phage[host])
				for phage1 in host_phages:
					for phage2 in selected_phages:
						if phage1 == phage2:
							cluster = self.metadata["Cluster"][
								self.phage_index[phage1]]
							status = self.metadata["Status"][
								self.phage_index[phage1]]
							add = "\t({}, {}, {})".format(host, cluster,
														  status)
							display = "".join(
								["{:<20}".format(phage1), "{:<40}".format(
									add)])
							self.selected_list.insert(END, display)
							continue

		elif mode == 2:
			available_clusters = self.available_clusters
			for cluster in available_clusters:
				cluster_phages = sorted(self.cluster_to_phage[cluster])
				for phage in cluster_phages:
					host = self.metadata["HostStrain"][self.phage_index[phage]]
					cluster = self.metadata["Cluster"][self.phage_index[phage]]
					status = self.metadata["Status"][self.phage_index[phage]]
					add = "\t({}, {}, {})".format(host, cluster, status)
					display = "".join(["{:<20}".format(phage), "{:<40}".format(
						add)])
					self.available_list.insert(END, display)

			selected_clusters = sorted(list(set(selected_clusters)))
			for cluster in selected_clusters:
				cluster_phages = sorted(self.cluster_to_phage[cluster])
				for phage1 in cluster_phages:
					for phage2 in selected_phages:
						if phage1 == phage2:
							host = self.metadata["HostStrain"][
								self.phage_index[phage1]]
							status = self.metadata["Status"][
								self.phage_index[phage1]]
							add = "\t({}, {}, {})".format(host, cluster,
														  status)
							display = "".join(
								["{:<20}".format(phage1), "{:<40}".format(
									add)])
							self.selected_list.insert(END, display)
							continue
		return

	def add(self):
		sel = self.available_list.curselection()
		for i in sel:
			add_name = self.available_phages[i]
			if add_name not in self.selected_list.get(0, END):
				host = self.metadata["HostStrain"][self.phage_index[add_name]]
				cluster = self.metadata["Cluster"][self.phage_index[add_name]]
				status = self.metadata["Status"][self.phage_index[add_name]]
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(add_name), "{:<40}".format(
					add)])
				self.selected_list.insert(END, display)
		return

	def remove(self):
		sel = self.selected_list.curselection()
		# need to delete in reverse order because indices shift otherwise
		for i in list(reversed(sel)):
			self.selected_list.delete(i)

	def back(self):
		if self.runmode < 2:
			self.controller.redraw_window(frame=int(2 + self.runmode))
		else:
			self.controller.redraw_window(frame=2)

	def make_nexus(self):
		selection = self.selected_list.get(0, END)
		selection = [select.split()[0] for select in selection]
		result = asksaveasfilename(initialdir="~",
								   title="Choose save filename",
								   filetypes=(("Nexus", "*.nex *.nxs "
														"*.nexus"),))
		self.root.update()
		if len(result) == 0 or result == "":
			showinfo(message="Program can't continue without a save "
							 "filename. Please click 'Make Nexus File' "
							 "again, and this time indicate a save filename.")
			return

		self.controller.selected_phages = list(selection)

		self.controller.make_nexus(filename=result)
		self.controller.redraw_window(frame=1)
