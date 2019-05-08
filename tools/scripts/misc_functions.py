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
	try:
		hosts = []
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


def get_database_phages(username, password, database, host=None, cluster=None):
	if host:
		try:
			phages = list()
			connection = pms.connect("localhost", username, password, database)
			cursor = connection.cursor()
			cursor.execute("SELECT PhageID FROM phage WHERE HostStrain = "
						   "'{}'".format(host))
			results = cursor.fetchall()
			for result in results:
				phages.append(result[0])
			connection.close()
			return phages
		except pms.err.Error:
			return
	elif cluster:
		try:
			phages = list()
			connection = pms.connect("localhost", username, password, database)
			cursor = connection.cursor()
			if cluster == "Singleton":
				cursor.execute("SELECT PhageID FROM phage WHERE Cluster is "
							   "Null")
			elif cluster == "Unclustered":
				cursor.execute("SELECT PhageID FROM phage WHERE Cluster = "
							   "'UNK'")
			else:
				cursor.execute("SELECT PhageID FROM phage WHERE Cluster = "
						   "'{}'".format(cluster))
			results = cursor.fetchall()
			for result in results:
				phages.append(result[0])
			connection.close()
			return phages
		except pms.err.Error as err:
			print(err)
			return
	else:
		try:
			phages = list()
			connection = pms.connect("localhost", username, password, database)
			cursor = connection.cursor()
			cursor.execute("SELECT PhageID FROM phage")
			results = cursor.fetchall()
			for result in results:
				phages.append(result[0])
			connection.close()
			return phages
		except pms.err.Error:
			return


def get_phams(username, password, database, phage):
	try:
		phams = []
		connection = pms.connect("localhost", username, password, database)
		cursor = connection.cursor()
		cursor.execute("SELECT DISTINCT d.name FROM (SELECT a.PhageID, "
					   "c.name FROM phage AS a INNER JOIN gene AS b ON "
					   "a.PhageID = b.PhageID INNER JOIN pham AS c ON "
					   "b.GeneID = c.GeneID) AS d WHERE d.PhageID = '{}' "
					   "ORDER BY d.name ASC".format(phage))
		results = cursor.fetchall()
		for result in results:
			phams.append(int(result[0]))
		return phams
	except pms.err.Error:
		return