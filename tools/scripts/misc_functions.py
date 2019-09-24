from data.constants import *
import os
import shlex
from subprocess import Popen



def get_database_names(handler):
	"""
	Connects to MySQL using verified username and password and queries
	for all databases the user has access to.
	:param handler: MySQLConnectionHandler instance
	:return: List of databases parsed from returned results
	"""
	# Initialize list to store results
	databases = list()
	# Query to give MySQLConnectionHandler
	query = "SELECT DATABASES"

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


def get_metadata(handler):
	"""

	:param handler:
	:return:
	"""
	# Initialize metadata dictionary
	metadata = {"PhageID": list(), "HostStrain": list(),
				"Cluster": list(), "Subcluster": list(), "Status": list()}
	# Query for MySQL
	query = "SELECT PhageID, HostStrain, Cluster2, Subcluster2, status FROM " \
			"phage"

	try:
		handler.open_connection()
		results = handler.execute_query(query)
		for result in results:
			metadata["PhageID"].append(result["PhageID"])
			metadata["HostStrain"].append(result["HostStrain"])
			if result["Cluster2"] is None:
				metadata["Cluster"].append("Singleton")
				metadata["Subcluster"].append("Singleton")
			elif result["Cluster2"] == "UNK":
				metadata["Cluster"].append("Un-clustered")
				metadata["Subcluster"].append("Un-clustered")
			elif result["Subcluster2"] is None:
				metadata["Cluster"].append(result["Cluster2"])
				metadata["Subcluster"].append("Un-subclustered")
			else:
				metadata["Cluster"].append(result["Cluster2"])
				metadata["Subcluster"].append(result["Subcluster2"])
			metadata["Status"].append(result["status"])
		handler.close_connection()
	except:
		handler.close_connection()

	return metadata


def update_mac_application(version):
	"""
	Downloads Mac App bundle from github, unzips it, and discards the
	zip file.
	:param version: The version string of the Mac App bundle to get
	:return: 0 if success, 1 if any fail
	"""
	# Download will be put in user's Downloads folder
	download_dir = os.path.expanduser("~") + "/Downloads/"
	commands = [
		"curl -L {} {}/MacOS-version{}.zip".format(GIT_APP.format(version),
												   download_dir, version),
		"unzip {}/MacOS-version{}.zip -d {}".format(download_dir, version,
													download_dir),
		"rm {}/MacOS-version{}.zip".format(download_dir, version)]

	# Iterate through, process, and run each command as a subprocess
	try:
		for command in commands:
			command = shlex.split(command)
			Popen(args=command).wait()
		return 0
	except OSError:
		return 1


