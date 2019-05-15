import pymysql as pms
from tools.objects.MySQLConnectionHandler import MySQLConnectionHandler


def validate_mysql_credentials(username, password):
	"""
	Tests input username and password to see if a successful MySQL
	connection can be made using them.  If yes, close the connection and
	return the given username and password.  Else, close the connection
	and return None and None.
	:param username: MySQL username to be tested
	:param password: MySQL password to be tested
	:return: (username, password) or (None, None)
	"""
	temp_handler = MySQLConnectionHandler(username, password)
	temp_handler.test_username_and_password()
	if temp_handler.successful_login is True:
		del temp_handler
		return username, password
	else:
		del temp_handler
		return None, None


def get_database_names(username, password):
	"""
	Connects to MySQL using verified username and password and queries
	for all databases the user has access to.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:return databases: list of MySQL databases that the verified user
	has access to.
	"""
	try:
		databases = []
		connection = pms.connect("localhost", username, password)
		cursor = connection.cursor()
		cursor.execute("SHOW DATABASES")
		results = cursor.fetchall()
		for result in results:
			databases.append(result[0])
		connection.close()
		return databases
	except pms.err.Error:  # as err:
		# print("Error {}: {}".format(err.args[0], err.args[1]))
		return


def get_database_hosts(username, password, database):
	"""
	Connects to MySQL using verified username, password, and a database
	and queries for all the hosts in that database.
	:param username: verified MySQL username
	:param password: verified MySQL password
	:param database: selected MySQL database
	:return hosts: list of hosts in the selected database
	"""
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


def get_database_clusters(username, password, database):
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


def get_database_phages(username, password, database, status):
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
			query = "SELECT PhageID FROM phage WHERE status = 'final' OR " \
					"status = 'gbk'"
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


def get_phams_by_host(username, password, database, host, status):
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
					"a.HostStrain = '{}' AND a.status = 'final' OR a.status " \
					"= 'gbk') AS d ORDER BY d.PhageID ASC".format(host)
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


def get_phams_by_cluster(username, password, database, cluster, status):
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
						"c.GeneID WHERE a.Cluster is Null AND a.status = " \
						"'final' OR status = 'gbk') AS d ORDER BY d.PhageID " \
						"ASC".format(cluster)
			elif cluster == "Unclustered":
				query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster = 'UNK' AND a.status = " \
						"'final' OR status = 'gbk') AS d ORDER BY d.PhageID " \
						"ASC".format(cluster)
			else:
				query = "SELECT * FROM (SELECT a.PhageID, c.name, a.status " \
						"FROM phage AS a INNER JOIN gene AS b ON a.PhageID " \
						"= b.PhageID INNER JOIN pham AS c ON b.GeneID = " \
						"c.GeneID WHERE a.Cluster = '{}' AND a.status = " \
						"'final' OR status = 'gbk') AS d ORDER BY d.PhageID " \
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


def get_phams_by_phage(username, password, database, phage):
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
