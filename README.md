# PhameratorNexusBuilder
This program's goal is to bridge the gap between Phamerator databases and Splitstree diagrams in as user-friendly a way as possible.  The current version builds on a command line-only tool with more or less the same functionality, by wrapping it in a relatively lightweight, minimalistic GUI.  Briefly, this program serves as an interface allowing one to interact with a locally available Phamerator database, select the desired genomes for comparison, and build a Nexus file from those genomes' pham data.  The Nexus file can then be used as an input file for Splitstree4 (www.splitstree.org) to generate a dendrogram/phylogram demonstrating the relatedness of the selected genomes based on gene content similarity.


# Installation Instructions:

In order to use this application you must have a local installation of MySQL (I recommend using a version no higher than 8.0.15).  For compatibility with modern MySQL versions (8.0+), when installing MySQL you should use the newest encryption settings (not legacy).

For MacOS, a standalone application is available (MacOS-version#.#.#.zip) which when unzipped and placed in your desired Application folder will run when double-clicked like any other application.  The program can also be run from source if python3, pymysql, and requests are all installed.  Python 3 can be installed by downloading and running an installer from www.python.org/downloads/.  Pymysql and requests can be installed by opening the Mac Terminal and executing the following commands:

1.  sudo pip3 install pymysql
2.  sudo pip3 install requests

For Linux (only tested on Ubuntu 14.04+), a standalone application is not presently available, however a template .desktop file is available with the source code.  When the "Path=" line is filled in properly (input path to your downloaded copy of this repository), the .desktop file will allow users to double-click to execute the program.  This program makes use of python3, pymysql, and requests, which aren't always installed by default, so users may need to execute the following commands from the Gnome Terminal in order to be able to run the program:

1.  sudo apt-get install python3
2.  sudo apt-get install python3-pymysql
3.  sudo apt-get install python3-requests

On both MacOS and Linux, the application can be launched from the source code from the terminal by executing the following command:

python3 \_\_main__.py

# Development (bug reports and feature requests)

This program is being actively developed, albeit only by myself during my spare time.  

Bug reports can be submitted by emailing me at chg60@pitt.edu, or submitting an issue here on github.  Please include at a minimum your operating system, a description of the button(s) pressed to encounter the bug, what the buggy behavior is, and what you were expecting to happen.  I will attempt to address all bugs within 24 hours, but this may not always be possible.

Feature requests can likewise be submitted by emailing me at chg60@pitt.edu, or submitting an issue on github.  When requesting a feature, please be as specific as possible with respect to layout/behavior/etc.  I will respond to all feature requests indicating whether I'm interested in building that feature or not, and if I need additional information.  I will attempt to build all accepted features within 1 week, but this may not always be possible.
