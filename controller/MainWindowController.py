import tkinter as tk
import tkinter.messagebox
import sys
import platform
import requests
import os

from subprocess import Popen
from tkinter.messagebox import showinfo

from ui.windows.MainWindow import MainWindow
from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from tools.scripts.misc_functions import *


class MainWindowController:
	def __init__(self):
		# MySQL database read-only credentials
		self.mysql_read_u = "anonymous"
		self.mysql_read_p = "anonymous"
		self.u_p_valid = False

		# MySQL databases available for use
		self.local_databases = []

		# Remember user options for this session
		self.write_file = None
		self.runmode_selection = None
		self.database_selection = None

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
		while not self.u_p_valid:
			self.mysql_read_u, self.mysql_read_p = \
				validate_mysql_credentials(self.mysql_read_u,
										   self.mysql_read_p)
			if self.mysql_read_u is not None and self.mysql_read_p is not None:
				self.u_p_valid = True
			else:
				GetMySQLUserPassDialog(self).wait_window()

	def get_mysql_dbs(self):
		# If we already did this, there's no need to repeat it
		if len(self.local_databases) != 0:
			return
		# Databases that come with MySQL and should be ignored
		ignore_dbs = ["information_schema", "mysql", "performance_schema",
					  "sys"]

		# Validate read-only credentials
		self.validate_credentials()

		all_dbs = get_database_names(self.mysql_read_u, self.mysql_read_p)
		for database in all_dbs:
			if database not in ignore_dbs:
				self.local_databases.append(database)
		return

	def redraw(self, frame):
		self.window.redraw(frame=frame)

	def make_nexus(self, filename):
		all_phageids = []
		all_phams = []
		phages_and_phams = {}
		phages_and_nex_strings = {}
		if self.runmode_selection == 0:
			for host in self.selected_hosts:
				phages = get_database_phages(username=self.mysql_read_u,
											 password=self.mysql_read_p,
											 database=self.database_selection,
											 host=host)
				for phage in phages:
					all_phageids.append(phage)
				print("Got all the {} phages".format(host))

		elif self.runmode_selection == 1:
			print(self.selected_clusters)
			for cluster in self.selected_clusters:
				phages = get_database_phages(username=self.mysql_read_u,
											 password=self.mysql_read_p,
											 database=self.database_selection,
											 cluster=cluster)
				for phage in phages:
					all_phageids.append(phage)
				print("Got all the {} phages".format(str(cluster)))

		elif self.runmode_selection == 2 or self.runmode_selection == 3 or \
				self.runmode_selection == 4:
			all_phageids = self.selected_phages

		# Get phams for the phages
		for phageid in all_phageids:
			phams = get_phams(username=self.mysql_read_u,
							  password=self.mysql_read_p,
							  database=self.database_selection,
							  phage=phageid)
			phages_and_phams[phageid] = phams
			for pham in phams:
				all_phams.append(pham)
			print("Got all the phams for {}".format(phageid))

		# Create the nexus strings
		all_phams = sorted(list(set(all_phams)))
		# print(len(all_phams))
		for phage in phages_and_phams.keys():
			phage_phams = phages_and_phams[phage]
			nex_string = ""
			for pham in all_phams:
				if pham in phage_phams:
					nex_string = nex_string + "1"
				else:
					nex_string = nex_string + "0"
			phages_and_nex_strings[phage] = nex_string

		# print("writing the nexus file")
		# Write the nexus file
		f = open(filename, "w")
		f.write("#NEXUS\n\nbegin taxa;\n\tdimensions ntax={};\n"
				"TAXLABELS\n\n".format(len(all_phageids)))
		for phageid in all_phageids:
			f.write(phageid + "\n")
		f.write(";\nEND;\n\n")
		f.write("begin characters;\n	dimensions nchar={};\n".format(len(
			all_phams)))
		f.write("\tFORMAT\n\t	datatype=standard\n\t	missing=?\n\t	"
				"gap=-\n\t	matchchar=.\n\t	Interleave\n\t	;\n\nMATRIX\n\n")
		indices = range(0, len(all_phams), 100)
		print(indices)
		for i in range(len(indices)-1):
			start = indices[i]
			end = indices[i+1]
			for phageid in all_phageids:
				string = phages_and_nex_strings[phageid][start:end]
				line = '{:<27}   {:>100}\n'.format(phageid, string)
				f.write(line)
			f.write("\n")
		start = indices[-1]
		for phageid in all_phageids:
			string = phages_and_nex_strings[phageid][start:]
			line = '{:<27}   {}\n'.format(phageid, string)
			f.write(line)
		f.write("\n;\nend;\n")
		f.close()

		showinfo(message="Your nexus file has been saved to {}".format(
			filename))
		return

	def check_updates(self):
		# local version
		f = open("version.txt", "r")
		local_version = f.readline()
		f.close()

		# remote version
		response = requests.get(
			"https://raw.github.com/chg60/phamnexus/master/data/version.txt")
		remote_version = response.text.rstrip("\n")
		if remote_version > local_version:
			update = tkinter.messagebox.askyesnocancel(
				title="Updates Available",
				message="Updates are available. Would you like to download them now? This should take a few seconds, and the new application will be found in your Downloads folder.")
		else:
			tkinter.messagebox.showinfo(title="No Updates Available",
										message="There are no updates available at this time.")
			update = False
		if update is True:
			if platform.system().lower() == "darwin":
				os.system("cd ~/Downloads/; curl -LO "
						  "https://raw.github.com/chg60/phamnexus/master/"
						  "MacOSX-version{}.zip; unzip MacOSX-version{}.zip; "
						  "rm MacOSX-version{}.zip".format(remote_version,
														   remote_version,
														   remote_version))
			elif platform.system().lower() == "linux":
				os.system("cd ~/Downloads/; curl -LO "
						  "https://raw.github.com/chg60/phamnexus/master"
						  "/Linux-version{}.zip; unzip Linux-version{}.zip; "
						  "rm Linux-version{}.zip".format(remote_version,
														  remote_version,
														  remote_version))
			showinfo(title="Program Restart Required",
					 message="The updated application can be found in your "
							 "downloads folder. You'll need to manually drag "
							 "it into your Applications folder to overwrite "
							 "this version.")

	def documentation(self):
		if platform.system().lower() == "darwin":
			Popen(args=["open", "-a", "Preview", "Documentation.pdf"])
		elif platform.system().lower() == "linux":
			Popen(args=["xdg-open", "Documentation.pdf"])

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