def get_database_hosts(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all the hosts in that database.
	:param handler: MySQLConnectionHandler instance
	:return: List of hosts returned by
	"""
	hosts = list()

	try:
		hosts = list()
		connection = pms.connect("localhost", username, password, database)
		cursor = connection.cursor()
		cursor.execute("SELECT DISTINCT HostStrain FROM phage")
		results = cursor.fetchall()
		for result in results:
			hosts.append(result[0])
		connection.close()
		return hosts
	except pms.err.Error:
		return


def get_database_clusters(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all the clusters in that database.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:return clusters: list of clusters in the selected database
	"""
	try:
		clusters = list()
		connection = pms.connect("localhost", username, password, database)
		cursor = connection.cursor()
		cursor.execute("SELECT DISTINCT Cluster FROM phage")
		results = cursor.fetchall()
		for result in results:
			if result[0] is None:
				clusters.append("Singleton")
			elif result[0] == "UNK":
				clusters.append("Unclustered")
			else:
				clusters.append(result[0])
		connection.close()
		return clusters
	except pms.err.Error:
		return


def get_database_phages(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all the phages in the database matching the desired
	status.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:param status: selected genome status (0 or 1)
	:return phages: list of phages in the selected database matching
	the genome status
	"""
	if status is None or status == 0:
		try:
			phages = []
			query = "SELECT PhageID FROM phage"
			con = pms.connect("localhost", username, password, database)
			cur = con.cursor()
			cur.execute(query)
			results = cur.fetchall()
			con.close()
			for result in results:
				phages.append(result[0])
			return phages
		except pms.err.Error as err:
			print(err)
			return
	elif status == 1:
		try:
			phages = []
			query = "SELECT PhageID FROM phage WHERE status in ('final','gbk')"
			con = pms.connect("localhost", username, password, database)
			cur = con.cursor()
			cur.execute(query)
			results = cur.fetchall()
			con.close()
			for result in results:
				phages.append(result[0])
			return phages
		except pms.err.Error as err:
			print(err)
			return


def get_host_and_cluster_by_phageid(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for the host for the input phageid
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:param phageid: phage whose host is requested
	:return: phageid, host, cluster
	"""
	try:
		query = "SELECT HostStrain, Cluster FROM phage WHERE PhageID = " \
				"'{}'".format(phageid)
		con = pms.connect("localhost", username, password, database)
		cur = con.cursor()
		cur.execute(query)
		results = cur.fetchall()
		con.close()
		host = results[0][0]
		cluster = results[0][1]
		if cluster is None:
			return phageid, host, "Singleton"
		elif cluster == "UNK":
			return phageid, host, "Unclustered"
		else:
			return phageid, host, cluster
	except pms.err.Error as err:
		print(err)
		return


def get_phams_by_host(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all phages and phams in the database matching the
	input host and status.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:param host: selected genome HostStrain
	:param status: selected genome status (0 or 1)
	:return pham_data: dictionary whose keys are phageids and whose
	values are the phams in that phageid.
	"""
	if status is None or status == 0:
		try:
			pham_data = {}
			query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status FROM " \
					"phage AS a INNER JOIN gene AS b ON a.PhageID = " \
					"b.PhageID INNER JOIN pham AS c ON b.GeneID = c.GeneID " \
					"WHERE a.HostStrain = '{}') AS d ORDER BY " \
					"d.PhageID ASC".format(host)
			con = pms.connect("localhost", username, password, database)
			cur = con.cursor()
			cur.execute(query)
			results = cur.fetchall()
			con.close()
			for result in results:
				phageid = result[0]
				phams = pham_data.get(phageid, [])
				phams.append(result[1])
				pham_data[phageid] = phams
			return pham_data
		except pms.err.Error as err:
			print(err)
			return
	elif status == 1:
		try:
			pham_data = {}
			query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status FROM " \
					"phage AS a INNER JOIN gene AS b ON a.PhageID = b.PhageID" \
					" INNER JOIN pham AS c ON b.GeneID = c.GeneID WHERE " \
					"a.HostStrain = '{}' AND a.status in ('final','gbk')) AS " \
					"d ORDER BY d.PhageID ASC".format(host)
			con = pms.connect("localhost", username, password, database)
			cur = con.cursor()
			cur.execute(query)
			results = cur.fetchall()
			con.close()
			for result in results:
				phageid = result[0]
				phams = pham_data.get(phageid, [])
				phams.append(result[1])
				pham_data[phageid] = phams
			return pham_data
		except pms.err.Error as err:
			print(err)
			return


def get_phams_by_cluster(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all phages and phams in the database matching the
	input cluster and status.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:param cluster: selected genome Cluster
	:param status: selected genome status (0 or 1)
	:return pham_data: dictionary whose keys are phageids and whose
	values are the phams in that phageid.
	"""
	if status is None or status == 0:
		try:
			pham_data = {}
			# Format the query based on cluster; status is irrelevant
			if cluster == "Singleton":
				query ="SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster is Null) AS d ORDER BY " \
						"d.PhageID ASC".format(cluster)
			elif cluster == "Unclustered":
				query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster = 'UNK') AS d ORDER BY " \
						"d.PhageID ASC".format(cluster)
			else:
				query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster = '{}') AS d ORDER BY " \
						"d.PhageID ASC".format(cluster)
			con = pms.connect("localhost", username, password, database)
			cur = con.cursor()
			cur.execute(query)
			results = cur.fetchall()
			con.close()
			for result in results:
				phageid = result[0]
				phams = pham_data.get(phageid, [])
				phams.append(result[1])
				pham_data[phageid] = phams
			return pham_data
		except pms.err.Error as err:
			print(err)
			return
	elif status == 1:
		try:
			pham_data = {}
			# Format the query based on cluster and status=final
			if cluster == "Singleton":
				query ="SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster is Null AND a.status in " \
						"('final','gbk')) AS d ORDER BY d.PhageID " \
						"ASC".format(cluster)
			elif cluster == "Unclustered":
				query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster = 'UNK' AND a.status in " \
						"('final','gbk')) AS d ORDER BY d.PhageID " \
						"ASC".format(cluster)
			else:
				query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster = '{}' AND a.status in " \
						"('final','gbk')) AS d ORDER BY d.PhageID " \
						"ASC".format(cluster)

			con = pms.connect("localhost", username, password, database)
			cur = con.cursor()
			cur.execute(query)
			results = cur.fetchall()
			con.close()
			for result in results:
				phageid = result[0]
				phams = pham_data.get(phageid, [])
				phams.append(result[1])
				pham_data[phageid] = phams
			return pham_data
		except pms.err.Error as err:
			print(err)
			return


def get_phams_by_phage(handler):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all phages and phams in the database matching the
	input phage.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:param phage: selected genome
	:return pham_data: dictionary whose keys are phageids and whose
	values are the phams in that phageid.
	"""
	try:
		pham_data = {}
		query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status FROM phage" \
				" AS a INNER JOIN gene AS b ON a.PhageID = b.PhageID INNER " \
				"JOIN pham AS c ON b.GeneID = c.GeneID WHERE a.PhageID = " \
				"'{}') AS d ORDER BY d.PhageID ASC".format(phage)
		con = pms.connect("localhost", username, password, database)
		cur = con.cursor()
		cur.execute(query)
		results = cur.fetchall()
		con.close()
		for result in results:
			phageid = result[0]
			phams = pham_data.get(phageid, [])
			phams.append(result[1])
			pham_data[phageid] = phams
		return pham_data
	except pms.err.Error as err:
		print(err)
		return
