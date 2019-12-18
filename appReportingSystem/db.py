import pyodbc
import mysql.connector
from mysql.connector import Error

import base64

class databaseCMS:


	def db_aws(database):
		connection = mysql.connector.connect(
		host='52.220.146.133',
		database=database,
		user='pifelix',
		password='7f2rFS*2018')
		if connection.is_connected():
		    db_Info= connection.get_server_info()
		print("=======================================")
		print("Connected to MySQL database...",db_Info)
		print("=======================================")


		return connection
	

	def db_request():
		
		connection = mysql.connector.connect(
		host='localhost',
		database='cms_request',
		user='root',
		password='qwerty')
		if connection.is_connected():
		    db_Info= connection.get_server_info()
		print("=======================================")
		print("Connected to MySQL database...",db_Info)
		print("=======================================")


		return connection


	def db_template():

		connection = mysql.connector.connect(
		host='localhost',
		database='cms_template',
		user='root',
		password='qwerty')
		if connection.is_connected():
		    db_Info= connection.get_server_info()
		print("=======================================")
		print("Connected to MySQL database...",db_Info)
		print("=======================================")
		return connection


	def db_scheduling():

		connection = mysql.connector.connect(
		host='localhost',
		database='cms_scheduling',
		user='root',
		password='qwerty')
		if connection.is_connected():
		    db_Info= connection.get_server_info()
		print("=======================================")
		print("Connected to MySQL database...",db_Info)
		print("=======================================")
		return connection

	def db_readReport():

		connection = mysql.connector.connect(
		host="localhost",
		database="cms_readreport",
		user="root",
		password="qwerty")
		if connection.is_connected():
			db_Info = connection.get_server_info()
		print("=======================================")
		print("Connected to MySQL database...",db_Info)
		print("=======================================")
		return connection


	def db_server(serverId):
		db=databaseCMS.db_template()
		cursor=db.cursor()
		cursor.execute('SELECT server_jenis, server_host, server_port,\
						 server_loginName, server_password FROM m_server\
						WHERE server_id = "'+serverId+'" ')
		result = cursor.fetchone()

		server_jenis 	= result[0]
		server_host 	= result[1]
		server_port 	= result[2]
		server_user 	= result[3]

		# passwordDecoded=base64.b64decode(result[4])
		# server_password=str(passwordDecoded,'utf-8')

		if server_jenis == '1':
			passwordDecoded=base64.b64decode(result[4])
			server_password=str(passwordDecoded,'utf-8')

			connection = mysql.connector.connect(
			host = server_host,
			user = server_user,
			password = server_password)
			
			#base64.b64decode("cGFzc3dvcmQ=").decode("utf-8")
			if connection.is_connected():
			    db_Info= connection.get_server_info()
			print("=======================================")
			print("Connected to MySQL database...",db_Info)
			print("=======================================")
			return connection

		else:
			connection = mysql.connector.connect(
			host='localhost',
			database='cms_request',
			user='root',
			password='qwerty')
			if connection.is_connected():
			    db_Info= connection.get_server_info()
			print("=======================================")
			print("Connected to MySQL database...",db_Info)
			print("=======================================")

			# connection = pyodbc.connect(r'Driver={SQL Server};Server=oculus;\
			#						Database=CMS_2;UID=reporting_dept;PWD=r3porting')
        

   			#return conn

			return connection
			



