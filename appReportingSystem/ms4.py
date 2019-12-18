from flask import Flask, render_template, redirect, url_for, request, session, flash, json, jsonify, send_file, send_from_directory
from base64 import b64encode
import mysql.connector
from mysql.connector import Error
import requests
import datetime
from db import databaseCMS
import pandas as pd
# import pickle

app = Flask(__name__, static_folder='app/static')
app.static_folder = 'static'
app.secret_key = 'ms4'

app.config['UPLOAD_FINISHED_REQUEST'] = 'finishedRequest'
app.config['FOLDER_SCHEDULE'] = 'Schedule'

micro1 = 'http://127.0.0.1:5001/'
micro2 = 'http://127.0.0.1:5002/'
micro3 = 'http://127.0.0.1:5003/'
micro4 = 'http://127.0.0.1:5004/'


@app.route('/getNamaFile/<kode_laporan>', methods=['GET'])
def getNamaFile(kode_laporan):
	try:
		db 		= databaseCMS.db_readReport()
		cursor 	= db.cursor()

		cursor.execute('SELECT namaFile from readreport WHERE report_id = "'+kode_laporan+'"')

		result = cursor.fetchone()
		print(result)
		return json.dumps(result)

	except Error as e :
		            print("Error while connecting file MySQL", e)
	finally:
	        #Closing DB Connection.
	            if(db.is_connected()):
	                cursor.close()
	                db.close()
	            print("MySQL connection is closed")

	
@app.route('/updateReport/<dataMS4>', methods=['POST','GET'])
def updateReport(dataMS4):
	if request.method == 'POST':
		loadData = json.loads(dataMS4)
		for row in loadData:
			kode_laporan 	= row['kode_laporan']
			org_id 			= row['org_id']
			namaFile 		= row['namaFile']
			PIC 			= row['PIC']
			Pen 			= row['Penerima']
			report_judul 	= row['reportJudul']



		lastProc = datetime.datetime.now()
		try:
			db = databaseCMS.db_readReport()
			cursor = db.cursor()
			cursor.execute("INSERT INTO readreport (report_id, report_judul, org_id, namaFile,\
	                             report_lastProcess, read_PIC, read_Penerima)\
	                             VALUES(%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE\
	                             report_judul='"+report_judul+"', org_id='"+org_id+"',\
	                             namaFile='"+namaFile+"', report_lastProcess='"+str(lastProc)+"',\
	                             read_PIC = '"+str(PIC)+"', read_Penerima='"+str(Pen)+"' ",(kode_laporan, report_judul,\
	                                org_id, namaFile, str(lastProc), str(PIC), str(Pen)))
			db.commit()
		except Error as e :
		            print("Error while connecting file MySQL", e)
		finally:
		        #Closing DB Connection.
		            if(db.is_connected()):
		                cursor.close()
		                db.close()
		            print("MySQL connection is closed")


@app.route('/viewReportId')
def viewReportId():
	try:
		db = databaseCMS.db_readReport()
		cursor = db.cursor()

		cursor.execute('SELECT LEFT(report_id, 3) FROM readreport ')

		listReportId = cursor.fetchall()

		LR = []

		for row in listReportId:
			listDict={
			'reportId' 		: row[0]
			}
			LR.append(listDict)

		result = json.dumps(LR)

		return result

	except Error as e :
		print("Error while connecting file MySQL", e)
	finally:
	#Closing DB Connection.
		if(db.is_connected()):
		        cursor.close()
		        db.close()
		print("MySQL connection is closed")	



@app.route('/viewReport/<email>', methods=['POST','GET'])
def viewReport(email):
	try:
		db = databaseCMS.db_readReport()
		cursor = db.cursor()

		cursor.execute('SELECT report_id, org_id, report_judul,namaFile, report_lastProcess\
		                FROM readreport WHERE read_PIC\
		                LIKE "%'+email+'%" OR read_penerima LIKE "%'+email+'%" ')

		listReport = cursor.fetchall()

		LR = []


		for row in listReport:
			a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+str(row[1]))
			b = json.dumps(a.json())
			c = json.loads(b)
			for x in c:
				orgName = x['org_name']


			listDict={
			'reportId' 		: row[0],
			'orgName' 		: orgName,
			'orgId' 		: row[1],
			'reportJudul' 	: row[2],
			'namaFile' 		: row[3],
			'reportLastProc': row[4]
			}
			LR.append(listDict)

		result = json.dumps(LR)

		return result

	except Error as e :
		print("Error while connecting file MySQL", e)
	finally:
	#Closing DB Connection.
		if(db.is_connected()):
		        cursor.close()
		        db.close()
		print("MySQL connection is closed")

