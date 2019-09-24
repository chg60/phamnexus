import pymysql as pms
import requests
import os
from tkinter.messagebox import showinfo
from tkinter.messagebox import askyesno

from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from data.constants import ERROR_MESSAGES, DOWNLOAD_DIR


class DatabaseUpdater:
	def __init__(self, controller, handler):
		"""
		Checks to see whether a local database name exists at the
		webfactional server, and what that remote version number is.
		If remote version > local version, prompt asking whether to
		update.  If yes, download the .sql file, overwrite the local
		database, and delete the .sql file.  If no, continue using
		the out of data version. If remote version <= local version,
		showinfo local version is up to date.
		:param controller: reference to the main window controller
		"""
		self.controller = controller
		self.handler = handler

		self.local_version = None
		self.remote_version = None

		self.do_update = self.ask_do_update()

	def ask_do_update(self):
		"""

		:return:
		"""
		response = askyesno(title="Check for Database Updates?",
							message=ERROR_MESSAGES["do_db_update"].format(
								self.handler.db))
		return response

	def check_db_versions(self):
		"""

		:return: False by default, True if remote > local
		"""
		# If admin credentials are invalid
		if not self.validate_admin_credentials():
			# Try to get valid credentials
			self.get_admin_credentials()
		# If we're still good to update (i.e. didn't fail to get admin u/p)
		if self.do_update:
			# Get local database version
			self.local_version = self.get_local_version()
			# Get remote database version
			self.remote_version = self.get_remote_version()
			# If remote > local, return True
			if self.remote_version > self.local_version:
				return True
		# Otherwise, return False by default
		return False

	def validate_admin_credentials(self):
		"""
        Uses the MySQLConnectionHandler's builtin method to check if
        username@'localhost' identified by 'password' is valid on the
        machine in question.
        :return: True or False
        """
		self.handler.validate_credentials()
		return self.handler.credential_status

	def get_admin_credentials(self):
		"""
        Uses the GetMySQLUserPassDialog window to ask for user-input
        username and password for MySQL.
        :return:
        """
		attempts_remain = 3
		while attempts_remain > 0:
			attempts_remain -= 1
			self.handler.username, self.handler.password = \
				GetMySQLUserPassDialog(self).wait_window()
			if self.validate_admin_credentials():
				return
			if attempts_remain != 0:
				showinfo(title="MySQL Login Attempt Failed",
						 message=ERROR_MESSAGES["failed_login"])
			else:
				showinfo(title="Login Attempt Maximum Reached",
						 message=ERROR_MESSAGES["max_login"])
				showinfo(title="Skipping Database Update",
						 message=ERROR_MESSAGES["skip_db_upd"])
				self.do_update = False

	def get_local_version(self):
		"""
		Logs into MySQL using the validated username and password, and
		selects Version from the version table.
		:return: local_version
		"""
		query = "SELECT Version from version"
		try:
			self.handler.open_connection()
			local_version = int(self.handler.execute_query(query)[0]["Version"])
			self.handler.close_connection()
		except:
			local_version = 0

		return local_version

	def get_remote_version(self):
		"""
		Attempts to retrieve the database's remote version number.
		:return: remote_version
		"""
		try:
			response = requests.get("{}/{}.version".format(
				self.controller.server, self.handler.database))
			if response.status_code == 404:
				showinfo(title="404 Error",
						 message=ERROR_MESSAGES["404_db_update"].format(
							 self.handler.database))
				remote_version = 0
			elif response.status_code == 200:
				remote_version = int(response.text.rstrip("\n"))
			else:
				showinfo(title="{} Error".format(response.status_code),
						 message=ERROR_MESSAGES["unk_db_update"])
				remote_version = 0
		except requests.exceptions.ConnectionError:
			remote_version = 0

		return remote_version

	def do_update_db(self):
		"""
		Attempts to retrieve and import the remote .sql file if the
		local version is lower than the remote version. Otherwise,
		indicates that no updates are available.
		"""
		if self.do_update:
			updates_available = self.check_db_versions()
			if updates_available:
				get_updates = askyesno(title="Database Updates Available",
									   message=ERROR_MESSAGES[
										   "db_upd_avail"].format(
										   self.handler.database))
				if not get_updates:
					self.do_update = False
					showinfo(title="Skipping Database Updates",
							 message=ERROR_MESSAGES["skip_db_upd"])
			else:
				self.do_update = False
				showinfo(title="No Updates Available",
						 message=ERROR_MESSAGES["no_upd_avail"])

		if self.do_update:

			try:
				response = requests.get("{}/{}.sql".format(
					self.controller.server, self.handler.database))
				g = open("{}/{}.sql".format(DOWNLOAD_DIR,
											self.handler.database), "w")
				g.write(response.text)
				g.close()
			except requests.exceptions.ConnectionError:
				showinfo(title="Connection Error",
						 message="Failed to download updates.")
				return
			try:
				transaction = ["SOURCE {}/{}.sql".format(DOWNLOAD_DIR,
														 self.handler.database)]
				self.handler.execute_transaction(transaction)
			except pms.err.OperationalError:
				showinfo(title="MySQL Error",
						 message="Failed to import new database version.")
				return
			try:
				os.system("rm {}/{}.sql".format(DOWNLOAD_DIR,
												self.handler.database))
			except OSError:
				print("Failed to delete {}/{}.sql".format(DOWNLOAD_DIR,
					self.handler.database))

			showinfo(title="Done Importing Updates",
					 message=ERROR_MESSAGES["db_upd_done"].format(
						 self.handler.database))
			return
