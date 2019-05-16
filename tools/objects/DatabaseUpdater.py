import pymysql as pms
import requests
import os
from tkinter.messagebox import showinfo
from tkinter.messagebox import askyesno

from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from tools.scripts.misc_functions import validate_mysql_credentials


class DatabaseUpdater:
	def __init__(self, controller, database):
		"""
		Checks to see whether a local database name exists at the
		webfactional server, and what that remote version number is.
		If remote version > local version, prompt asking whether to
		update.  If yes, download the .sql file, overwrite the local
		database, and delete the .sql file.  If no, continue using
		the out of data version. If remote version <= local version,
		showinfo local version is up to date.
		:param controller: reference to the main window controller
		:param database: MySQL database to be checked
		"""
		self.controller = controller

		self.username = None
		self.password = None
		self.credentials_valid = False

		self.database = database

		self.remote_address = \
			"http://phamerator.webfactional.com/databases_Hatfull"

		self.local_version = None
		self.remote_version = None

	def get_root_pw(self):
		"""
		Checks that the username and password are valid - if they are
		not, prompts the user it input admin username and password.
		"""
		while not self.credentials_valid:
			self.username, self.password = validate_mysql_credentials(
				self.username, self.password)
			if self.username is not None and self.password is not None:
				self.credentials_valid = True
			else:
				GetMySQLUserPassDialog(self).wait_window()
		return

	def get_local_version(self):
		"""
		Logs into MySQL using the validated username and password, and
		selects Version from the version table.
		:return: local_version
		"""
		try:
			con = pms.connect("localhost", self.username, self.password,
							  self.database)
			cur = con.cursor()
			cur.execute("SELECT Version FROM version")
			local_version = int(cur.fetchall()[0][0])
			con.close()
		except pms.err.DatabaseError:
			local_version = 0
		self.local_version = local_version
		return

	def get_remote_version(self):
		"""
		Attempts to retrieve the database's remote version number.
		:return: remote_version
		"""
		try:
			response = requests.get("{}/{}.version".format(
				self.remote_address, self.database))
			if response.status_code == 404:
				showinfo(title="404 Error",
						 message="The default server address doesn't appear "
								 "to have a database called {}".format(
							 self.database))
				remote_version = 0
			elif response.status_code == 200:
				remote_version = int(response.text.rstrip("\n"))
			else:
				showinfo(title="Unknown Error",
						 message="An unknown error has occurred while "
								 "checking for database updates.")
				remote_version = 0
		except requests.exceptions.ConnectionError:
			remote_version = 0
		self.remote_version = remote_version
		return

	def update_db(self):
		"""
		Attempts to retrieve and import the remote .sql file if the
		local version is lower than the remote version. Otherwise,
		indicates that no updates are available.
		"""
		check_updates = askyesno(title="Check for Updates?",
								 message="Do you want to check the Hatfull "
										 "server for the newest version of "
										 "{}?".format(self.database))
		if check_updates is False:
			return

		self.get_root_pw()
		self.get_local_version()
		self.get_remote_version()
		print(self.local_version, self.remote_version)
		if self.local_version < self.remote_version:
			get_updates = askyesno(title="Updates Available",
								   message="The Hatfull server version for "
										   "{} is higher than your local "
										   "version. Download "
										   "updates?".format(self.database))
			if get_updates is False:
				return

			try:
				response = requests.get("{}/{}.sql".format(self.remote_address,
														   self.database))
				g = open("{}.sql".format(self.database), "w")
				g.write(response.text)
				g.close()
			except requests.exceptions.ConnectionError:
				showinfo(title="Connection Error",
						 message="Failed to download updates.")
				return
			try:
				os.system("mysql -u {} --password={} {} < {}.sql".format(
					self.username, self.password, self.database,
					self.database))
				os.system("rm {}.sql".format(self.database))
			except pms.err.OperationalError:
				showinfo(title="MySQL Error",
						 message="Failed to import new database version.")
				return
			showinfo(title="Done Importing Updates",
					 message="{} is now up to date!".format(self.database))
			return
		else:
			showinfo(title="No Updates Available",
					 message="There are no updates available for {} right "
							 "now.".format(self.database))
			return
