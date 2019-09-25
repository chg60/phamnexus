from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo
import random
import numpy as np


class FinalizePhage(Frame):
	def __init__(self, root, controller):
		super(FinalizePhage, self).__init__(master=root)
		self.pack(expand=True, fill=BOTH)

		self.controller = controller
		self.root = root

		# Get selection data from
		self.runmode = self.controller.runmode
		self.status = self.controller.final_status

		self.metadata = controller.metadata
		self.phages = controller.available_phages
		self.hosts = controller.available_hosts
		self.clusters = controller.available_clusters

		# List of ways that the PhageIDs can be sorted
		self.sort_mode = IntVar()
		self.sort_mode.set(value=0)
		sort_modes = ["Sort by PhageID (default)",
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
												"additional phages.",
										   font=controller.font)

			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 font=controller.font,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 font=controller.font,
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages",
										 font=controller.font)
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30, font=controller.font,
										  selectmode=EXTENDED)

			for phage in self.metadata:
				phageid = phage["PhageID"].decode("utf-8")
				host = phage["HostStrain"].decode("utf-8")
				cluster = phage["Cluster"].decode("utf-8")
				status = phage["Status"].decode("utf-8")
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phageid), add])
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
									 font=controller.font,
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										font=controller.font,
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages",
										font=controller.font)
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 height=30, selectmode=EXTENDED,
										 font=controller.font)

			# Auto-select phages based on chosen host(s) and status
			auto_chosen_phages = list()
			chosen_hosts = self.controller.selected_hosts
			# Convert chosen_hosts to bytes strings
			chosen_hosts = [host.encode('utf-8') for host in chosen_hosts]

			for host in chosen_hosts:
				phages = self.metadata[self.metadata["HostStrain"] == host]
				if self.status == 1:
					for phage in phages:
						if phage["Status"] != 'draft'.encode('utf-8'):
							phageid = phage["PhageID"].decode('utf-8')
							auto_chosen_phages.append(phageid)
				else:
					for phage in phages:
						phageid = phage["PhageID"].decode('utf-8')
						auto_chosen_phages.append(phageid)

			# Populate auto_chosen_phages into selected list
			for phage in sorted(auto_chosen_phages):
				data = self.metadata[self.metadata["PhageID"] ==
									 phage.encode('utf-8')]
				host = data['HostStrain'][0].decode('utf-8')
				cluster = data['Cluster'][0].decode('utf-8')
				status = data['Status'][0].decode('utf-8')
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
												"selection).",
										   font=controller.font)
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 font=controller.font,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 font=controller.font,
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Clusters",
										 font=controller.font)
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30, font=controller.font,
										  selectmode=EXTENDED)

			for phage in self.metadata:
				phageid = phage["PhageID"].decode("utf-8")
				host = phage["HostStrain"].decode("utf-8")
				cluster = phage["Cluster"].decode("utf-8")
				status = phage["Status"].decode("utf-8")
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phageid), add])
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
									 font=controller.font,
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										font=controller.font,
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages",
										font=controller.font)
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 font=controller.font,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on chosen cluster(s) and status
			auto_chosen_phages = list()
			chosen_clusters = self.controller.selected_clusters
			# Convert to utf-8 bytes strings
			chosen_clusters = [cluster.encode('utf-8') for cluster in
							   chosen_clusters]

			for cluster in chosen_clusters:
				phages = self.metadata[self.metadata["Cluster"] == cluster]
				if self.status == 1:
					for phage in phages:
						if phage["Status"] != 'draft'.encode('utf-8'):
							phageid = phage["PhageID"].decode('utf-8')
							auto_chosen_phages.append(phageid)
				else:
					for phage in phages:
						phageid = phage["PhageID"].decode('utf-8')
						auto_chosen_phages.append(phageid)

			# Populate auto_chosen_phages into selected list
			for phage in sorted(auto_chosen_phages):
				data = self.metadata[self.metadata["PhageID"] ==
									 phage.encode('utf-8')]
				host = data['HostStrain'][0].decode('utf-8')
				cluster = data['Cluster'][0].decode('utf-8')
				status = data['Status'][0].decode('utf-8')
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
												"Nexus File'.",
										   font=controller.font)
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 font=controller.font,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 font=controller.font,
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages",
										 font=controller.font)
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30, font=controller.font,
										  selectmode=EXTENDED)

			for phage in self.metadata:
				phageid = phage["PhageID"].decode("utf-8")
				host = phage["HostStrain"].decode("utf-8")
				cluster = phage["Cluster"].decode("utf-8")
				status = phage["Status"].decode("utf-8")
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phageid), add])
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
									 font=controller.font,
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										font=controller.font,
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages",
										font=controller.font)
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 font=controller.font,
										 height=30, selectmode=EXTENDED)

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
												"selection first.",
										   font=controller.font)
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 font=controller.font,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 font=controller.font,
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages",
										 font=controller.font)
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30, font=controller.font,
										  selectmode=EXTENDED)

			for phage in self.metadata:
				phageid = phage["PhageID"].decode("utf-8")
				host = phage["HostStrain"].decode("utf-8")
				cluster = phage["Cluster"].decode("utf-8")
				status = phage["Status"].decode("utf-8")
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phageid), add])
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
									 font=controller.font,
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										font=controller.font,
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages",
										font=controller.font)
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 font=controller.font,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on chosen status
			auto_chosen_phages = list()

			if self.status == 1:
				phages = self.metadata[self.metadata["Status"] != b'draft']
				for phage in phages:
					if phage["Status"] != 'draft'.encode('utf-8'):
						phageid = phage["PhageID"].decode('utf-8')
						auto_chosen_phages.append(phageid)
			else:
				phages = self.metadata
				for phage in phages:
					phageid = phage["PhageID"].decode('utf-8')
					auto_chosen_phages.append(phageid)

			# Populate auto_chosen_phages into selected list
			for phage in sorted(auto_chosen_phages):
				data = self.metadata[self.metadata["PhageID"] ==
									 phage.encode('utf-8')]
				host = data['HostStrain'][0].decode('utf-8')
				cluster = data['Cluster'][0].decode('utf-8')
				status = data['Status'][0].decode('utf-8')
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
												"the selected list first.",
										   font=controller.font)
			self.instruction_label.pack(side=LEFT, anchor=NW, fill=None,
										expand=True)
			self.instruction_frame.pack(side=TOP, anchor=NW, fill=X,
										expand=True)

			self.sort_frame = Frame(self.viewer)
			for i in range(len(sort_modes)):
				temp_radio = Radiobutton(master=self.sort_frame,
										 variable=self.sort_mode,
										 value=i,
										 font=controller.font,
										 text=sort_modes[i])
				temp_radio.pack(side=TOP, anchor=W, fill=None, expand=True)

			sort_button = Button(master=self.sort_frame,
								 text="Sort",
								 font=controller.font,
								 command=lambda: self.sort(
									 mode=self.sort_mode.get()))
			sort_button.pack(side=TOP, anchor=W, fill=None, expand=True)
			self.sort_frame.pack(side=TOP, anchor=N, fill=X, expand=True)

			# Build a frame on the left that will house available phage listbox
			self.selection_frame = Frame(self.viewer)

			# Build a left Listbox frame that will display the available phages
			self.available_frame = Frame(self.selection_frame)
			self.available_label = Label(self.available_frame,
										 text="Available Phages",
										 font=controller.font)
			self.available_label.pack(side=TOP, anchor=N, fill=None,
									  expand=True)
			self.available_list = Listbox(self.available_frame, width=40,
										  height=30, font=controller.font,
										  selectmode=EXTENDED)

			for phage in self.metadata:
				phageid = phage["PhageID"].decode("utf-8")
				host = phage["HostStrain"].decode("utf-8")
				cluster = phage["Cluster"].decode("utf-8")
				status = phage["Status"].decode("utf-8")
				add = "\t({}, {}, {})".format(host, cluster, status)
				display = "".join(["{:<20}".format(phageid), add])
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
									 font=controller.font,
									 command=self.add)
			self.add_button.pack(side=TOP, anchor=CENTER, fill=None,
								 expand=True)
			self.remove_button = Button(self.middle_button_frame,
										text="<< Remove from Selection",
										font=controller.font,
										command=self.remove)
			self.remove_button.pack(side=TOP, anchor=CENTER, fill=None,
									expand=True)

			self.middle_button_frame.pack(side=LEFT, anchor=CENTER,
										  fill=None, expand=True)

			# Build a frame on the right that will house the selected phage
			# listbox
			self.selected_frame = Frame(self.selection_frame)
			self.selected_label = Label(self.selected_frame,
										text="Selected Phages",
										font=controller.font)
			self.selected_label.pack(side=TOP, anchor=N, fill=None,
									 expand=True)
			self.selected_list = Listbox(self.selected_frame, width=40,
										 font=controller.font,
										 height=30, selectmode=EXTENDED)

			# Auto-select phages based on random and chosen status
			auto_chosen_phages = list()

			if self.status == 1:
				phages = self.metadata[self.metadata["Status"] != b'draft']
				for phage in phages:
					if phage["Status"] != 'draft'.encode('utf-8'):
						phageid = phage["PhageID"].decode('utf-8')
						auto_chosen_phages.append(phageid)
			else:
				phages = self.metadata
				for phage in phages:
					phageid = phage["PhageID"].decode('utf-8')
					auto_chosen_phages.append(phageid)

			available_indices = range(0, len(auto_chosen_phages))
			indices = random.sample(available_indices, int(len(
				available_indices)/5))
			indices.sort()
			for index in indices:
				phage = auto_chosen_phages[index]
				data = self.metadata[self.metadata["PhageID"] ==
									 phage.encode('utf-8')]
				host = data["HostStrain"][0].decode('utf-8')
				cluster = data["Cluster"][0].decode('utf-8')
				status = data["Status"][0].decode('utf-8')
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
								  font=controller.font,
								  command=self.back)
		self.back_button.pack(side=LEFT, anchor=SW, fill=None, expand=True)
		self.next_button = Button(self.bottom_button_frame,
								  text="Make Nexus File",
								  font=controller.font,
								  command=self.make_nexus)
		self.next_button.pack(side=LEFT, anchor=SE, fill=None, expand=True)
		self.bottom_button_frame.pack(side=BOTTOM, anchor=S, fill=X,
									  expand=True)

		self.viewer.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=True)

	def sort(self, mode):
		# Empty the available list
		while len(self.available_list.get(0, END)) > 0:
			self.available_list.delete(END)

		# Get selected list and then empty it
		selected_phages = list()
		selection = self.selected_list.get(0, END)
		for select in selection:
			selected_phages.append(select.split()[0])
		while len(self.selected_list.get(0, END)) > 0:
			self.selected_list.delete(END)

		# Sort by PhageID
		if mode == 0:
			self.metadata = np.sort(self.metadata, order=["PhageID"])

		# Sort by HostStrain, then PhageID
		elif mode == 1:
			self.metadata = np.sort(self.metadata, order=["HostStrain",
														  "PhageID"])

		# Sort by Cluster, then PhageID
		elif mode == 2:
			self.metadata = np.sort(self.metadata, order=["Cluster",
														  "HostStrain",
														  "PhageID"])

		self.phages = list(self.metadata["PhageID"])
		self.phages = [phage.decode('utf-8') for phage in self.phages]

		for phage in self.metadata:
			phageid = phage["PhageID"].decode('utf-8')
			host = phage["HostStrain"].decode('utf-8')
			cluster = phage["Cluster"].decode('utf-8')
			status = phage["Status"].decode('utf-8')
			add = "\t({}, {}, {})".format(host, cluster, status)
			display = "".join(["{:<20}".format(phageid), "{:<40}".format(
				add)])
			self.available_list.insert(END, display)

			if phageid in selected_phages:
				self.selected_list.insert(END, display)

	def add(self):
		sel = self.available_list.curselection()
		for i in sel:
			add_name = self.phages[i]
			print(i, add_name)
			if add_name not in self.selected_list.get(0, END):
				data = self.metadata[self.metadata["PhageID"] ==
									 add_name.encode('utf-8')]
				host = data["HostStrain"][0].decode('utf-8')
				cluster = data["Cluster"][0].decode('utf-8')
				status = data["Status"][0].decode('utf-8')
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
