import os

# Links to repository pages at github
GIT_WIKI = "https://github.com/chg60/phamnexus/wiki/"
GIT_ISSUES = "https://github.com/chg60/phamnexus/issues/new"
GIT_MASTER = "https://gihub.com/chg60/phamnexus"
GIT_VERSION = "https://raw.github.com/chg60/phamnexus/master/data/version.txt"
GIT_APP = "https://raw.github.com/chg60/phamnexus/master/MacOS-version{}.zip"

# Downloads will be put in user's Downloads folder
DOWNLOAD_DIR = os.path.expanduser("~") + "/Downloads/"

# Error messages for SHOWINFO messages
ERROR_MESSAGES = {"failed_login":  "A connection to MySQL could not be "
                                   "established using the provided username "
                                   "and password. Please verify your "
                                   "credentials and try again.",
                  "max_login":     "You have reached the maximum number of "
                                   "attempts to log into MySQL. PhamNexus "
                                   "will now close.",
                  "nexus_done":    "The nexus file containing your "
                                   "selected phages and their pham "
                                   "information is done being written",
                  "app_upd_avail": "Updates are available. Would you like "
                                   "to download them now?",
                  "no_upd_avail":  "There are no updates available at this "
                                   "time.",
                  "download_done": "The updated application has been "
                                   "downloaded. To apply updates, quit and "
                                   "drag the new version from your Downloads "
                                   "folder to your Applications folder.",
                  "do_db_update":  "Do you want to check the Hatfull server "
                                   "for the newest version of {}?",
                  "skip_db_upd":   "Continuing without updating the database.",
                  "404_db_update": "The default server address doesn't appear "
                                   "to have a database called {}",
                  "unk_db_update": "An unknown error has occurred while "
                                   "checking for database updates.",
                  "db_upd_avail":  "Updates are available for database {}."
                                   "Download updates?",
                  "db_upd_failed": "Failed to update the database. The most "
                                   "likely cause is that your MySQL account "
                                   "doesn't have 'INSERT' or 'UPDATE' "
                                   "privileges on the chosen database.",
                  "db_upd_done":   "{} updates have been completed!"
                  }

# Several databases come with MySQL but are not Phamerator databases.
# NOTE: Any other databases to ignore can be added to the code here.
IGNORE_DBS = ("information_schema", "mysql", "performance_schema",
              "sys")
