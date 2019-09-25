import json
import os
import platform
import sys
import webbrowser
import requests
import tkinter as tk
import numpy as np

from tkinter.messagebox import showinfo, askyesnocancel

from tools.objects.MySQLConnectionHandler import MySQLConnectionHandler
from tools.objects.NexusHandler import NexusHandler
from tools.objects.DatabaseUpdater import DatabaseUpdater
from tools.scripts.misc_functions import *
from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from ui.windows.MainWindow import MainWindow
from data.constants import *

if platform.system().lower() == "darwin":
    import _cffi_backend


class MainWindowController:
    def __init__(self):
        # Load application preferences
        self.server = "http://phamerator.webfactional.com/databases_Hatfull/"
        self.font = ("Monaco", 12)

        # MySQL connection with select-only privileges
        self.anon_mysql = MySQLConnectionHandler()
        self.anon_mysql.username = DEFAULT_USER
        self.anon_mysql.password = DEFAULT_PASS
        self.anon_usable = self.validate_anon_credentials()

        # MySQL connection with all privileges
        self.admin_mysql = MySQLConnectionHandler()

        # Available to user in MySQL
        self.available_databases = list()
        self.available_hosts = list()
        self.available_clusters = list()
        self.available_phages = list()

        self.metadata = None

        # User selections
        self.runmode = None
        self.exclude_draft = False

        self.selected_database = None
        self.selected_hosts = list()
        self.selected_clusters = list()
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
        self.anon_mysql.validate_credentials()
        return self.anon_mysql.credential_status

    def validate_admin_credentials(self):
        """
        Uses the MySQLConnectionHandler's builtin method to check if
        username@'localhost' identified by 'password' is valid on the
        machine in question.
        :return: True or False
        """
        self.admin_mysql.validate_credentials()
        return self.admin_mysql.credential_status

    def get_admin_credentials(self):
        """
        Uses the GetMySQLUserPassDialog window to ask for user-input
        username and password for MySQL.
        :return:
        """
        attempts_remain = 3
        while attempts_remain > 0:
            attempts_remain -= 1
            GetMySQLUserPassDialog(controller=self,
                                   parent=self.window.root,
                                   title="MySQL Login")
            if self.validate_admin_credentials():
                return
            if attempts_remain != 0:
                showinfo(title="MySQL Login Attempt Failed",
                         message=ERROR_MESSAGES["failed_login"])
            else:
                showinfo(title="Login Attempt Maximum Reached",
                         message=ERROR_MESSAGES["max_login"])
                sys.exit(1)

    def get_mysql_dbs(self):
        """
        Uses MySQLConnectionHandler builtin method to query for the
        databases available for use by the logged-in user.
        :return:
        """
        # If the anonymous account is usable, use it
        if self.anon_usable:
            self.available_databases = get_database_names(self.anon_mysql)
        else:
            # Otherwise if the admin account is usable, use it
            if self.admin_mysql.credential_status:
                self.available_databases = get_database_names(
                    self.admin_mysql)
            # Otherwise if the admin account is unusable, get credentials
            else:
                self.get_admin_credentials()
                self.available_databases = get_database_names(
                    self.admin_mysql)

    def update_database(self):
        """
        Uses DatabaseUpdater methods to check whether updates are
        available for the selected database, and optionally download
        and apply those updates if they are available.
        :return:
        """
        self.anon_mysql.database = self.selected_database
        self.admin_mysql.database = self.selected_database
        updater = DatabaseUpdater(controller=self, handler=self.admin_mysql)
        updater.do_update_db()

    def update_available_hosts(self):
        """
        Finds all the unique hosts available in self.metadata, converts
        them to utf-8 strings, and adds them to self.available_hosts.
        :return:
        """
        for host in list(np.unique(self.metadata["HostStrain"])):
            self.available_hosts.append(host.decode("utf-8"))

    def update_available_clusters(self):
        """
        Finds all the unique clusters available in self.metadata,
        converts them to utf-8 strings, and adds them to
        self.available_clusters.
        :return:
        """
        for cluster in list(np.unique(self.metadata["Cluster"])):
            self.available_clusters.append(cluster.decode("utf-8"))

    def update_available_phages(self):
        """
        Finds all the unique phages available in self.metadata,
        converts them to utf-8 strings, and adds them to
        self.available_phages.
        :return:
        """
        for phage in list(np.unique(self.metadata["PhageID"])):
            self.available_phages.append(phage.decode("utf-8"))

    def get_phages(self):
        """
        Sends a valid mysql connection handler out to `get_metadata`
        function from `misc_functions`. `get_metadata` returns
        all metadata, which is then written to self._metadata.
        :return:
        """
        # Use anonymous account if possible, otherwise use admin
        if self.anon_usable:
            self.anon_mysql.database = self.selected_database
            self.metadata = get_phages(self.anon_mysql)
        else:
            self.admin_mysql.database = self.selected_database
            self.metadata = get_phages(self.admin_mysql)

        self.update_available_hosts()
        self.update_available_clusters()
        self.update_available_phages()

    def redraw_window(self, frame):
        self.window.redraw(frame=frame)

    def make_nexus(self, filename="output.nex"):
        """
        Takes user selection and queries the database for phage and
        pham data specific to that selection. Sifts through phage and
        pham data retrieved, and writes the data out in Nexus format.
        :param filename: name of the nexus file to be written.
        :return:
        """
        all_phams = list()
        phages_and_phams = dict()

        if self.anon_usable:
            handler = self.anon_mysql
        else:
            handler = self.admin_mysql

        # Populate the queue with selected phages.
        query_queue = self.selected_phages
        # While there's still something in the queue
        while len(query_queue) > 0:
            # Grab the first item in the queue and use it as this
            # query's phage.
            phage = query_queue.pop(0)
            # Results dictionary will only have 1 key at a time, but for
            # simplicity, processing is done the same as other runmodes.
            results = get_phams_by_phage(handler=handler,
                                         phage=phage)
            phages_and_phams[phage] = results
            for pham in results:
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
                                    message=ERROR_MESSAGES["app_upd_avail"])
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
                                  default=tk.messagebox.CANCEL)
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