@app.route('/viewAllReport/<kode_laporan>', methods=['POST','GET'])
def viewAllReport(kode_laporan):
	try:
		db = databaseCMS.db_readReport()
		cursor = db.cursor()

		cursor.execute('SELECT report_id, org_id, report_judul,namaFile, report_lastProcess\
		                FROM readreport WHERE report_id LIKE "%kode_laporan%"\
		                ORDER BY report_lastProcess desc ')

		listReport = cursor.fetchall()

		LR = []

		for row in listReport:
			a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+str(row[1]))
			b = json.dumps(a.json())
			c = json.loads(b)
			for x in c:
				orgName = x['org_name']

			listDict={
			'reportId' 		: row[0],
			'orgName' 		: orgName,
			'orgId' 		: row[1],
			'reportJudul' 	: row[2],
			'namaFile' 		: row[3],
			'reportLastProc': row[4]
			}
			LR.append(listDict)

		result = json.dumps(LR)

		return result

	except Error as e :
		print("Error while connecting file MySQL", e)
	finally:
	#Closing DB Connection.
		if(db.is_connected()):
		        cursor.close()
		        db.close()
		print("MySQL connection is closed")

@app.route('/readNow/<sessId>/<sessName>', methods=['POST','GET'])
def readNow(sessId,sessName):
    if request.method == 'POST':
        kode_laporan = request.form['kodRead']
        namaF       = requests.get(micro4+'getNamaFile/'+kode_laporan)
        namaResp    = json.dumps(namaF.json())
        namaFi      = json.loads(namaResp)
        namaFile    = str(namaFi).replace("['","").replace("']","")
        
        df = pd.read_excel(app.config['FOLDER_SCHEDULE']+'/'+namaFile+'.xls')
        # read = pickle.loads(base64.b64decode(excel.encode()))
        print("=== [ readNow ] ===")
        print('ID   : ',sessId),print('Name : ',sessName)
        print('Time : ',datetime.datetime.now().strftime('%X'))
        print("===================")
        
        return df.to_html()		


@app.route('/downloadReport/<sessId>/<sessName>', methods=['POST','GET'])
def downloadReport(sessId,sessName):
    if request.method == 'POST':
        kode_laporan = request.form['kodLap']
        print(kode_laporan)

        tgl = datetime.datetime.now().strftime('%d')
        bln = datetime.datetime.now().strftime('%B')

        # resp = requests.get(micro4+'downloadReport/'+kode_laporan)

        namaF       = requests.get(micro4+'getNamaFile/'+kode_laporan)
        namaResp    = json.dumps(namaF.json())
        namaFi      = json.loads(namaResp)
        namaFile    = str(namaFi).replace("['","").replace("']","")
        
        # directory = 'C:/Report/'+bln+'/'+tgl

        # if not os.path.exists(directory):
        #     os.makedirs(directory)

        # output = open(directory+'/'+namaFile+'.xls', 'wb')
        # output.write(resp.content)
        # output.close()
        print("=== [ downloadReport ] ===")
        print('ID   : ',sessId),print('Name : ',sessName)
        print('Time : ',datetime.datetime.now().strftime('%X'))
        print("===================")

        return send_from_directory(app.config['FOLDER_SCHEDULE'],namaFile+'.xls',attachment_filename=namaFile+'.xls', as_attachment=True)

@app.route('/downloadRequest',methods=['POST','GET'])
def downloadRequest():
    if request.method == 'POST':
        request_id=request.form['downloadButton']

        print(request_id)


        # resp=requests.get(micro4+'downloadRequest/'+request_id)


        # directory = 'C:/Request/'

        # if not os.path.exists(directory):
        #     os.makedirs(directory)
 
        # output = open(directory+request_id+'.xls', 'wb')
        # output.write(resp.content)
        # output.close()
        return send_from_directory(app.config['UPLOAD_FINISHED_REQUEST'],request_id+'.xls', attachment_filename=request_id+'.xls', as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port='5004')