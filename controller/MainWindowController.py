import json
import os
import platform
import sys
import tkinter as tk
import tkinter.messagebox
from subprocess import Popen
from tkinter.messagebox import showinfo, askyesnocancel

import requests

from tools.scripts.misc_functions import *
from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from ui.windows.MainWindow import MainWindow


class MainWindowController:
	def __init__(self):
		# Error messages
		try:
			with open("errors.json", "r") as fh:
				self.messages = json.load(fh)
		except FileNotFoundError:
			with open("data/errors.json", "r") as fh:
				self.messages = json.load(fh)

		# MySQL database read-only credentials
		self.username = "anonymous"
		self.password = "anonymous"
		self.u_p_valid = False

		# MySQL databases available for use
		self.available_databases = []
		self.selected_database = None

		# Remember user options for this session
		self.write_file = None
		self.runmode = None
		self.final_status = None

		self.available_hosts = []
		self.selected_hosts = []

		self.available_clusters = []
		self.selected_clusters = []

		self.available_phages = []
		self.selected_phages = []

		# Launch main window
		self.window = MainWindow(controller=self)
		self.window.launch()

	def validate_credentials(self):
		# While u_p_valid flag is set to False
		while not self.u_p_valid:
			# Username and password remain unchanged if valid, but get set
			# to None and None if invalid.
			self.username, self.password = validate_mysql_credentials(
				self.username, self.password)
			# If username and password are not None, we know the credentials
			# are valid, and can set the u_p_valid flag to True, breaking
			# out of the while loop.
			if self.username is not None and self.password is not None:
				self.u_p_valid = True
			# Otherwise, we need to retrieve valid credentials to test,
			# and remain in the loop.
			else:
				GetMySQLUserPassDialog(self).wait_window()

	def get_mysql_dbs(self):
		# If we already did this, there's no need to repeat it, so if we 
		# have databases in local_databases, we'll return to break out of 
		# this function.
		if len(self.available_databases) != 0:
			return
		
		# Several databases come with MySQL but are not Phamerator databases.
		# NOTE: Any other databases to ignore can be added to the code here.
		ignore_dbs = ["information_schema", "mysql", "performance_schema",
					  "sys"]

		# Validate credentials, because we can't log in to MySQL and query 
		# for a list of available databases without valid credentials.
		self.validate_credentials()

		all_dbs = get_database_names(self.username, self.password)
		for database in all_dbs:
			if database not in ignore_dbs:
				self.available_databases.append(database)
		return

	def redraw(self, frame):
		self.window.redraw(frame=frame)

	def make_nexus(self, filename):
		"""
		Takes user selection and queries the database for phage and
		pham data specific to that selection. Sifts through phage and
		pham data retrieved, and writes the data out in Nexus format.
		:param filename: name of the nexus file to be written.
		:return:
		"""
		all_phams = []
		phages_and_phams = {}
		phages_and_nex_strings = {}

		# If runmode is 0, select phage/pham data based on selected hosts.
		if self.runmode == 0:
			# Populate the queue with selected hosts
			query_queue = self.selected_hosts
			# While there's still something in the queue
			while len(query_queue) > 0:
				# Grab the first item in the queue and use it as this
				# query's host.
				host = query_queue.pop(0)
				# Results dictionary will have [1, n] keys at a time,
				# so process with a for loop.
				results = get_phams_by_host(username=self.username,
											password=self.password,
											database=self.selected_database,
											host=host,
											status=self.final_status)
				for phageid in results.keys():
					phams = results[phageid]
					phages_and_phams[phageid] = phams
					for pham in phams:
						all_phams.append(pham)

		# If runmode is 1, select phage/pham data based on selected clusters.
		elif self.runmode == 1:
			# Populate the queue with selected clusters.
			query_queue = self.selected_clusters
			# While there's still something in the queue
			while len(query_queue) > 0:
				# Grab the first item in the queue and use it as this
				# query's cluster.
				cluster = query_queue.pop(0)
				# Results dictionary will have [1, n] keys at a time,
				# so process with a for loop.
				results = get_phams_by_cluster(username=self.username,
											   password=self.password,
											   database=self.selected_database,
											   cluster=cluster,
											   status=self.final_status)
				for phageid in results.keys():
					phams = results[phageid]
					phages_and_phams[phageid] = phams
					for pham in phams:
						all_phams.append(pham)

		# If runmode is 2, 3, or 4, select phage/pham data based on selected
		# phages.
		elif self.runmode == 2 or self.runmode == 3 or self.runmode == 4:
			# Populate the queue with selected phages.
			query_queue = self.selected_phages
			# While there's still something in the queue
			while len(query_queue) > 0:
				# Grab the first item in the queue and use it as this
				# query's phage.
				phage = query_queue.pop(0)
				# Results dictionary will only have 1 key at a time, but for
				# simplicity, processing is done the same as other runmodes.
				results = get_phams_by_phage(username=self.username,
											 password=self.password,
											 database=self.selected_database,
											 phage=phage)
				for phageid in results.keys():
					phams = results[phageid]
					phages_and_phams[phageid] = phams
					for pham in phams:
						all_phams.append(pham)

		# List of all_phams is non-unique; fix that, and sort the list.
		all_phams = sorted(list(set(all_phams)))

		print("{} phages have {} phams".format(len(phages_and_phams),
											   len(all_phams)))

		# Create the Nexus strings for each phage. This is the bottleneck in
		# the whole process
		for phage in phages_and_phams.keys():
			phams = phages_and_phams[phage]
			nex_list = []
			for pham in all_phams:
				if pham in phams:
					nex_list.append("1")
				else:
					nex_list.append("0")
			phages_and_nex_strings[phage] = "".join(nex_list)

		print("Created the nexus strings")

		# Create the nexus file.
		f = open(filename, "w")

		# Write out header information.
		f.write("#NEXUS\n")
		f.write("BEGIN TAXA;\n")
		f.write("\tdimensions ntax={};\n".format(len(phages_and_phams.keys())))
		f.write("\ttaxlabels {};\n".format(" ".join(phages_and_phams.keys())))
		f.write("END;\n")
		f.write("BEGIN CHARACTERS;\n")
		f.write("\tdimensions nchar={};\n".format(len(all_phams)))
		f.write("\tformat datatype=standard missing=? gap=- matchchar=. "
				"interleave;\n")
		f.write("\tmatrix\n")

		indices = range(0, len(all_phams), 100)
		# print(indices[0:])
		for i in range(len(indices)-1):
			start = indices[i]
			end = indices[i+1]
			for phageid in phages_and_phams.keys():
				string = phages_and_nex_strings[phageid][start:end]
				line = '{:<27}\t{:>100}\n'.format(phageid, string)
				f.write(line)
			f.write("\n")
		start = indices[-1]

		for phageid in phages_and_phams.keys():
			string = phages_and_nex_strings[phageid][start:]
			line = '{:<27}\t{}\n'.format(phageid, string)
			f.write(line)
		f.write("\n;\nend;\n")
		f.close()

		showinfo(message="Your nexus file has been saved to {}".format(
			filename))
		return

	def check_updates(self):
		# local version
		try:
			f = open("version.txt", "r")
		except FileNotFoundError:
			f = open("data/version.txt", "r")
		local_version = f.readline()
		f.close()

		# remote version
		response = requests.get(
			"https://raw.github.com/chg60/phamnexus/master/data/version.txt")
		remote_version = response.text.rstrip("\n")
		if remote_version > local_version:
			update = askyesnocancel(title="Updates Available",
									message="Updates are available. Would you "
											"like to download them now? This "
											"should take a few seconds, and "
											"the new application will be found"
											" in your Downloads folder.")
		else:
			showinfo(title="No Updates Available",
					 message="There are no updates available at this time.")
			update = False
		if update is True:
			if platform.system().lower() == "darwin":
				os.system("cd ~/Downloads/; curl -LO "
						  "https://raw.github.com/chg60/phamnexus/master/"
						  "MacOS-version{}.zip; unzip MacOS-version{}.zip; "
						  "rm MacOS-version{}.zip".format(remote_version,
														  remote_version,
														  remote_version))
				showinfo(title="Download Complete",
						 message=self.messages["Download Complete"])
			else:
				showinfo("This feature hasn't yet been completed for your "
						 "system.  Updates can be retrieved by downloading "
						 "the updated git repository ("
						 "https://github.com/chg60/phamnexus.git) to your "
						 "machine.")

	def documentation(self):
		if platform.system().lower() == "darwin":
			try:
				Popen(args=["open", "-a", "Preview", "Documentation.pdf"])
			except:
				Popen(args=["open", "-a", "Preview", "data/Documentation.pdf"])
		elif platform.system().lower() == "linux":
			Popen(args=["xdg-open", "data/Documentation.pdf"])

	def report_bug(self):
		showinfo(title="Bug Report Info",
				 message="Please email Christian at chg60@pitt.edu with a "
						 "detailed description of the bug.  Include the "
						 "button(s) pressed to get the behavior, what you "
						 "were expecting to happen, and what actually "
						 "happened.")

	def quit(self):
		response = tk.messagebox.askyesnocancel(title="Really quit?",
												message="Are you sure you "
														"want to quit?",
												default=tk.messagebox.CANCEL)
		if response is None or response is False:
			return

		self.window.destroy()
		sys.exit(0)

