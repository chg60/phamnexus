from data.constants import *
import os
import shlex
from subprocess import Popen
import numpy as np


def get_database_names(handler):
    """
    Connects to MySQL using MySQLConnectionHandler with verified user
    credentials and queries for all databases the user has access to.
    :param handler: MySQLConnectionHandler instance
    :return: List of databases parsed from returned results
    """
    # Initialize list to store results
    databases = list()
    # Query to give MySQLConnectionHandler
    query = "SHOW DATABASES"

    try:
        handler.open_connection()
        results = handler.execute_query(query)
        for result in results:
            if result["Database"] not in IGNORE_DBS:
                databases.append(result["Database"])
        handler.close_connection()
    except:
        handler.close_connection()

    # Sort the database list, then return it
    databases.sort()
    return databases


def get_phages(handler):
    """
    Connects to MySQL using MySQLConnectionHandler with verified user
    credentials and database and queries for all phages and their
    metadata in the chosen database.
    :param handler: MySQLConnectionHandler instance
    :return:
    """
    # Initialize phage data dictionary
    dtype = [("PhageID", "S14"), ("HostStrain", "S20"), ("Cluster", "S12"),
             ("Status", "S5")]
    values = []
    # Query for MySQL
    query = "SELECT PhageID, HostStrain, Cluster2, Subcluster2, status FROM " \
            "phage"

    try:
        handler.open_connection()
        results = handler.execute_query(query)
        for result in results:
            value = list()
            value.append(result["PhageID"])
            value.append(result["HostStrain"])
            if result["Cluster2"] is None:
                value.append("Singleton")
            elif result["Cluster2"] == "UNK":
                value.append("Unclustered")
            elif result["Subcluster2"] is None:
                value.append(result["Cluster2"])
            else:
                value.append(result["Subcluster2"])
            value.append(result["status"])
            value = tuple(value)
            values.append(value)
        handler.close_connection()
    except:
        handler.close_connection()

    phage_array = np.array(values, dtype=dtype)
    phage_array = np.sort(phage_array, order=["PhageID"], kind="mergesort")

    return phage_array


def get_phams_by_phage(handler, phage):
    """
    Connects to MySQL using MySQLConnectionHandler with verified user
    credentials and database and queries for the phams present in a
    particular phage genome.
    :param handler: MySQLConnectionHandler instance
    :param phage: selected genome
    :return pham_data: dictionary whose keys are phageids and whose
    values are the phams in that phageid.
    """
    query = "SELECT * FROM (SELECT c.name FROM phage AS a INNER JOIN gene" \
            " AS b ON a.PhageID = b.PhageID INNER JOIN pham AS c ON " \
            "b.GeneID = c.GeneID WHERE a.PhageID = '{}') AS d ORDER BY " \
            "name ASC".format(phage)
    phams = list()

    try:
        handler.open_connection()
        results = handler.execute_query(query)
        handler.close_connection()
    except:
        handler.close_connection()
        return phams

    for result in results:
        phams.append(result["name"])
    return phams


def update_mac_application(version):
    """
    Downloads Mac App bundle from github, unzips it, and discards the
    zip file.
    :param version: The version string of the Mac App bundle to get
    :return: 0 if success, 1 if any fail
    """
    commands = [
        "curl -L {} {}/MacOS-version{}.zip".format(GIT_APP.format(version),
                                                   DOWNLOAD_DIR, version),
        "unzip {}/MacOS-version{}.zip -d {}".format(DOWNLOAD_DIR, version,
                                                    DOWNLOAD_DIR),
        "rm {}/MacOS-version{}.zip".format(DOWNLOAD_DIR, version)]

    # Iterate through, process, and run each command as a subprocess
    try:
        for command in commands:
            command = shlex.split(command)
            Popen(args=command).wait()
        return 0
    except OSError:
        return 1
