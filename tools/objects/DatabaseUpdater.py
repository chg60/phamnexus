import pymysql as pms
import urllib3
import shlex
from subprocess import Popen
from tkinter.messagebox import showinfo
from tkinter.messagebox import askyesno

from ui.dialogs.GetUserPassDialog import GetMySQLUserPassDialog
from data.constants import ERROR_MESSAGES, DOWNLOAD_DIR

http_pool = urllib3.PoolManager()


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
        Ask user whether they want to look for updates, return response
        :return:
        """
        response = askyesno(title="Check for Database Updates?",
                            message=ERROR_MESSAGES["do_db_update"].format(
                                self.handler.database))
        return response

    def check_db_versions(self):
        """
        Check local and remote database versions, report if remote >
        local.
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
            GetMySQLUserPassDialog(controller=self.controller,
                                   parent=self.controller.window.root,
                                   title="MySQL Admin Login")
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
            version_url = "{}/{}.version".format(self.controller.server,
                                                 self.handler.database)
            request = http_pool.request('GET', version_url)
            if request.status == 404:
                showinfo(title="404 Error",
                         message=ERROR_MESSAGES["404_db_update"].format(
                             self.handler.database))
                remote_version = 0
            elif request.status == 200:
                remote_version = int(request.data.rstrip())
            else:
                showinfo(title="{} Error".format(request.status),
                         message=ERROR_MESSAGES["unk_db_update"])
                remote_version = 0
        except:
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
                db_url = "{}/{}.sql".format(self.controller.server,
                                            self.handler.database)

                request = http_pool.request('GET', db_url, preload_content=False)
                if request.status == 200:
                    with open("{}/{}.sql".format(DOWNLOAD_DIR, self.handler.database), "wb") as fh:
                        for chunk in request.stream(512000):
                            fh.write(chunk)
            except:
                showinfo(title="Connection Error",
                         message="Failed to download updates.")
                return
            try:
                command = "mysql -u {} -p{} -e 'DROP DATABASE {}; CREATE DATABASE {}".format(
                    self.handler.username, self.handler.password,
                    self.handler.database, self.handler.database)
                with Popen(shlex.split(command)) as proc:
                    proc.wait()

                command = "mysql -u {} -p{} {}".format(
                    self.handler.username, self.handler.password,
                    self.handler.database)
                command = shlex.split(command)
                f = open("{}/{}.sql".format(DOWNLOAD_DIR, self.handler.database))
                with Popen(args=command, stdin=f) as proc:
                    proc.wait()
                f.close()
            except pms.err.OperationalError:
                showinfo(title="MySQL Error",
                         message="Failed to import new database version.")
                return
            try:
                command = "rm {}/{}.sql".format(DOWNLOAD_DIR,
                                                self.handler.database)
                command = shlex.split(command)
                Popen(args=command).wait()
            except OSError:
                print("Failed to delete {}/{}.sql".format(DOWNLOAD_DIR,
                                                          self.handler.database))

            showinfo(title="Done Importing Updates",
                     message=ERROR_MESSAGES["db_upd_done"].format(
                         self.handler.database))
            return
