import json
import os
import platform
import sys
import webbrowser
import requests
import tkinter as tk

from tkinter.messagebox import showinfo, askyesnocancel

from tools.objects.MySQLConnectionHandler import MySQLConnectionHandler
from tools.objects.NexusHandler import NexusHandler
from tools.scripts.misc_functions import *
from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from ui.windows.MainWindow import MainWindow
from data.constants import *

if platform.system().lower() == "darwin":
    import _cffi_backend


class MainWindowController:
    def __init__(self):
        # Load application preferences
        self._server = "http://phamerator.webfactional.com/databases_Hatfull/"
        self._font_family = "Helvetica"
        self._font_size = 14

        # MySQL connection with select-only privileges
        self._anon_mysql = MySQLConnectionHandler()
        self._anon_mysql.username = "anonymous"
        self._anon_mysql.password = "anonymous"
        self._anon_usable = self.validate_anon_credentials()

        # MySQL connection with all privileges
        self._admin_mysql = MySQLConnectionHandler()

        # Available to user in MySQL
        self._available_databases = list()
        self._available_hosts = list()
        self._available_clusters = list()
        self._available_subclusters = list()
        self._available_phages = list()

        self._metadata = None

        # User selections
        self.runmode = None
        self.exclude_draft = False
        self.selected_database = None
        self.selected_hosts = list()
        self.selected_clusters = list()
        self.selected_subclusters = list()
        self.selected_phages = list()

        # Output file
        self.output_file = None

        # Initialize and launch main window
        self.window = MainWindow(controller=self)
        self.window.launch()

    def validate_anon_credentials(self):
        """
        Uses the MySQLConnectionHandler's builtin method to check if
        'anonymous'@'localhost' identified by 'anonymous' is valid on
        the machine in question.
        :return: True or False
        """
        self._anon_mysql.validate_credentials()
        return self._anon_mysql.credential_status

    def validate_admin_credentials(self):
        """
        Uses the MySQLConnectionHandler's builtin method to check if
        username@'localhost' identified by 'password' is valid on the
        machine in question.
        :return: True or False
        """
        self._admin_mysql.validate_credentials()
        return self._admin_mysql.credential_status

    def get_admin_credentials(self):
        """
        Uses the GetMySQLUserPassDialog window to ask for user-input
        username and password for MySQL.
        :return:
        """
        attempts_remain = 3
        while attempts_remain > 0:
            attempts_remain -= 1
            self._admin_mysql.username, self._admin_mysql.password = \
                GetMySQLUserPassDialog(self).wait_window()
            if self.validate_admin_credentials():
                return
            if attempts_remain != 0:
                showinfo(title="MySQL Login Attempt Failed",
                         message=ERROR_MESSAGES["failed_login"])
            else:
                showinfo(title="Login Attempt Maximum Reached",
                         message=ERROR_MESSAGES["max_login"])
                sys.exit(1)

    # TODO: is this necessary?
    def refresh_available_hosts(self):
        self._available_hosts = sorted(list(set(self._metadata["HostStrain"])))

    # TODO: is this necessary?
    def refresh_available_clusters(self):
        self._available_clusters = sorted(list(set(self._metadata["Cluster"])))

    # TODO: is this necessary?
    def refresh_available_phages(self):
        self._available_phages = sorted(list(set(self._metadata["PhageID"])))

    def get_mysql_dbs(self):
        """
        Uses MySQLConnectionHandler builtin method to query for the
        databases available for use by the logged-in user.
        :return:
        """
        # If the anonymous account is usable, use it
        if self._anon_usable:
            self._available_databases = get_database_names(
                self._anon_mysql, IGNORE_DBS)
        else:
            # Otherwise if the admin account is usable, use it
            if self._admin_mysql.credential_status:
                self._available_databases = get_database_names(
                    self._admin_mysql, IGNORE_DBS)
            # Otherwise if the admin account is unusable, get credentials
            else:
                self.get_admin_credentials()
                self._available_databases = get_database_names(
                    self._admin_mysql, IGNORE_DBS)

    def get_metadata(self):
        """
        Sends a valid mysql connection handler out to `get_metadata`
        function from `misc_functions`. `get_metadata` returns
        all metadata, which is then written to self._metadata.
        :return:
        """
        # Use anonymous account if possible, otherwise use admin
        if self._anon_usable:
            self._anon_mysql.database = self.selected_database
            self._metadata = get_metadata(self._anon_mysql)
        else:
            self._admin_mysql.database = self.selected_database
            self._metadata = get_metadata(self._admin_mysql)

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
        showinfo(title="Nexus file complete",
                 message=ERROR_MESSAGES["nexus_done"])

    def check_updates(self):
        # local version
        try:
            f = open("version.txt", "r")
        except FileNotFoundError:
            f = open("data/version.txt", "r")
        local_version = f.readline()
        f.close()

        # remote version
        response = requests.get(GIT_VERSION)
        remote_version = response.text.rstrip("\n")
        if remote_version > local_version:
            update = askyesnocancel(title="Updates Available",
                                    message=ERROR_MESSAGES["updates_avail"])
        else:
            showinfo(title="No Updates Available",
                     message=ERROR_MESSAGES["no_upd_avail"])
            update = False
        if update is True:
            if platform.system().lower() == "darwin":
                status = update_mac_application(remote_version)
                if status == 0:
                    showinfo(title="Download Complete",
                             message=ERROR_MESSAGES["download_done"])
            else:

                try_git = askyesnocancel(title="Update with Git?",
                                         message="Would you like updates to "
                                                 "be attempted using git?",
                                         default=tk.messagebox.CANCEL)
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
        """
        Asks for confirmation to open github issues page in browser.
        If cancel or no, do nothing. Else, open new tab in browser.
        :return:
        """
        # Ask for user input
        response = askyesnocancel(title="Open Browser Window?",
                                  message="Do you want to open a browser "
                                          "window where bug reports and "
                                          "feature requests can be made?",
                                  default=tk.messagebox.CANCEL)

        # If they said no or cance, do nothing
        if response is None or response is False:
            return

        # Otherwise, try to open tab in browser
        try:
            webbrowser.open_new_tab(
                "https://github.com/chg60/phamnexus/issues/new")
        except webbrowser.Error:
            showinfo(title="Failed To Open Browser",
                     message="Unable to open a browser window. Issues can be "
                             "submitted at "
                             "https://github.com/chg60/phamnexus/issues/new. "
                             "Guidelines can be found at "
                             ""
                             "Recommendations-and-Bug-Reports.")

    def quit(self):
        """
        Asks user to verify the quit action. If cancel or no, return
        and do nothing. If yes, destroy window and exit program.
        :return:
        """
        # Ask for user input
        response = askyesnocancel(title="Quit PhamNexus",
                                  message="Are you sure you want to quit?",
                                  default=tk.messagebox.CANCEL)

        # If they said no or cancel, do nothing
        if not response:
            return

        # Otherwise, quit
        self.window.destroy()
        sys.exit(0)
