# Links to repository pages at github
GIT_WIKI = "https://github.com/chg60/phamnexus/wiki/"
GIT_ISSUES = "https://github.com/chg60/phamnexus/issues/new"
GIT_MASTER = "https://gihub.com/chg60/phamnexus"
GIT_VERSION = "https://raw.github.com/chg60/phamnexus/master/data/version.txt"
GIT_APP = "https://raw.github.com/chg60/phamnexus/master/MacOS-version{}.zip"

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
                  "updates_avail": "Updates are available. Would you like "
                                   "to download them now?",
                  "no_upd_avail":  "There are no updates available at this "
                                   "time.",
                  "download_done": "The updated application has been "
                                   "downloaded. To apply updates, quit and "
                                   "drag the new version from your Downloads "
                                   "folder to your Applications folder.",

                  }



# Several databases come with MySQL but are not Phamerator databases.
# NOTE: Any other databases to ignore can be added to the code here.
IGNORE_DBS = ("information_schema", "mysql", "performance_schema",
              "sys")
