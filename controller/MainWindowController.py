import json
import os
import platform
import sys
import tkinter as tk
import tkinter.messagebox
import webbrowser

from tkinter.messagebox import showinfo, askyesnocancel

import requests
if platform.system().lower() == "darwin":
	import _cffi_backend

from tools.objects.NexusHandler import NexusHandler
from tools.scripts.misc_functions import *
from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from ui.windows.MainWindow import MainWindow


class MainWindowController:
	def __init__(self):
		# TODO load application preferences
		# TODO write function to read application preferences
		# TODO write function to save application preferences
		# TODO write dialog to modify application preferences
		# TODO write Host selection Frame
		# TODO write Cluster selection Frame

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
		self.available_databases = list()
		self.selected_database = None

		# Remember user options for this session
		self.write_file = None
		self.runmode = None
		self.final_status = None

		self.metadata = None

		self.available_hosts = list()
		self.selected_hosts = list()

		self.available_clusters = list()
		self.selected_clusters = list()

		self.available_phages = list()
		self.selected_phages = list()

		# Launch main window
		self.window = MainWindow(controller=self)
		self.window.launch()

	def set_username(self, username=None):
		self.username = username

	def set_password(self, password=None):
		self.password = password

	def set_u_p_valid(self, bool=False):
		self.u_p_valid = bool

	def set_metadata(self, dataframe):
		self.metadata = dataframe

	def refresh_available_hosts(self):
		self.available_hosts = sorted(list(set(self.metadata["HostStrain"])))

	def refresh_available_clusters(self):
		self.available_clusters = sorted(list(set(self.metadata["Cluster"])))

	def refresh_available_phages(self):
		self.available_phages = sorted(list(set(self.metadata["PhageID"])))

	def validate_credentials(self):
		# While u_p_valid flag is set to False
		while not self.u_p_valid:
			username, password = validate_mysql_credentials(self.username,
															self.password)
			# Username and password will not be None if valid
			if username is not None and password is not None:
				self.set_username(username)
				self.set_password(password)
				self.set_u_p_valid(True)
			# Username and password will be None if invalid... get new
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

	def get_metadata(self):
		"""
		Connects to MySQL using verified username, password, and a database
		and queries for PhageID, HostStrain, Cluster, status from phage
		table. Creates a pandas DataFrame object from the results for
		simpler data handling on the backend of the application.
		"""
		# Initialize variables to use with MySQL
		username = self.username
		password = self.password
		database = self.selected_database

		# Initialize metadata storage variable
		metadata = {"PhageID": list(),
					"HostStrain": list(),
					"Cluster": list(),
					"Status": list()}

		# Try executing the query
		try:
			query = "SELECT PhageID, HostStrain, Cluster, status FROM phage"
			connection = pms.connect("localhost", username, password, database)
			cursor = connection.cursor()
			cursor.execute(query)
			results = cursor.fetchall()
			connection.close()
			for result in results:
				if result[2] == "UNK":
					metadata["PhageID"].append(result[0])
					metadata["HostStrain"].append(result[1])
					metadata["Cluster"].append("Unclustered")
					metadata["Status"].append(result[3])
				elif result[2] is None:
					metadata["PhageID"].append(result[0])
					metadata["HostStrain"].append(result[1])
					metadata["Cluster"].append("Singleton")
					metadata["Status"].append(result[3])
				else:
					metadata["PhageID"].append(result[0])
					metadata["HostStrain"].append(result[1])
					metadata["Cluster"].append(result[2])
					metadata["Status"].append(result[3])

		# If anything fails with MySQL, return an empty initialized dataframe
		except pms.err.Error as err:
			print(err)
			metadata = {"PhageID": list(), "HostStrain": list(),
						"Cluster": list(), "Status": list()}

		self.set_metadata(metadata)
		self.refresh_available_hosts()
		self.refresh_available_clusters()
		self.refresh_available_phages()
		return

	def redraw_window(self, frame):
		self.window.redraw(frame=frame)

	def make_nexus(self, filename):
		"""
		Takes user selection and queries the database for phage and
		pham data specific to that selection. Sifts through phage and
		pham data retrieved, and writes the data out in Nexus format.
		:param filename: name of the nexus file to be written.
		:return:
		"""
		all_phams = list()
		phages_and_phams = dict()

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

		# Create the Nexus strings
		nexus_handler = NexusHandler(phages_and_phams, all_phams, filename)
		nexus_handler.write_nexus_file()

		# Cleanup the handler in case someone runs the program multiple ways
		# in a row
		del nexus_handler

		# Show message so user knows their job is done
		showinfo("Nexus file complete", "The nexus file containing your "
										"selected phages and their pham "
										"information is done being written")

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
											"like to download them now?")
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
				try_git = askyesnocancel(title="Update with Git?",
										 message="Would you like updates to "
												 "be attempted using git?",
										 default=tkinter.messagebox.CANCEL)
				if try_git is None:
					return
				elif try_git is False:
					try_manual = askyesnocancel(title="Update Manually?",
												message="Would you like to "
														"download updates "
														"manually?")
					if try_manual is None or try_manual is False:
						return
					else:
						try:
							webbrowser.open_new_tab(
								"https://github.com/chg60/phamnexus")
						except webbrowser.Error:
							showinfo(title="Failed To Open Browser",
									 message="Unable to open a browser "
											 "window. The repository "
											 "can be downloaded from "
											 "https://github.com/chg60/phamnexus")

				elif try_git is True:
					try:
						os.system("git remote update; git pull")
						showinfo(title="Updates Downloaded",
								 message="Updates were successfully "
										 "downloaded. Close application and "
										 "restart it to apply updates.")
					except OSError:
						showinfo(title="Update Failure",
								 message="Updates couldn't be retrieved "
										 "automatically.")
						try_manual = askyesnocancel(title="Update Manually?",
													message="Would you like "
															"to download "
															"updates "
															"manually?")
						if try_manual is None or try_manual is False:
							return
						else:
							try:
								webbrowser.open_new_tab(
									"https://github.com/chg60/phamnexus")
							except webbrowser.Error:
								showinfo(title="Failed To Open Browser",
										 message="Unable to open a browser "
												 "window. The repository "
												 "can be downloaded from "
												 "https://github.com/chg60/phamnexus")
		return

	def documentation(self):
		response = askyesnocancel(title="Open Browser Window?",
								  message="Do you want to launch this "
										  "program's documentation in a "
										  "web browser window?",
								  default=tkinter.messagebox.CANCEL)
		if response is None or response is False:
			return

		try:
			webbrowser.open_new_tab("https://github.com/chg60/phamnexus/wiki")
		except webbrowser.Error:
			showinfo(title="Failed To Open Browser",
					 message="Unable to open a browser window. Documentation "
							 "can be found at "
							 "https://github.com/chg60/phamnexus/wiki.")

	def report_bug(self):
		response = askyesnocancel(title="Open Browser Window?",
								  message="Do you want to open a browser "
										  "window where bug reports and "
										  "feature requests can be made?",
								  default=tkinter.messagebox.CANCEL)
		if response is None or response is False:
			return

		try:
			webbrowser.open_new_tab(
				"https://github.com/chg60/phamnexus/issues/new")
		except webbrowser.Error:
			showinfo(title="Failed To Open Browser",
					 message="Unable to open a browser window. Issues can be "
							 "submitted at "
							 "https://github.com/chg60/phamnexus/issues/new. "
							 "Guidelines can be found at "
							 "https://github.com/chg60/phamnexus/wiki/"
							 "Recommendations-and-Bug-Reports.")

	def quit(self):
		response = tk.messagebox.askyesnocancel(title="Really quit?",
												message="Are you sure you "
														"want to quit?",
												default=tk.messagebox.CANCEL)
		if response is None or response is False:
			return

		self.window.destroy()
		sys.exit(0)
