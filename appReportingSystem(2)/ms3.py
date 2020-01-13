from flask import Flask, json, session, flash,send_from_directory
import datetime
import mysql.connector
from mysql.connector import Error
from db import databaseCMS
import json
import requests
import xlsxwriter
import os
from flask_apscheduler import APScheduler
# from apscheduler.scheduler import BlockingScheduler
import socket

scheduler = APScheduler()
# scheduler.start()


app = Flask(__name__, static_folder='app/static')


app.static_folder = 'static'
app.secret_key = 'ms3'


app.config['FOLDER_PREVIEW'] = 'previewReport'
app.config['FOLDER_SCHEDULE'] = 'Schedule'

micro2 = 'http://127.0.0.1:5002/'



def generateRunId():
    now     = datetime.datetime.now()
    runDate = datetime.datetime.now().strftime('%x')

    try: 
        db      = databaseCMS.db_scheduling()
        cursor  = db.cursor()
        cursor.execute('select count(report_id) from t_runningLog\
                        where run_date = "'+str(runDate)+'" ')
  
        record  = cursor.fetchone()
        clear   = str(record).replace('(','').replace(',)','')

        runId   = str(runDate).replace('/','')+str(clear).zfill(4)
 
        return runId
    except Error as e :
            print("Error while connecting file MySQL", e)
    finally:
            #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")




@scheduler.task('cron', id="run_schedule", hour='14', minute='43')
@app.route('/runScheduleToday')
def runScheduleToday():
	def getScheduleToday():

		kodeToday 	= requests.get(micro2+'getKodeReportRunToday')
		resp 		= json.dumps(kodeToday.json())
		result 		= json.loads(resp)

		getRunSched = getStatusRunSchedule()
		getRunSched = json.loads(getRunSched)

		finishRun = []
		for i in getRunSched:
			repId = i['reportId']
			finishRun.append(repId)

		# listKode = []
		# for i in result:
		# 	kode = i['reportId']
		# 	listKode.append(kode)
	
		# listKodeFix = [x for x in listKode if not x in finishRun]
		listKode = []
		for i in result:
			listKodeD={
			'reportId'      : i['reportId'],
			'server_id'     : i['server_id'],
			'org_id'        : i['org_id'],
			'orgNama'       : i['orgNama'],
			'ktgri_id'      : i['ktgri_id'],
			'kateNama'      : i['kateNama'],
			'reportJudul'   : i['reportJudul'],
			'schHari'       : i['schHari'],
			'schBulan'      : i['schBulan'],
			'schTanggal'    : i['schTanggal'],
			'schPenerima'   : i['schPenerima'],
			'namaPenerima'  : i['namaPenerima'],
			'schPIC'        : i['schPIC'],
			'namaPIC'       : i['namaPIC']
			}
			if listKodeD['reportId'] not in finishRun:
				listKode.append(listKodeD)
		
		return listKode

	def runSchedule():
		
		listSchedule = getScheduleToday()
		# listJam 	= getScheduleJam()

		listKodeToday   = []
		organisasi      = []
		serverR         = []
		kategori        = []
		judulR          = []
		hariR           = []
		bulanR          = []
		tglR            = []
		for i in listSchedule:
			reportId    = i['reportId']
			server_id   = i['server_id']
			org_id      = i['org_id']
			ktgri_id    = i['ktgri_id']
			reportJudul = i['reportJudul']
			hari        = i['schHari']
			bulan       = i['schBulan']
			tanggal     = i['schTanggal']


			listKodeToday.append(reportId)
			organisasi.append(org_id)
			serverR.append(server_id)
			kategori.append(ktgri_id)
			judulR.append(reportJudul)
			hariR.append(hari)
			bulanR.append(bulan)
			tglR.append(tanggal)

		lengthOfReportId = len(listKodeToday)
		

		for i in range (lengthOfReportId):        
			executeSchedule(listKodeToday[i])

	while len(getScheduleToday())  > 0:
		runSchedule()
	# runSchedule()	

	return 'Tidak ada report untuk dijalankan'


@scheduler.task('interval', id="run_scheduleJam", hours=1,start_date='2019-12-17 01:00:00', end_date='2200-12-12 01:00:00')
@app.route('/runScheduleJam')
def runScheduleJam():
	def getScheduleJam():

		kodeJam 	= requests.get(micro2+'getKodeReportRunJam')
		respJ 		= json.dumps(kodeJam.json())
		resultJ 	= json.loads(respJ)

		getRunSched = getStatusRunSchedule()
		getRunSched = json.loads(getRunSched)

		finishRun = []
		for i in getRunSched:
			repId = i['reportId']
			finishRun.append(repId)
		
		listJam = []
		for i in resultJ:			
			listJamD = {
			'reportId'      : i['reportId'],
			'server_id'     : i['server_id'],
			'org_id'        : i['org_id'],
			'orgNama'       : i['orgNama'],
			'ktgri_id'      : i['ktgri_id'],
			'kateNama'      : i['kateNama'],
			'reportJudul'   : i['reportJudul'],
			'schHari'       : i['schHari'],
			'schBulan'      : i['schBulan'],
			'schTanggal'    : i['schTanggal'],
			'schPenerima'   : i['schPenerima'],
			'namaPenerima'  : i['namaPenerima'],
			'schPIC'        : i['schPIC'],
			'namaPIC'       : i['namaPIC'],
			'jam' 			: i['jamRun']
			}
			if listJamD['reportId'] not in finishRun:
				listJam.append(listJamD)
		return listJam

	def runScheduleJ():
		listScheduleJam = getScheduleJam()

		listKodeJam   	= []
		organisasi      = []
		serverR         = []
		kategori        = []
		judulR          = []
		hariR           = []
		bulanR          = []
		tglR            = []
		jam 			= []
		for i in listScheduleJam:
			reportId    = i['reportId']
			server_id   = i['server_id']
			org_id      = i['org_id']
			ktgri_id    = i['ktgri_id']
			reportJudul = i['reportJudul']
			hari        = i['schHari']
			bulan       = i['schBulan']
			tanggal     = i['schTanggal']
			schJam 		= i['jam']

			listKodeJam.append(reportId)
			organisasi.append(org_id)
			serverR.append(server_id)
			kategori.append(ktgri_id)
			judulR.append(reportJudul)
			hariR.append(hari)
			bulanR.append(bulan)
			tglR.append(tanggal)
			jam.append(schJam)

		lengthOfReportId = len(listKodeJam)

		jamSekarang = datetime.datetime.now().strftime('%X')[0:2]

		for i in range (lengthOfReportId):
			if jam[i] == jamSekarang:
				executeSchedule(listKodeJam[i])
			else:
				pass
	
	while len(getScheduleJam()) > 0:
		runScheduleJ()
	



@app.route('/countScheduleToday')
def countScheduleToday():
	try:
		db = databaseCMS.db_scheduling()
		cursor = db.cursor()

		cursor.execute('SELECT COUNT(DISTINCT report_id) FROM t_runningLog WHERE LEFT(run_date,2)\
						= (SELECT MONTH(NOW())) AND MID(run_date,4,2) = (SELECT RIGHT(curdate(),2))\
						AND run_status ="B"')
		
		successReport = cursor.fetchone()

		cursor.execute('SELECT COUNT(DISTINCT report_id) FROM t_runningLog WHERE LEFT(run_date,2)\
		 				= (SELECT MONTH(NOW())) AND MID(run_date,4,2) = (SELECT RIGHT(curdate(),2))\
		 				AND run_status ="G" ')
		failedReport = cursor.fetchone()

		countReport = {
		'successReport' : str(successReport).replace("(","").replace(",)",""),
		'failedReport' : str(failedReport).replace("(","").replace(",)","")
		}
		
		result = json.dumps({'data' : countReport})

		return result
	except Error as e :
	        print("Error while connecting file MySQL", e)
	finally:
	        #Closing DB Connection.
	            if(db.is_connected()):
	                cursor.close()
	                db.close()
	            print("MySQL connection is closed")



@app.route('/getStatusRunSchedule',methods=['POST','GET'])
def getStatusRunSchedule():
    try:
        db = databaseCMS.db_scheduling()
        cursor = db.cursor()
        cursor.execute('SELECT report_id, org_id, ktgri_id, run_date, MAX(run_startTime),\
                        run_endTime, server_id, run_status, error_deskripsi\
                        FROM t_runningLog\
                        WHERE LEFT(run_date,2) = (SELECT MONTH(NOW()))\
                        AND MID(run_date,4,2) = (SELECT RIGHT(curdate(),2))\
                        GROUP BY report_id\
                        ORDER BY run_startTime')
        res = cursor.fetchall()


        res2 = []

        for row in res:
            a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+str(row[1]))
            b = json.dumps(a.json())
            c = json.loads(b)
            for x in c:
                orgName = x['org_name']
        
            d = requests.get('http://127.0.0.1:5001/getNamaKat/'+str(row[2]))
            e = json.dumps(d.json())
            f = json.loads(e)
            for kat in f:
                katName = kat['kat_name']

        
        # for row in res:
            resD={
            'reportId'      : row[0],
            'orgId'         : row[1],
            'orgNama'       : orgName,
            'ktgriId'       : row[2],
            'kateNama'      : katName,
            'runDate'       : row[3],
            'runStartTime'  : row[4],
            'runEndTime'    : row[5],
            'serverId'      : row[6],
            'runStatus'     : row[7],
            'errorDesc'     : row[8]
            }
            res2.append(resD)
        resFix = json.dumps(res2)

        return resFix
    except Error as e :
            print("Error while connecting file MySQL", e)
    finally:
            #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")



@app.route('/previewLaporan/<kode_laporan>', methods=['GET','POST'])
def previewLaporan(kode_laporan):
	try:

		count_header = 0
		waktuproses = datetime.datetime.now().strftime('%X')
		#==============================[ MENDAPATKAN DETAIL REPORT ]============================== 
		detReport       = requests.get('http://127.0.0.1:5002/getDetailReport/'+kode_laporan)
		detRResp        = json.dumps(detReport.json())
		loadDetailReport = json.loads(detRResp)


		# MENDAPATKAN JUMLAH HEADER (1 / 2)
		jmlHead = loadDetailReport[6]
		servId = loadDetailReport[9]

		print('=============[PREVIEW]===============')
		print('Jumlah Header: ',jmlHead)


	    #==============================[ MENDAPATKAN DETAIL HEADER ]==============================
		getDetH = requests.get('http://127.0.0.1:5002/getDetailH/'+kode_laporan)
		detHResp = json.dumps(getDetH.json())
		loadDetailH = json.loads(detHResp)

		countHeader     = []
		lebar           = []
		listKolom       = []
		lokasiHeader    = []
		formatKolom     = []
		rataTengah      = []
		rataKanan       = []
		formulaH 		= []
		formatFooterH 	= []
		for i in loadDetailH:
			namaKolom   = i['namaKolom']
			lokasiKolom = i['lokasi']
			forKolom    = i['formatKolom']
			leb         = i['lebarKolom']
			ratTengah   = i['rataTengah']
			ratKanan    = i['rataKanan']
			formulaH1 	= i['formula']

			forFoot = {
			'lokasi' : str(lokasiKolom)[0:1],
			'format' : forKolom
			}
			formatFooterH.append(forFoot)

			formulaD = {
			'lokasi' : str(lokasiKolom)[0:1],
			'formula': formulaH1
			}
			formulaH.append(formulaD)

			listKolom.append(namaKolom)
			lokasiHeader.append(lokasiKolom)
			formatKolom.append(forKolom)
			lebar.append(leb)
			countHeader.append(namaKolom)
			rataTengah.append(ratTengah)
			rataKanan.append(ratKanan)

		formatFooterH = {'data' : formatFooterH}
		formulaH = {'data' : formulaH}
		listKolom2      = len(listKolom)
		countHeader2    = len(countHeader)
		print(formatFooterH)
		print('List Kolom : ',listKolom)
		print('Format Kolom : ',formatKolom)
		print('List Lebar : ',lebar)
	    #_________________________________________________________________________________________#
	    
		getDetH2    = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
		detHResp2   = json.dumps(getDetH2.json())
		loadDetailH2 = json.loads(detHResp2)


		listKolomHeader2    = []
		lebarH2             = []
		lokasiH2            = []
		formatKolomH2		= []
		formatFooterH2 		= []
		formulaH2 			= []
		for i in loadDetailH2:
			namaKolomH2     = i['namaKolom']
			lokasi2         = i['lokasi']
			formatKolom2   	= i['formatKolom']
			lebH2           = i['lebarKolom']
			formula2 		=i['formula']

			forFoot2={
			'lokasi2' : str(lokasi2)[0:1],
			'format2' : formatKolom2
			}
			formatFooterH2.append(forFoot2)

			formulaD2 = {
			'lokasi2' : str(lokasi2)[0:1],
			'formula2' : formula2
			}
			formulaH2.append(formulaD2)

			
			listKolomHeader2.append(namaKolomH2)
			lebarH2.append(lebH2)
			lokasiH2.append(lokasi2)
			formatKolomH2.append(formatKolom2)
		formatFooterH2 = {'data' : formatFooterH2}
		formulaH2 = {'data' : formulaH2}
		countHeaderH2 = len(listKolomHeader2)

		print('formulah2', formulaH2)

	    #==============================[ MENDAPATKAN DETAIL PIC ]==============================
		PIC = []
		Penerima = []

		getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+kode_laporan)
		namaResp = json.dumps(getNama.json())
		loadNama = json.loads(namaResp)
		for i in loadNama:
			namaPIC = i['PIC']
			namaPen = i['Pen']
			PIC.append(namaPIC)
			Penerima.append(namaPen)
		PIC = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")
		Penerima = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")

		print('List PIC : ',PIC)
		print('List Penerima : ',Penerima)
		#_________________________________________________________________________________________#




		#==============================[ MENDAPATKAN DETAIL QUERY ]==============================
		getQ = requests.get('http://127.0.0.1:5002/getQuery/'+kode_laporan)
		qResp = json.dumps(getQ.json())
		loadQ = json.loads(qResp)
		

		db = databaseCMS.db_server(loadDetailReport[9])
		cursor = db.cursor(buffered = True)

		listQuery = []
		for i in loadQ:
			reportId    = i['reportId']
			quer        = i['query']
			qno         = i['query_no']

			listQuery.append(quer)

		
		lengthOfQuery = len(listQuery)


		try:
			for i in range (lengthOfQuery):
				sql2 = listQuery[i]
				print(listQuery[i])
				cursor.execute(sql2)          
			result = cursor.fetchall()
			db.close()
			cursor.close()
			#HASIL DARI EXECUTE QUERY
			toExcel = []
			for i in result:
				toExcel.append(i)

		except Exception as e:
			err = {
			'Error execute Query :' : str(e)
			}

			return  json.dumps(err),400


		data = []
		data = toExcel
		

		lengthOfData = [x[0] for x in data]

		totalRow = len(lengthOfData)
		#_________________________________________________________________________________________#

		#======================[ FOOTER ]================================

		getF = requests.get('http://127.0.0.1:5002/getDetailF/'+kode_laporan)
		FResp = json.dumps(getF.json())
		detailFooter = json.loads(FResp)

		countFooter = loadDetailReport[4]

		kolomFooter     = []
		lokasiFooter    = []
		lokasiFooter2	= []

		for row in detailFooter:
			namaKolomF  = row['namaKolom']
			kolomFooter.append(namaKolomF)

			if row['urutan'] == '1':
				lokasi = row['lokasi'].split(", ")	
				lokasiFooter.append(lokasi)
			else:
				lokasi2 = row['lokasi'].split(", ")
				lokasiFooter2.append(lokasi2)

		lokasiFooter = str(lokasiFooter).replace("[[","").replace("]]","").replace("'","").split(", ")
		lokasiFooter2 = str(lokasiFooter2).replace("[[","").replace("]]","").replace("'","").split(", ")



		#=========== UNTUK FOOTER 1
		lokasiCurr      = []
		countOfFooter   = len(lokasiFooter)



		l = 0
		for i in range(countOfFooter):
			if (lokasiFooter[l] == 'B'):
				lokasiCurr.append(1)
			elif(lokasiFooter[l] == 'C'):
				lokasiCurr.append(2)
			elif(lokasiFooter[l] == 'D'):
				lokasiCurr.append(3)
			elif(lokasiFooter[l] == 'E'):
				lokasiCurr.append(4)
			elif(lokasiFooter[l] == 'F'):
				lokasiCurr.append(5)
			elif(lokasiFooter[l] == 'G'):
				lokasiCurr.append(6)
			elif(lokasiFooter[l] == 'H'):
				lokasiCurr.append(7)
			elif(lokasiFooter[l] == 'I'):
				lokasiCurr.append(8)
			elif(lokasiFooter[l] == 'J'):
				lokasiCurr.append(9)
			elif(lokasiFooter[l] == 'K'):
				lokasiCurr.append(10)
			elif(lokasiFooter[l] == 'L'):
				lokasiCurr.append(11)
			elif(lokasiFooter[l] == 'M'):
				lokasiCurr.append(12)
			elif(lokasiFooter[l] == 'N'):
				lokasiCurr.append(13)
			elif(lokasiFooter[l] == 'O'):
				lokasiCurr.append(14)
			elif(lokasiFooter[l] == 'P'):
				lokasiCurr.append(15)
			l = l + 1

		lokasiCurr2 = []
		
		l = 0
		for i in range(countOfFooter):
			if (lokasiFooter[l] == 'B'):
				lokasiCurr2.append('B')
			elif(lokasiFooter[l] == 'C'):
				lokasiCurr2.append('C')
			elif(lokasiFooter[l] == 'D'):
				lokasiCurr2.append('D')
			elif(lokasiFooter[l] == 'E'):
				lokasiCurr2.append('E')
			elif(lokasiFooter[l] == 'F'):
				lokasiCurr2.append('F')
			elif(lokasiFooter[l] == 'G'):
				lokasiCurr2.append('G')
			elif(lokasiFooter[l] == 'H'):
				lokasiCurr2.append('H')
			elif(lokasiFooter[l] == 'I'):
				lokasiCurr2.append('I')
			elif(lokasiFooter[l] == 'J'):
				lokasiCurr2.append('J')
			elif(lokasiFooter[l] == 'K'):
				lokasiCurr2.append('K')
			elif(lokasiFooter[l] == 'L'):
				lokasiCurr2.append('L')
			elif(lokasiFooter[l] == 'M'):
				lokasiCurr2.append('M')
			elif(lokasiFooter[l] == 'N'):
				lokasiCurr2.append('N')
			elif(lokasiFooter[l] == 'O'):
				lokasiCurr2.append('O')
			elif(lokasiFooter[l] == 'P'):
				lokasiCurr2.append('P')
			l = l + 1

		lokasiCurr2Len = len(lokasiCurr2)
		
		formatFooter1 = []
		for i in formatFooterH['data']:
			if i['lokasi'] in lokasiCurr2:
				formatFooter1.append(i['format'])
		print(formatFooterH)
		print(formatFooter1)


		formatFooter12 = []
		for i in formatFooterH2['data']:
			if i['lokasi2'] in lokasiCurr2:
				formatFooter12.append(i['format2'])
		print(formatFooterH2)
		print(formatFooter12)


		#=========== UNTUK FOOTER 2


		lokasiCurr3      = []
		countOfFooter2   = len(lokasiFooter2)

		l = 0
		for i in range(countOfFooter2):
			if (lokasiFooter2[l] == 'B'):
				lokasiCurr3.append(1)
			elif(lokasiFooter2[l] == 'C'):
				lokasiCurr3.append(2)
			elif(lokasiFooter2[l] == 'D'):
				lokasiCurr3.append(3)
			elif(lokasiFooter2[l] == 'E'):
				lokasiCurr3.append(4)
			elif(lokasiFooter2[l] == 'F'):
				lokasiCurr3.append(5)
			elif(lokasiFooter2[l] == 'G'):
				lokasiCurr3.append(6)
			elif(lokasiFooter2[l] == 'H'):
				lokasiCurr3.append(7)
			elif(lokasiFooter2[l] == 'I'):
				lokasiCurr3.append(8)
			elif(lokasiFooter2[l] == 'J'):
				lokasiCurr3.append(9)
			elif(lokasiFooter2[l] == 'K'):
				lokasiCurr3.append(10)
			elif(lokasiFooter2[l] == 'L'):
				lokasiCurr3.append(11)
			elif(lokasiFooter2[l] == 'M'):
				lokasiCurr3.append(12)
			elif(lokasiFooter2[l] == 'N'):
				lokasiCurr3.append(13)
			elif(lokasiFooter2[l] == 'O'):
				lokasiCurr3.append(14)
			elif(lokasiFooter2[l] == 'P'):
				lokasiCurr3.append(15)
			l = l + 1

		lokasiCurr4 = []
		
		l = 0
		for i in range(countOfFooter2):
			if (lokasiFooter2[l] == 'B'):
				lokasiCurr4.append('B')
			elif(lokasiFooter2[l] == 'C'):
				lokasiCurr4.append('C')
			elif(lokasiFooter2[l] == 'D'):
				lokasiCurr4.append('D')
			elif(lokasiFooter2[l] == 'E'):
				lokasiCurr4.append('E')
			elif(lokasiFooter2[l] == 'F'):
				lokasiCurr4.append('F')
			elif(lokasiFooter2[l] == 'G'):
				lokasiCurr4.append('G')
			elif(lokasiFooter2[l] == 'H'):
				lokasiCurr4.append('H')
			elif(lokasiFooter2[l] == 'I'):
				lokasiCurr4.append('I')
			elif(lokasiFooter2[l] == 'J'):
				lokasiCurr4.append('J')
			elif(lokasiFooter2[l] == 'K'):
				lokasiCurr4.append('K')
			elif(lokasiFooter2[l] == 'L'):
				lokasiCurr4.append('L')
			elif(lokasiFooter2[l] == 'M'):
				lokasiCurr4.append('M')
			elif(lokasiFooter2[l] == 'N'):
				lokasiCurr4.append('N')
			elif(lokasiFooter2[l] == 'O'):
				lokasiCurr4.append('O')
			elif(lokasiFooter2[l] == 'P'):
				lokasiCurr4.append('P')
			l = l + 1

		lokasiCurr4Len = len(lokasiCurr4)

		#HEADER 1
		formatFooter2 = []
		for i in formatFooterH['data']:
			if i['lokasi'] in lokasiCurr4:
				formatFooter2.append(i['format'])
		print(formatFooter2)

		formula1 = []
		for i in formulaH['data']:
			if i['lokasi'] in lokasiCurr2:
				formula1.append(i['formula'])
		print(formula1)

		formula2 = []
		for i in formulaH['data']:
			if i['lokasi'] in lokasiCurr4:
				formula2.append(i['formula'])
		print(formula2)




		#HEADER 2
		formatFooter22 = []
		for i in formatFooterH2['data']:
			if i['lokasi2'] in lokasiCurr4:
				formatFooter22.append(i['format2'])

		formula12 = []
		for i in formulaH2['data']:
			if i['lokasi2'] in lokasiCurr2:
				formula12.append(i['formula2'])

		formula22 = []
		for i in formulaH2['data']:
			if i['lokasi2'] in lokasiCurr4:
				formula22.append(i['formula2'])

		#_________________________________________________________________________________________#
		print('COUNT OF FOOTER 1: ',countOfFooter)
		print('COUNT OF FOOTER 2: ',countOfFooter2)
		print('LOKASI FOOTER 1 : ', lokasiCurr2)
		print('LOKASI FOOTER 2 : ', lokasiCurr4)
		print('LOKASI FOOTER 1 LEN : ', lokasiCurr2Len)
		print('LOKASI FOOTER 2 LEN : ', lokasiCurr4Len)



		if not os.path.exists(app.config['FOLDER_PREVIEW']):
			os.makedirs(app.config['FOLDER_PREVIEW'])


		namaFileExcel =  kode_laporan+'_'+loadDetailReport[5]+datetime.datetime.now().strftime('%d%m%Y')

		workbook 	= xlsxwriter.Workbook(app.config['FOLDER_PREVIEW']+'/%s.xls'% (namaFileExcel))
		worksheet 	= workbook.add_worksheet()

		#=======================[STYLE]========================================================
		string_format 	= workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman'})
		string_format2 	= workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman','top':1,'bottom':1,'hidden':True})
		integer_format 	= workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman'})
		integer_format2 = workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman','top':1,'bottom':1,'hidden':True})
		decimal_format 	= workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman'})
		decimal_format2 = workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman','top':1,'bottom':1,'hidden':True})
		date_format 	= workbook.add_format({'num_format': 15,'font_size':8,'font_name':'Times New Roman'})
		time_format 	= workbook.add_format({'num_format': 21,'font_size':8,'font_name':'Times New Roman'})
		datetime_format = workbook.add_format({'num_format': 22,'font_size':8,'font_name':'Times New Roman'})

		font_size 			= workbook.add_format({'font_size':8,'font_name':'Times New Roman'})
		format_header 		= workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True,'font_name':'Times New Roman'})
		format_headerMid 	= workbook.add_format({'font_size':8,'top':1,'bold':True,'align' : 'center','valign' : 'center','font_name':'Times New Roman'})
		format_headerBot 	= workbook.add_format({'font_size':8,'bottom':1,'bold':True,'align' : 'center','valign' : 'center','font_name':'Times New Roman'})
		category_style 		= workbook.add_format({'font_size':8,'align':'right','font_name':'Times New Roman'})
		merge_format 		= workbook.add_format({'bold':2, 'align' : 'center', 'valign' : 'vcenter', 'font_size':10,'font_name':'Times New Roman'})
		merge_formatEmpty 	= workbook.add_format({'bold':2, 'align' : 'center', 'valign' : 'vcenter', 'font_size':10, 'top':1, 'bottom':1,'font_name':'Times New Roman'})
		bold 				= workbook.add_format({'bold':True,'font_size':8,'font_name':'Times New Roman'})
	    ##################################


		if jmlHead == '1':
			print('HEAD 1')

			listMaxCol  = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
			maxCol      = (listMaxCol[countHeader2])



			nOrg        = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
			orgResp     = json.dumps(nOrg.json())
			loadNamaOrg = json.loads(orgResp)
			for i in loadNamaOrg:
				namaOrg = i['org_name']

			listColWidth    =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
			colWidth        = (listColWidth[0:countHeader2])

			colWidth2 		= (listColWidth[countHeader2-1])

			worksheet.merge_range('A1:%s'%(maxCol),'%s'%(namaOrg), merge_format) 
			worksheet.write('A2','%s' % (loadDetailReport[1]),bold ) #nama report
			worksheet.write('A3','Report Code : %s' % (loadDetailReport[0]),font_size) #kode report
			worksheet.write('A4','PIC : %s' % (PIC),font_size)
			worksheet.write('A5','Penerima : %s' % (Penerima),font_size)
			worksheet.write('A6','Filter : %s' % (loadDetailReport[2]), bold ) #filter
			worksheet.write('A7','Period : %s' % (loadDetailReport[3]),font_size) #periode
			worksheet.repeat_rows(7)  
			#penulisan printed date
			worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

			row = 0
			kol = 0

			kolom = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
			row2 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


			kolomList   = (kolom[0:countHeader2])
			rowList     = (row2[0:countHeader2])
			j = 1

			#ini untuk menulis header

			#sebelumnya for i in countHeader

			lok = 0
			

			if countFooter == '1' or countFooter == '' or countFooter is None:
				print('FOOTER 1')
				for i in (listKolom): 
					worksheet.write(lokasiHeader[lok],i,format_header)
					lok             = lok + 1
					count_header    = count_header + 1

				#end menulis header
				#Untuk mengatur lebar Kolom
				for i in range(countHeader2):
					worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))


				#UNTUK MENULIS PENOMORAN
				# lengthOfData = [x[0] for x in data]
				lengthOfData2 = len(lengthOfData)
				num = 1

				for i in range(lengthOfData2+1): 
					if (i == 0):
						worksheet.write(row + 7,kol,'No',format_header)
						row = row + 1
					else:
						worksheet.write(row + 7,kol,num,font_size)
						row = row + 1
						num = num + 1

				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':

					worksheet.merge_range('A9:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					row2 = 0
					row2 = row2 + 4

				else:
					
					# UNTUK MENULIS DATA
					m = 1
					row2 = 0

					######ZONE NEW
					rowString 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowInt 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDec 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowPer 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDate 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowTime 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDateTime = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	

					for i in range(lengthOfData2):
						for x in range(listKolom2):
							if formatKolom[x] == 'String':
								worksheet.write('%s%s'%(listColWidth[x],rowString[x]+9),data[i][x], string_format)
								rowString[x] = rowString[x] + 1
								

							elif formatKolom[x] == 'Integer':
								worksheet.write('%s%s'%(listColWidth[x],rowInt[x]+9),data[i][x], integer_format)
								rowInt[x] = rowInt[x] + 1

							elif formatKolom[x] == 'Decimal':
								worksheet.write('%s%s'%(listColWidth[x],rowDec[x]+9),data[i][x], decimal_format)
								rowDec[x] = rowDec[x] + 1

							elif formatKolom[x] == 'Percentage':
								worksheet.write('%s%s'%(listColWidth[x],rowPer[x]+9),data[i][x]*100, decimal_format)
								rowPer[x] = rowPer[x] + 1

							elif formatKolom[x] == 'Date':
								worksheet.write('%s%s'%(listColWidth[x],rowDate[x]+9),data[i][x], date_format)
								rowDate[x] = rowDate[x] + 1

							elif formatKolom[x] == 'Time':
								worksheet.write('%s%s'%(listColWidth[x],rowTime[x]+9),data[i][x], time_format)
								rowTime[x] = rowTime[x] + 1

							elif formatKolom[x] == 'Datetime':
								worksheet.write('%s%s'%(listColWidth[x],rowDateTime[x]+9),data[i][x], datetime_format)
								rowDateTime[x] = rowDateTime[x] + 1
						row2=row2+1

					######ENDZONE

					for i in range(countHeader2+1):
						worksheet.write(row2+8,i,'',format_header)
					for i in range(lokasiCurr2Len):
						if formatFooter1[i] == 'Integer' and formula1[i] == '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),integer_format2)
						elif formatFooter1[i] == 'Integer' and formula1[i] != '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=(%s%s%s%s)'% (formula1[i][0:1],totalRow+8,formula1[i][1:2],formula1[i][2:3],totalRow+8),integer_format2)

						elif formatFooter1[i] == 'Decimal' and formula1[i] == '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),decimal_format2)
						elif formatFooter1[i] == 'Decimal' and formula1[i] != '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=(%s%s%s%s)'% (formula1[i][0:1],totalRow+8,formula1[i][1:2],formula1[i][2:3],totalRow+8),decimal_format2)

						elif formatFooter1[i] == 'Percentage' and formula1[i] == '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),decimal_format2)
						elif formatFooter1[i] == 'Percentage' and formula1[i] != '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=(%s%s%s%s)'% (formula1[i][0:1],totalRow+8,formula1[i][1:2],formula1[i][2:3],totalRow+8),decimal_format2)

						else:
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),string_format2)
					



				worksheet.write(row2+10,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(row2+11,1,'Since : %s' % (loadDetailReport[7]),font_size)
				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(row2+12,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(row2+12,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(row2+13,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(row2+13,1,'Schedule : -',font_size)
				#Penulisan Creator
				worksheet.write(row2+10,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()

				return json.dumps(loadDetailReport[5]),200


			elif countFooter == '2':
				print('FOOTER 2')

				for i in (listKolom): 
					worksheet.write(lokasiHeader[lok],i,format_header)
					lok             = lok + 1
					count_header    = count_header + 1

				#end menulis header
				#Untuk mengatur lebar Kolom
				for i in range(countHeader2):
					worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))
					
				#UNTUK MENULIS PENOMORAN
				m = 1
				
				lengthOfData = [x[0] for x in data]
				lengthOfData2 = len(lengthOfData)
				
				


				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':
					worksheet.merge_range('A9:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					dataSub = 13
					
					
				else:

					try:
						dataSub = 8
						countAwal = 9

					

						for i in range(lengthOfData2):
							for x in range(countHeader2):

								if formatKolom[x] == 'String':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], string_format)
																	
								elif formatKolom[x] == 'Integer':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], integer_format)
								elif formatKolom[x] == 'Decimal':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], decimal_format)
																		
								elif formatKolom[x] == 'Percentage':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x]*100, decimal_format)
									
								elif formatKolom[x] == 'Date':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], date_format)
																	
								elif formatKolom[x] == 'Time':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], time_format)
									
								elif formatKolom[x] == 'Datetime':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], datetime_format)
									
							print('asdasdsadassd')
							dataSub = dataSub + 1

							if data[i][0] != data[i+1][0]:
								subTotal = 0
								for k in range(countHeader2+1):
									worksheet.write(dataSub,k,'',format_header)
								

								for k in range(lokasiCurr2Len):
									
									if formatFooter1[k] == 'Integer' and formula1[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
									elif formatFooter1[k] == 'Integer' and formula1[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),integer_format2)

									elif formatFooter1[k] == 'Decimal' and formula1[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter1[k] == 'Decimal' and formula1[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)

									elif formatFooter1[k] == 'Percentage' and formula1[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter1[k] == 'Percentage' and formula1[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)

									else:
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)
	

								dataSub = dataSub + 1
								countAwal = dataSub + 1



					except IndexError as e:
						
						#SUBTOTAL TERAKHIR
						for k in range(countHeader2+1):
							worksheet.write(dataSub,k,'',format_header)
						# Untuk menulis footer
						for k in range(lokasiCurr2Len):
							if formatFooter1[k] == 'Integer' and formula1[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
							elif formatFooter1[k] == 'Integer' and formula1[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),integer_format2)

							elif formatFooter1[k] == 'Decimal' and formula1[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter1[k] == 'Decimal' and formula1[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)
							
							elif formatFooter1[k] == 'Percentage' and formula1[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter1[k] == 'Percentage' and formula1[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)

							else:
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)
						
						#GRANDTOTAL
						dataSub = dataSub + 1
						countAwal = dataSub + 1
						
						for k in range(countHeader2+1):
							worksheet.write(dataSub,k,'',format_header)

				    	
						for k in range(lokasiCurr4Len):
							if formatFooter2[k] == 'Integer' and formula2[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),integer_format2)	
							elif formatFooter2[k] == 'Integer' and formula2[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s%s%s%s%s)'% (formula2[k][0:1],dataSub+1,formula2[k][1:2],formula2[k][2:3],dataSub+1),integer_format2)	
							
							elif formatFooter2[k] == 'Decimal' and formula2[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)
							elif formatFooter2[k] == 'Decimal' and formula2[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s%s%s%s%s)'% (formula2[k][0:1],dataSub+1,formula2[k][1:2],formula2[k][2:3],dataSub+1),decimal_format2)	

							elif formatFooter2[k] == 'Percentage' and formula2[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)	
							elif formatFooter2[k] == 'Percentage' and formula2[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s%s%s%s%s)'% (formula2[k][0:1],dataSub+1,formula2[k][1:2],formula2[k][2:3],dataSub+1),decimal_format2)	

							else:
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								if lokasiCurr3[k] in lokasiCurr:
									worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)	
								else:
									worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)	
						dataSub = dataSub+1
						countAwal = dataSub+1
						
						print(dataSub)


					try:
						row=0
						num = 1
						for i in range(lengthOfData2+1): 
						    if (i == 0):
						        worksheet.write(row + 7,kol,'No',format_header)
						        row = row + 1
						    elif data[i-1][0] == data[i][0]:
						    	worksheet.write(row + 7,kol,num,font_size)
						    	row = row+1
						    	num = num +1
						    	
						    else:
						        worksheet.write(row + 7,kol,num,font_size)
						        row = row + 2
						        num = num + 1

					except IndexError as e:
						worksheet.write(row + 7,kol,num,font_size)

			    # Penulisan Process Time
				worksheet.write(dataSub+1,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(dataSub+2,1,'Since : %s' % (loadDetailReport[7]),font_size)

				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(dataSub+3,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(dataSub+3,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(dataSub+4,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(dataSub+4,1,'Schedule : -',font_size)

				#Penulisan Creator
				worksheet.write(dataSub+1,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()
				return json.dumps(loadDetailReport[5]),200


		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================




		elif jmlHead == '2':
			print('HEAD 2')

			getDetH2    = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
			detHResp2   = json.dumps(getDetH2.json())
			loadDetailH2 = json.loads(detHResp2)


			listKolomHeader2    = []
			lebarH2             = []
			lokasiH2            = []
			formatKolomH2		= []
			# formulaH2 			= []
			for i in loadDetailH2:
			    namaKolomH2     = i['namaKolom']
			    lokasi2         = i['lokasi']
			    formatKolom2   	= i['formatKolom']
			    lebH2           = i['lebarKolom']
			    # formula2 		=i['formula']


			    # formulaH2.append(formula2)
			    listKolomHeader2.append(namaKolomH2)
			    lebarH2.append(lebH2)
			    lokasiH2.append(lokasi2)
			    formatKolomH2.append(formatKolom2)

			countHeaderH2 = len(listKolomHeader2)

			mCell = i['formatMerge'].replace('-',':').replace(' ','').split(',')

			for i in range(len(mCell)):
			    worksheet.merge_range('%s'%(mCell[i]),'%s'%(''), format_headerMid)


			lok = 0
			#HEADER 1
			for i in (listKolom): 
			    worksheet.write(lokasiHeader[lok],i,format_headerMid)
			    lok = lok + 1
			    count_header = count_header + 1

			#HEADER 2
			lok2 = 0
			for x in (listKolomHeader2):
			    worksheet.write(lokasiH2[lok2], x,format_header)
			    lok2 = lok2 + 1
			    count_header = count_header + 1


			lengthOfData2 = len(lengthOfData)



			#Mengatur bagian atas dari laporan

			listMaxCol = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
			maxCol = (listMaxCol[countHeaderH2])
		         

			listColWidth =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
			colWidth = (listColWidth[0:countHeader2])

			colWidth2 = (listColWidth[countHeaderH2-1])



			nOrg        = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
			orgResp     = json.dumps(nOrg.json())
			loadNamaOrg = json.loads(orgResp)
			for i in loadNamaOrg:
				namaOrg = i['org_name']

			worksheet.merge_range('A1:%s'%(maxCol),'%s'%(namaOrg), merge_format) 
			worksheet.write('A2','%s' % (loadDetailReport[1]),bold ) #nama report
			worksheet.write('A3','Report Code : %s' % (loadDetailReport[0]),font_size) #kode report
			worksheet.write('A4','PIC : %s' % (PIC),font_size)
			worksheet.write('A5','Penerima : %s' % (Penerima),font_size)
			worksheet.write('A6','Filter : %s' % (loadDetailReport[2]), bold ) #filter
			worksheet.write('A7','Period : %s' % (loadDetailReport[3]),font_size) #periode
			worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)


			worksheet.repeat_rows(7,8)

			#Untuk mengatur lebar Kolom
			for i in range(countHeader2):
			    worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))

			row = 0
			kol = 0

			kolom = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
			row2 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


			kolomList = (kolom[0:countHeader2])
			rowList = (row2[0:countHeader2])
			j = 1


			if countFooter == '1' or countFooter == '' or countFooter is None:
				print('FOOTER 1')
				num = 1
				for i in range(lengthOfData2+2): #untuk menulis penomoran 1 s/d banyak data
				    if (i == 0):
				        worksheet.write(row + 7,kol,'No',format_headerMid)
				        row = row + 1
				    elif (i == 1):
				    	worksheet.write(row + 7, kol, '', format_headerBot)
				    else:
				        worksheet.write(row + 8,kol,num,font_size)
				        row = row + 1
				        num = num + 1

				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':


					worksheet.merge_range('A10:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					row2 = 0
					row2 = row2 + 4

				else:

					m = 1
					row2 = 0

					######ZONE NEW
					rowString 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowInt 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDec 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowPer 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDate 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowTime 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDateTime = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

					
					for i in range(lengthOfData2):
						for x in range(countHeaderH2):
							
							if formatKolomH2[x] == 'String':
								worksheet.write('%s%s'%(listColWidth[x],rowString[x]+10),data[i][x], string_format)
								rowString[x] = rowString[x] + 1
								
							elif formatKolomH2[x] == 'Integer':
								worksheet.write('%s%s'%(listColWidth[x],rowInt[x]+10),data[i][x], integer_format)
								rowInt[x] = rowInt[x] + 1
								
							elif formatKolomH2[x] == 'Decimal':
								worksheet.write('%s%s'%(listColWidth[x],rowDec[x]+10),data[i][x], decimal_format)
								rowDec[x] = rowDec[x] + 1
								
							elif formatKolomH2[x] == 'Percentage':
								worksheet.write('%s%s'%(listColWidth[x],rowPer[x]+10),data[i][x]*100, decimal_format)
								rowPer[x] = rowPer[x] + 1
								
							elif formatKolomH2[x] == 'Date':
								worksheet.write('%s%s'%(listColWidth[x],rowDate[x]+10),data[i][x], date_format)
								rowDate[x] = rowDate[x] + 1
								
							elif formatKolomH2[x] == 'Time':
								worksheet.write('%s%s'%(listColWidth[x],rowTime[x]+10),data[i][x], time_format)
								rowTime[x] = rowTime[x] + 1
								
							elif formatKolomH2[x] == 'Datetime':
								worksheet.write('%s%s'%(listColWidth[x],rowDateTime[x]+10),data[i][x], datetime_format)
								rowDateTime[x] = rowDateTime[x] + 1
								
						row2=row2+1
				
					######ENDZONE
					print('ASASASA')
					print(lokasiCurr2)
					print(formatFooter12)
					print(formula12)
					for i in range(countHeaderH2+1):
						worksheet.write(row2+9,i,'',format_header)
				
					for i in range(lokasiCurr2Len):
						if formatFooter12[i] == 'Integer' and formula12[i] == '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),integer_format2)
						elif formatFooter12[i] == 'Integer' and formula12[i] != '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=(%s%s%s%s%s)'% (formula12[i][0:1],totalRow+10,formula12[i][1:2],formula12[i][2:3],totalRow+10),integer_format2)

						elif formatFooter12[i] == 'Decimal' and formula12[i] == '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),decimal_format2)
						elif formatFooter12[i] == 'Decimal' and formula12[i] != '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=(%s%s%s%s%s)'% (formula12[i][0:1],totalRow+10,formula12[i][1:2],formula12[i][2:3],totalRow+10),decimal_format2)
						
						elif formatFooter12[i] == 'Percentage' and formula12[i] == '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),decimal_format2)
						elif formatFooter12[i] == 'Percentage' and formula12[i] != '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=(%s%s%s%s%s)'% (formula12[i][0:1],totalRow+10,formula12[i][1:2],formula12[i][2:3],totalRow+10),decimal_format2)

						else:
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),string_format2)

					


				#penulisan printed date

				worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)


				# Penulisan Process Time
				worksheet.write(row2+11,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(row2+12,1,'Since : %s' % (loadDetailReport[7]),font_size)


				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(row2+13,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(row2+13,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(row2+14,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(row2+14,1,'Schedule : -',font_size)
				#Penulisan Creator
				worksheet.write(row2+11,count_header - 3,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()

				return json.dumps(loadDetailReport[5]),200

			elif countFooter == '2':
				print('FOOTER 2')
				#UNTUK MENULIS PENOMORAN
				m = 1

				lengthOfData2 = len(lengthOfData)
				
				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':

					worksheet.merge_range('A10:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					dataSub = 14
					
					
				else:

					try:
						dataSub = 9
						countAwal = 10
					    
					    ######ZONE NEW

						print(lengthOfData2)
						print(countHeaderH2)
						print(formatFooter22)
						print(formula22)
						for i in range(lengthOfData2):
							for x in range(countHeaderH2):

								if formatKolomH2[x] == 'String':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], string_format)
			
								elif formatKolomH2[x] == 'Integer':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], integer_format)

								elif formatKolomH2[x] == 'Decimal':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], decimal_format)
																
								elif formatKolomH2[x] == 'Percentage':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x]*100, decimal_format)
									
								elif formatKolomH2[x] == 'Date':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], date_format)
																	
								elif formatKolomH2[x] == 'Time':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], time_format)
									
								elif formatKolomH2[x] == 'Datetime':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], datetime_format)
									

							dataSub = dataSub + 1

							if data[i][0] != data[i+1][0]:
								subTotal = 0
								
								# Untuk menulis footer
								
								for k in range(countHeaderH2+1):
									worksheet.write(dataSub,k,'',format_header)

								for k in range(lokasiCurr2Len):
									if formatFooter12[k] == 'Integer' and formula12[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
									elif formatFooter12[k] == 'Integer' and formula12[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),integer_format2)

									elif formatFooter12[k] == 'Decimal' and formula12[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter12[k] == 'Decimal' and formula12[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)

									elif formatFooter12[k] == 'Percentage' and formula12[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter12[k] == 'Percentage' and formula12[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)
									
									else:
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)

								
								dataSub = dataSub + 1
								countAwal = dataSub + 1

					######ENDZONE


					except IndexError as e:
						#SUBTOTAL TERAKHIR
						for k in range(countHeaderH2+1):
							worksheet.write(dataSub,k,'',format_header)
						# Untuk menulis footer
						for k in range(lokasiCurr2Len):
							if formatFooter12[k] == 'Integer' and formula12[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
							elif formatFooter12[k] == 'Integer' and formula21[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),integer_format2)

							elif formatFooter12[k] == 'Decimal' and formula12[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter12[k] == 'Decimal' and formula12[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)
							
							elif formatFooter12[k] == 'Percentage' and formula12[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter12[k] == 'Percentage' and formula12[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)

							else:
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)

							
						dataSub = dataSub + 1
						countAwal = dataSub + 1

						#GRANDTOTAL
						for k in range(countHeaderH2+1):
						    		worksheet.write(dataSub,k,'',format_header)
						
						for k in range(lokasiCurr4Len):
							if formatFooter22[k] == 'Integer' and formula22[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),integer_format2)	
							elif formatFooter22[k] == 'Integer' and formula22[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=(%s%s%s%s%s)'% (formula22[k][0:1],dataSub+1,formula22[k][1:2],formula22[k][2:3],dataSub+1),integer_format2)	

							elif formatFooter22[k] == 'Decimal' and formula22[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)
							elif formatFooter22[k] == 'Decimal' and formula22[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=(%s%s%s%s%s)'% (formula22[k][0:1],dataSub+1,formula22[k][1:2],formula22[k][2:3],dataSub+1),decimal_format2)	

							elif formatFooter22[k] == 'Percentage' and formula22[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)	
							elif formatFooter22[k] == 'Percentage' and formula22[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=(%s%s%s%s%s)'% (formula22[k][0:1],dataSub+1,formula22[k][1:2],formula22[k][2:3],dataSub+1),decimal_format2)	

							else:
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								if lokasiCurr3[k] in lokasiCurr:
									worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)	
								else:
									worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)

						dataSub = dataSub+1
						countAwal = dataSub+1



					try:
						row=0
						num = 1
						for i in range(lengthOfData2+1): 
						    if (i == 0):
						        worksheet.write(row + 7,kol,'No',format_headerMid)
						        row = row + 1
						    elif data[i-1][0] == data[i][0]:
						    	worksheet.write(row + 8,kol,num,font_size)
						    	row = row+1
						    	num = num +1
						    else:
						        worksheet.write(row + 8,kol,num,font_size)
						        row = row + 2
						        num = num + 1

					except IndexError as e:
						worksheet.write(row + 8,kol,num,font_size)


			    # Penulisan Process Time
				worksheet.write(dataSub+1,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(dataSub+2,1,'Since : %s' % (loadDetailReport[7]),font_size)

				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(dataSub+3,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(dataSub+3,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(dataSub+4,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(dataSub+4,1,'Schedule : -',font_size)
				#Penulisan Creator
				worksheet.write(dataSub+1,count_header - 3,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()
				return json.dumps(loadDetailReport[5]),200


	except Exception as e:

		err = {
		'error' : str(e)
		}

		print('ERROR2:',err['error'])

		return  json.dumps(err), 400






@app.route('/executeSchedule/<kode_laporan>', methods=['GET','POST'])
def executeSchedule(kode_laporan):
	try:

		tglRun          = datetime.datetime.now().strftime('%x')
		waktuRun        = datetime.datetime.now().strftime('%X')
		
		error_deskripsi = ''
		selesaiRun 		= ''
		runStatus 		= ''
		run_hostname    = socket.gethostname()

		count_header = 0
		waktuproses = datetime.datetime.now().strftime('%X')
		#==============================[ MENDAPATKAN DETAIL REPORT ]============================== 
		detReport       = requests.get('http://127.0.0.1:5002/getDetailReport/'+kode_laporan)
		detRResp        = json.dumps(detReport.json())
		loadDetailReport = json.loads(detRResp)

		getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
		getSchResp = json.dumps(getSch.json())
		loadGetSch = json.loads(getSchResp)

		# MENDAPATKAN JUMLAH HEADER (1 / 2)
		jmlHead = loadDetailReport[6]
		servId = loadDetailReport[9]

		print('=============[EXECUTE SCHEDULE]===============')
		print('Jumlah Header: ',jmlHead)

		dbs = databaseCMS.db_scheduling()
		dbsC = dbs.cursor()

		dbsC.execute("INSERT INTO t_runningLog (run_id, report_id, server_id, org_id, ktgri_id,\
		             report_judul, sch_hari, sch_bulan, sch_tanggal, run_date,\
		             run_startTime, run_endTime, run_status, error_deskripsi,\
		             run_hostname) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(generateRunId(), kode_laporan,\
		                servId, loadDetailReport[5], loadDetailReport[10], loadDetailReport[1], loadGetSch[0], \
		                loadGetSch[1], loadGetSch[2], tglRun, waktuRun, selesaiRun,\
		                runStatus, error_deskripsi, run_hostname))
		dbs.commit()

		dbs.close()
		dbsC.close()

	    #==============================[ MENDAPATKAN DETAIL HEADER ]==============================
		getDetH = requests.get('http://127.0.0.1:5002/getDetailH/'+kode_laporan)
		detHResp = json.dumps(getDetH.json())
		loadDetailH = json.loads(detHResp)

		countHeader     = []
		lebar           = []
		listKolom       = []
		lokasiHeader    = []
		formatKolom     = []
		rataTengah      = []
		rataKanan       = []
		formulaH 		= []
		formatFooterH 	= []
		for i in loadDetailH:
			namaKolom   = i['namaKolom']
			lokasiKolom = i['lokasi']
			forKolom    = i['formatKolom']
			leb         = i['lebarKolom']
			ratTengah   = i['rataTengah']
			ratKanan    = i['rataKanan']
			formulaH1 	= i['formula']

			forFoot = {
			'lokasi' : str(lokasiKolom)[0:1],
			'format' : forKolom
			}
			formatFooterH.append(forFoot)

			# formulaD = {
			# 'lokasi' : str(lokasiKolom)[0:1],
			# 'formula': formulaH1
			# }
			# formulaH.append(formulaD)

			listKolom.append(namaKolom)
			lokasiHeader.append(lokasiKolom)
			formatKolom.append(forKolom)
			lebar.append(leb)
			countHeader.append(namaKolom)
			rataTengah.append(ratTengah)
			rataKanan.append(ratKanan)

		formatFooterH = {'data' : formatFooterH}
		# formulaH = {'data' : formulaH}
		listKolom2      = len(listKolom)
		countHeader2    = len(countHeader)
		print(formatFooterH)
		print('List Kolom : ',listKolom)
		print('Format Kolom : ',formatKolom)
		print('List Lebar : ',lebar)
	    #_________________________________________________________________________________________#
	    
		getDetH2    = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
		detHResp2   = json.dumps(getDetH2.json())
		loadDetailH2 = json.loads(detHResp2)


		listKolomHeader2    = []
		lebarH2             = []
		lokasiH2            = []
		formatKolomH2		= []
		formatFooterH2 		= []
		formulaH2 			= []
		for i in loadDetailH2:
			namaKolomH2     = i['namaKolom']
			lokasi2         = i['lokasi']
			formatKolom2   	= i['formatKolom']
			lebH2           = i['lebarKolom']
			formula2 		=i['formula']

			forFoot2={
			'lokasi2' : str(lokasi2)[0:1],
			'format2' : formatKolom2
			}
			formatFooterH2.append(forFoot2)

			formulaD2 = {
			'lokasi2' : str(lokasi2)[0:1],
			'formula2' : formula2
			}
			formulaH2.append(formulaD2)

			
			listKolomHeader2.append(namaKolomH2)
			lebarH2.append(lebH2)
			lokasiH2.append(lokasi2)
			formatKolomH2.append(formatKolom2)
		formatFooterH2 = {'data' : formatFooterH2}
		formulaH2 = {'data' : formulaH2}
		countHeaderH2 = len(listKolomHeader2)

		print('formulah2', formulaH2)

	    #==============================[ MENDAPATKAN DETAIL PIC ]==============================
		PIC = []
		Penerima = []

		getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+kode_laporan)
		namaResp = json.dumps(getNama.json())
		loadNama = json.loads(namaResp)
		for i in loadNama:
			namaPIC = i['PIC']
			namaPen = i['Pen']
			PIC.append(namaPIC)
			Penerima.append(namaPen)
		PIC = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")
		Penerima = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")

		print('List PIC : ',PIC)
		print('List Penerima : ',Penerima)
		#_________________________________________________________________________________________#




		#==============================[ MENDAPATKAN DETAIL QUERY ]==============================
		getQ = requests.get('http://127.0.0.1:5002/getQuery/'+kode_laporan)
		qResp = json.dumps(getQ.json())
		loadQ = json.loads(qResp)
		

		db = databaseCMS.db_server(loadDetailReport[9])
		cursor = db.cursor(buffered = True)

		listQuery = []
		for i in loadQ:
			reportId    = i['reportId']
			quer        = i['query']
			qno         = i['query_no']

			listQuery.append(quer)

		
		lengthOfQuery = len(listQuery)


		try:
			for i in range (lengthOfQuery):
				sql2 = listQuery[i]
				print(listQuery[i])
				cursor.execute(sql2)          
			result = cursor.fetchall()
			db.close()
			cursor.close()
			#HASIL DARI EXECUTE QUERY
			toExcel = []
			for i in result:
				toExcel.append(i)

		except Exception as e:
			err = {
			'Error execute Query :' : str(e)
			}
			dbs = databaseCMS.db_scheduling()
			selesaiRun      = datetime.datetime.now().strftime('%X')
			cursor = dbs.cursor()
			cursor.execute('UPDATE t_runningLog SET run_endTime ="'+selesaiRun+'",\
			                run_status="G", error_deskripsi="'+str(e)+'" WHERE report_id = "'+kode_laporan+'"\
			                AND run_date ="'+str(tglRun)+'" ')
			dbs.commit()

			dbs.close()
			cursor.close()
			return  json.dumps(err),400


		data = []
		data = toExcel
		

		lengthOfData = [x[0] for x in data]

		totalRow = len(lengthOfData)
		#_________________________________________________________________________________________#

		#======================[ FOOTER ]================================

		getF = requests.get('http://127.0.0.1:5002/getDetailF/'+kode_laporan)
		FResp = json.dumps(getF.json())
		detailFooter = json.loads(FResp)

		countFooter = loadDetailReport[4]

		kolomFooter     = []
		lokasiFooter    = []
		lokasiFooter2	= []

		for row in detailFooter:
			namaKolomF  = row['namaKolom']
			kolomFooter.append(namaKolomF)

			if row['urutan'] == '1':
				lokasi = row['lokasi'].split(", ")	
				lokasiFooter.append(lokasi)
			else:
				lokasi2 = row['lokasi'].split(", ")
				lokasiFooter2.append(lokasi2)

		lokasiFooter = str(lokasiFooter).replace("[[","").replace("]]","").replace("'","").split(", ")
		lokasiFooter2 = str(lokasiFooter2).replace("[[","").replace("]]","").replace("'","").split(", ")



		#=========== UNTUK FOOTER 1
		lokasiCurr      = []
		countOfFooter   = len(lokasiFooter)



		l = 0
		for i in range(countOfFooter):
			if (lokasiFooter[l] == 'B'):
				lokasiCurr.append(1)
			elif(lokasiFooter[l] == 'C'):
				lokasiCurr.append(2)
			elif(lokasiFooter[l] == 'D'):
				lokasiCurr.append(3)
			elif(lokasiFooter[l] == 'E'):
				lokasiCurr.append(4)
			elif(lokasiFooter[l] == 'F'):
				lokasiCurr.append(5)
			elif(lokasiFooter[l] == 'G'):
				lokasiCurr.append(6)
			elif(lokasiFooter[l] == 'H'):
				lokasiCurr.append(7)
			elif(lokasiFooter[l] == 'I'):
				lokasiCurr.append(8)
			elif(lokasiFooter[l] == 'J'):
				lokasiCurr.append(9)
			elif(lokasiFooter[l] == 'K'):
				lokasiCurr.append(10)
			elif(lokasiFooter[l] == 'L'):
				lokasiCurr.append(11)
			elif(lokasiFooter[l] == 'M'):
				lokasiCurr.append(12)
			elif(lokasiFooter[l] == 'N'):
				lokasiCurr.append(13)
			elif(lokasiFooter[l] == 'O'):
				lokasiCurr.append(14)
			elif(lokasiFooter[l] == 'P'):
				lokasiCurr.append(15)
			l = l + 1

		lokasiCurr2 = []
		
		l = 0
		for i in range(countOfFooter):
			if (lokasiFooter[l] == 'B'):
				lokasiCurr2.append('B')
			elif(lokasiFooter[l] == 'C'):
				lokasiCurr2.append('C')
			elif(lokasiFooter[l] == 'D'):
				lokasiCurr2.append('D')
			elif(lokasiFooter[l] == 'E'):
				lokasiCurr2.append('E')
			elif(lokasiFooter[l] == 'F'):
				lokasiCurr2.append('F')
			elif(lokasiFooter[l] == 'G'):
				lokasiCurr2.append('G')
			elif(lokasiFooter[l] == 'H'):
				lokasiCurr2.append('H')
			elif(lokasiFooter[l] == 'I'):
				lokasiCurr2.append('I')
			elif(lokasiFooter[l] == 'J'):
				lokasiCurr2.append('J')
			elif(lokasiFooter[l] == 'K'):
				lokasiCurr2.append('K')
			elif(lokasiFooter[l] == 'L'):
				lokasiCurr2.append('L')
			elif(lokasiFooter[l] == 'M'):
				lokasiCurr2.append('M')
			elif(lokasiFooter[l] == 'N'):
				lokasiCurr2.append('N')
			elif(lokasiFooter[l] == 'O'):
				lokasiCurr2.append('O')
			elif(lokasiFooter[l] == 'P'):
				lokasiCurr2.append('P')
			l = l + 1

		lokasiCurr2Len = len(lokasiCurr2)
		
		formatFooter1 = []
		for i in formatFooterH['data']:
			if i['lokasi'] in lokasiCurr2:
				formatFooter1.append(i['format'])
		print(formatFooterH)
		print(formatFooter1)


		formatFooter12 = []
		for i in formatFooterH2['data']:
			if i['lokasi2'] in lokasiCurr2:
				formatFooter12.append(i['format2'])
		print(formatFooterH2)
		print(formatFooter12)


		#=========== UNTUK FOOTER 2


		lokasiCurr3      = []
		countOfFooter2   = len(lokasiFooter2)

		l = 0
		for i in range(countOfFooter2):
			if (lokasiFooter2[l] == 'B'):
				lokasiCurr3.append(1)
			elif(lokasiFooter2[l] == 'C'):
				lokasiCurr3.append(2)
			elif(lokasiFooter2[l] == 'D'):
				lokasiCurr3.append(3)
			elif(lokasiFooter2[l] == 'E'):
				lokasiCurr3.append(4)
			elif(lokasiFooter2[l] == 'F'):
				lokasiCurr3.append(5)
			elif(lokasiFooter2[l] == 'G'):
				lokasiCurr3.append(6)
			elif(lokasiFooter2[l] == 'H'):
				lokasiCurr3.append(7)
			elif(lokasiFooter2[l] == 'I'):
				lokasiCurr3.append(8)
			elif(lokasiFooter2[l] == 'J'):
				lokasiCurr3.append(9)
			elif(lokasiFooter2[l] == 'K'):
				lokasiCurr3.append(10)
			elif(lokasiFooter2[l] == 'L'):
				lokasiCurr3.append(11)
			elif(lokasiFooter2[l] == 'M'):
				lokasiCurr3.append(12)
			elif(lokasiFooter2[l] == 'N'):
				lokasiCurr3.append(13)
			elif(lokasiFooter2[l] == 'O'):
				lokasiCurr3.append(14)
			elif(lokasiFooter2[l] == 'P'):
				lokasiCurr3.append(15)
			l = l + 1

		lokasiCurr4 = []
		
		l = 0
		for i in range(countOfFooter2):
			if (lokasiFooter2[l] == 'B'):
				lokasiCurr4.append('B')
			elif(lokasiFooter2[l] == 'C'):
				lokasiCurr4.append('C')
			elif(lokasiFooter2[l] == 'D'):
				lokasiCurr4.append('D')
			elif(lokasiFooter2[l] == 'E'):
				lokasiCurr4.append('E')
			elif(lokasiFooter2[l] == 'F'):
				lokasiCurr4.append('F')
			elif(lokasiFooter2[l] == 'G'):
				lokasiCurr4.append('G')
			elif(lokasiFooter2[l] == 'H'):
				lokasiCurr4.append('H')
			elif(lokasiFooter2[l] == 'I'):
				lokasiCurr4.append('I')
			elif(lokasiFooter2[l] == 'J'):
				lokasiCurr4.append('J')
			elif(lokasiFooter2[l] == 'K'):
				lokasiCurr4.append('K')
			elif(lokasiFooter2[l] == 'L'):
				lokasiCurr4.append('L')
			elif(lokasiFooter2[l] == 'M'):
				lokasiCurr4.append('M')
			elif(lokasiFooter2[l] == 'N'):
				lokasiCurr4.append('N')
			elif(lokasiFooter2[l] == 'O'):
				lokasiCurr4.append('O')
			elif(lokasiFooter2[l] == 'P'):
				lokasiCurr4.append('P')
			l = l + 1

		lokasiCurr4Len = len(lokasiCurr4)

		#HEADER 1
		formatFooter2 = []
		for i in formatFooterH['data']:
			if i['lokasi'] in lokasiCurr4:
				formatFooter2.append(i['format'])
		print(formatFooter2)

		formula1 = []
		for i in formulaH['data']:
			if i['lokasi'] in lokasiCurr2:
				formula1.append(i['formula'])
		print(formula1)

		formula2 = []
		for i in formulaH['data']:
			if i['lokasi'] in lokasiCurr4:
				formula2.append(i['formula'])
		print(formula2)




		#HEADER 2
		formatFooter22 = []
		for i in formatFooterH2['data']:
			if i['lokasi2'] in lokasiCurr4:
				formatFooter22.append(i['format2'])

		formula12 = []
		for i in formulaH2['data']:
			if i['lokasi2'] in lokasiCurr2:
				formula12.append(i['formula2'])

		formula22 = []
		for i in formulaH2['data']:
			if i['lokasi2'] in lokasiCurr4:
				formula22.append(i['formula2'])

		#_________________________________________________________________________________________#
		print('COUNT OF FOOTER 1: ',countOfFooter)
		print('COUNT OF FOOTER 2: ',countOfFooter2)
		print('LOKASI FOOTER 1 : ', lokasiCurr2)
		print('LOKASI FOOTER 2 : ', lokasiCurr4)
		print('LOKASI FOOTER 1 LEN : ', lokasiCurr2Len)
		print('LOKASI FOOTER 2 LEN : ', lokasiCurr4Len)



		if not os.path.exists(app.config['FOLDER_SCHEDULE']):
			os.makedirs(app.config['FOLDER_SCHEDULE'])


		namaFileExcel =  kode_laporan+'_'+loadDetailReport[5]+datetime.datetime.now().strftime('%d%m%Y')

		workbook 	= xlsxwriter.Workbook(app.config['FOLDER_SCHEDULE']+'/%s.xls'% (namaFileExcel))
		worksheet 	= workbook.add_worksheet()

		#=======================[STYLE]========================================================
		string_format 	= workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman'})
		string_format2 	= workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman','top':1,'bottom':1,'hidden':True})
		integer_format 	= workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman'})
		integer_format2 = workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman','top':1,'bottom':1,'hidden':True})
		decimal_format 	= workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman'})
		decimal_format2 = workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman','top':1,'bottom':1,'hidden':True})
		date_format 	= workbook.add_format({'num_format': 15,'font_size':8,'font_name':'Times New Roman'})
		time_format 	= workbook.add_format({'num_format': 21,'font_size':8,'font_name':'Times New Roman'})
		datetime_format = workbook.add_format({'num_format': 22,'font_size':8,'font_name':'Times New Roman'})

		font_size 			= workbook.add_format({'font_size':8,'font_name':'Times New Roman'})
		format_header 		= workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True,'font_name':'Times New Roman'})
		format_headerMid 	= workbook.add_format({'font_size':8,'top':1,'bold':True,'align' : 'center','valign' : 'center','font_name':'Times New Roman'})
		format_headerBot 	= workbook.add_format({'font_size':8,'bottom':1,'bold':True,'align' : 'center','valign' : 'center','font_name':'Times New Roman'})
		category_style 		= workbook.add_format({'font_size':8,'align':'right','font_name':'Times New Roman'})
		merge_format 		= workbook.add_format({'bold':2, 'align' : 'center', 'valign' : 'vcenter', 'font_size':10,'font_name':'Times New Roman'})
		merge_formatEmpty 	= workbook.add_format({'bold':2, 'align' : 'center', 'valign' : 'vcenter', 'font_size':10, 'top':1, 'bottom':1,'font_name':'Times New Roman'})
		bold 				= workbook.add_format({'bold':True,'font_size':8,'font_name':'Times New Roman'})
	    ##################################


		if jmlHead == '1':
			print('HEAD 1')

			listMaxCol  = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
			maxCol      = (listMaxCol[countHeader2])



			nOrg        = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
			orgResp     = json.dumps(nOrg.json())
			loadNamaOrg = json.loads(orgResp)
			for i in loadNamaOrg:
				namaOrg = i['org_name']

			listColWidth    =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
			colWidth        = (listColWidth[0:countHeader2])

			colWidth2 		= (listColWidth[countHeader2-1])

			worksheet.merge_range('A1:%s'%(maxCol),'%s'%(namaOrg), merge_format) 
			worksheet.write('A2','%s' % (loadDetailReport[1]),bold ) #nama report
			worksheet.write('A3','Report Code : %s' % (loadDetailReport[0]),font_size) #kode report
			worksheet.write('A4','PIC : %s' % (PIC),font_size)
			worksheet.write('A5','Penerima : %s' % (Penerima),font_size)
			worksheet.write('A6','Filter : %s' % (loadDetailReport[2]), bold ) #filter
			worksheet.write('A7','Period : %s' % (loadDetailReport[3]),font_size) #periode
			worksheet.repeat_rows(7)  
			#penulisan printed date
			worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

			row = 0
			kol = 0

			kolom = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
			row2 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


			kolomList   = (kolom[0:countHeader2])
			rowList     = (row2[0:countHeader2])
			j = 1

			#ini untuk menulis header

			#sebelumnya for i in countHeader

			lok = 0
			

			if countFooter == '1' or countFooter == '' or countFooter is None:
				print('FOOTER 1')
				for i in (listKolom): 
					worksheet.write(lokasiHeader[lok],i,format_header)
					lok             = lok + 1
					count_header    = count_header + 1

				#end menulis header
				#Untuk mengatur lebar Kolom
				for i in range(countHeader2):
					worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))


				#UNTUK MENULIS PENOMORAN
				# lengthOfData = [x[0] for x in data]
				lengthOfData2 = len(lengthOfData)
				num = 1

				for i in range(lengthOfData2+1): 
					if (i == 0):
						worksheet.write(row + 7,kol,'No',format_header)
						row = row + 1
					else:
						worksheet.write(row + 7,kol,num,font_size)
						row = row + 1
						num = num + 1

				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':

					worksheet.merge_range('A9:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					row2 = 0
					row2 = row2 + 4

				else:
					
					# UNTUK MENULIS DATA
					m = 1
					row2 = 0

					######ZONE NEW
					rowString 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowInt 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDec 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowPer 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDate 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowTime 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDateTime = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	

					for i in range(lengthOfData2):
						for x in range(listKolom2):
							if formatKolom[x] == 'String':
								worksheet.write('%s%s'%(listColWidth[x],rowString[x]+9),data[i][x], string_format)
								rowString[x] = rowString[x] + 1
								

							elif formatKolom[x] == 'Integer':
								worksheet.write('%s%s'%(listColWidth[x],rowInt[x]+9),data[i][x], integer_format)
								rowInt[x] = rowInt[x] + 1

							elif formatKolom[x] == 'Decimal':
								worksheet.write('%s%s'%(listColWidth[x],rowDec[x]+9),data[i][x], decimal_format)
								rowDec[x] = rowDec[x] + 1

							elif formatKolom[x] == 'Percentage':
								worksheet.write('%s%s'%(listColWidth[x],rowPer[x]+9),data[i][x]*100, decimal_format)
								rowPer[x] = rowPer[x] + 1

							elif formatKolom[x] == 'Date':
								worksheet.write('%s%s'%(listColWidth[x],rowDate[x]+9),data[i][x], date_format)
								rowDate[x] = rowDate[x] + 1

							elif formatKolom[x] == 'Time':
								worksheet.write('%s%s'%(listColWidth[x],rowTime[x]+9),data[i][x], time_format)
								rowTime[x] = rowTime[x] + 1

							elif formatKolom[x] == 'Datetime':
								worksheet.write('%s%s'%(listColWidth[x],rowDateTime[x]+9),data[i][x], datetime_format)
								rowDateTime[x] = rowDateTime[x] + 1
						row2=row2+1

					######ENDZONE

					for i in range(countHeader2+1):
						worksheet.write(row2+8,i,'',format_header)
					for i in range(lokasiCurr2Len):
						if formatFooter1[i] == 'Integer' and formula1[i] == '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),integer_format2)
						elif formatFooter1[i] == 'Integer' and formula1[i] != '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=(%s%s%s%s)'% (formula1[i][0:1],totalRow+8,formula1[i][1:2],formula1[i][2:3],totalRow+8),integer_format2)

						elif formatFooter1[i] == 'Decimal' and formula1[i] == '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),decimal_format2)
						elif formatFooter1[i] == 'Decimal' and formula1[i] != '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=(%s%s%s%s)'% (formula1[i][0:1],totalRow+8,formula1[i][1:2],formula1[i][2:3],totalRow+8),decimal_format2)

						elif formatFooter1[i] == 'Percentage' and formula1[i] == '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),decimal_format2)
						elif formatFooter1[i] == 'Percentage' and formula1[i] != '':
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=(%s%s%s%s)'% (formula1[i][0:1],totalRow+8,formula1[i][1:2],formula1[i][2:3],totalRow+8),decimal_format2)

						else:
							worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),string_format2)
					



				worksheet.write(row2+10,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(row2+11,1,'Since : %s' % (loadDetailReport[7]),font_size)
				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(row2+12,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(row2+12,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(row2+13,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(row2+13,1,'Schedule : -',font_size)
				#Penulisan Creator
				worksheet.write(row2+10,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()

				try:
					selesaiRun      = datetime.datetime.now().strftime('%X')
					db      = databaseCMS.db_scheduling()
					cursor  = db.cursor()
					cursor.execute('UPDATE t_runningLog SET run_endTime = "'+selesaiRun+'",\
					                run_status="B" WHERE report_id = "'+kode_laporan+'"\
					                AND run_date ="'+str(tglRun)+'" ')
					db.commit()
				except Error as e :
				    print("Error while connecting file MySQL", e)
				finally:
				        #Closing DB Connection.
				            if(db.is_connected()):
				                cursor.close()
				                db.close()
				            print("MySQL connection is closed")
				eml = requests.get('http://127.0.0.1:5002/listPIC/'+kode_laporan)
				emlResp = json.dumps(eml.json())
				loadEml = json.loads(emlResp)

				listEmailPIC = []
				listEmailPen = []
				for k in loadEml:
				    listEmPIC = k['PIC']
				    listEmPen = k['Pen']
				    listEmailPIC.append(listEmPIC)
				    listEmailPen.append(listEmPen)

				dataSend = []
				dataUpdate= {
				'kode_laporan'  : kode_laporan,
				'org_id'        : loadDetailReport[5],
				'namaFile'      : namaFileExcel,
				'PIC'           : ', '.join(listEmailPIC),
				'Penerima'      : ', '.join(listEmailPen),
				'reportJudul'   : loadDetailReport[1]
				}
				dataSend.append(dataUpdate)
				dataSendMS4 =  json.dumps(dataSend)

				requests.post('http://127.0.0.1:5004/updateReport/'+dataSendMS4)

				return json.dumps(loadDetailReport[5]),200


			elif countFooter == '2':
				print('FOOTER 2')

				for i in (listKolom): 
					worksheet.write(lokasiHeader[lok],i,format_header)
					lok             = lok + 1
					count_header    = count_header + 1

				#end menulis header
				#Untuk mengatur lebar Kolom
				for i in range(countHeader2):
					worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))
					
				#UNTUK MENULIS PENOMORAN
				m = 1
				
				lengthOfData = [x[0] for x in data]
				lengthOfData2 = len(lengthOfData)
				
				


				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':
					worksheet.merge_range('A9:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					dataSub = 13
					
					
				else:

					try:
						dataSub = 8
						countAwal = 9

					

						for i in range(lengthOfData2):
							for x in range(countHeader2):

								if formatKolom[x] == 'String':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], string_format)
																	
								elif formatKolom[x] == 'Integer':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], integer_format)
								elif formatKolom[x] == 'Decimal':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], decimal_format)
																		
								elif formatKolom[x] == 'Percentage':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x]*100, decimal_format)
									
								elif formatKolom[x] == 'Date':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], date_format)
																	
								elif formatKolom[x] == 'Time':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], time_format)
									
								elif formatKolom[x] == 'Datetime':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], datetime_format)
									
							print('asdasdsadassd')
							dataSub = dataSub + 1

							if data[i][0] != data[i+1][0]:
								subTotal = 0
								for k in range(countHeader2+1):
									worksheet.write(dataSub,k,'',format_header)
								

								for k in range(lokasiCurr2Len):
									
									if formatFooter1[k] == 'Integer' and formula1[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
									elif formatFooter1[k] == 'Integer' and formula1[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),integer_format2)

									elif formatFooter1[k] == 'Decimal' and formula1[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter1[k] == 'Decimal' and formula1[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)

									elif formatFooter1[k] == 'Percentage' and formula1[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter1[k] == 'Percentage' and formula1[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)

									else:
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)
	

								dataSub = dataSub + 1
								countAwal = dataSub + 1



					except IndexError as e:
						
						#SUBTOTAL TERAKHIR
						for k in range(countHeader2+1):
							worksheet.write(dataSub,k,'',format_header)
						# Untuk menulis footer
						for k in range(lokasiCurr2Len):
							if formatFooter1[k] == 'Integer' and formula1[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
							elif formatFooter1[k] == 'Integer' and formula1[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),integer_format2)

							elif formatFooter1[k] == 'Decimal' and formula1[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter1[k] == 'Decimal' and formula1[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)
							
							elif formatFooter1[k] == 'Percentage' and formula1[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter1[k] == 'Percentage' and formula1[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula1[k][0:1],dataSub+1,formula1[k][1:2],formula1[k][2:3],dataSub+1),decimal_format2)

							else:
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)
						
						#GRANDTOTAL
						dataSub = dataSub + 1
						countAwal = dataSub + 1
						
						for k in range(countHeader2+1):
							worksheet.write(dataSub,k,'',format_header)

				    	
						for k in range(lokasiCurr4Len):
							if formatFooter2[k] == 'Integer' and formula2[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),integer_format2)	
							elif formatFooter2[k] == 'Integer' and formula2[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s%s%s%s%s)'% (formula2[k][0:1],dataSub+1,formula2[k][1:2],formula2[k][2:3],dataSub+1),integer_format2)	
							
							elif formatFooter2[k] == 'Decimal' and formula2[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)
							elif formatFooter2[k] == 'Decimal' and formula2[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s%s%s%s%s)'% (formula2[k][0:1],dataSub+1,formula2[k][1:2],formula2[k][2:3],dataSub+1),decimal_format2)	

							elif formatFooter2[k] == 'Percentage' and formula2[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)	
							elif formatFooter2[k] == 'Percentage' and formula2[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s%s%s%s%s)'% (formula2[k][0:1],dataSub+1,formula2[k][1:2],formula2[k][2:3],dataSub+1),decimal_format2)	

							else:
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								if lokasiCurr3[k] in lokasiCurr:
									worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)	
								else:
									worksheet.write_formula(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)	
						dataSub = dataSub+1
						countAwal = dataSub+1
						
						print(dataSub)


					try:
						row=0
						num = 1
						for i in range(lengthOfData2+1): 
						    if (i == 0):
						        worksheet.write(row + 7,kol,'No',format_header)
						        row = row + 1
						    elif data[i-1][0] == data[i][0]:
						    	worksheet.write(row + 7,kol,num,font_size)
						    	row = row+1
						    	num = num +1
						    	
						    else:
						        worksheet.write(row + 7,kol,num,font_size)
						        row = row + 2
						        num = num + 1

					except IndexError as e:
						worksheet.write(row + 7,kol,num,font_size)

			    # Penulisan Process Time
				worksheet.write(dataSub+1,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(dataSub+2,1,'Since : %s' % (loadDetailReport[7]),font_size)

				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(dataSub+3,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(dataSub+3,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(dataSub+4,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(dataSub+4,1,'Schedule : -',font_size)

				#Penulisan Creator
				worksheet.write(dataSub+1,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()

				try:
					selesaiRun      = datetime.datetime.now().strftime('%X')
					db      = databaseCMS.db_scheduling()
					cursor  = db.cursor()
					cursor.execute('UPDATE t_runningLog SET run_endTime = "'+selesaiRun+'",\
					                run_status="B" WHERE report_id = "'+kode_laporan+'"\
					                AND run_date ="'+str(tglRun)+'" ')
					db.commit()
				except Error as e :
				    print("Error while connecting file MySQL", e)
				finally:
				        #Closing DB Connection.
				            if(db.is_connected()):
				                cursor.close()
				                db.close()
				            print("MySQL connection is closed")
				eml = requests.get('http://127.0.0.1:5002/listPIC/'+kode_laporan)
				emlResp = json.dumps(eml.json())
				loadEml = json.loads(emlResp)

				listEmailPIC = []
				listEmailPen = []
				for k in loadEml:
				    listEmPIC = k['PIC']
				    listEmPen = k['Pen']
				    listEmailPIC.append(listEmPIC)
				    listEmailPen.append(listEmPen)

				dataSend = []
				dataUpdate= {
				'kode_laporan'  : kode_laporan,
				'org_id'        : loadDetailReport[5],
				'namaFile'      : namaFileExcel,
				'PIC'           : ', '.join(listEmailPIC),
				'Penerima'      : ', '.join(listEmailPen),
				'reportJudul'   : loadDetailReport[1]
				}
				dataSend.append(dataUpdate)
				dataSendMS4 =  json.dumps(dataSend)

				requests.post('http://127.0.0.1:5004/updateReport/'+dataSendMS4)

				return json.dumps(loadDetailReport[5]),200



		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================
		#======================================================================================


		elif jmlHead == '2':
			print('HEAD 2')

			getDetH2    = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
			detHResp2   = json.dumps(getDetH2.json())
			loadDetailH2 = json.loads(detHResp2)


			listKolomHeader2    = []
			lebarH2             = []
			lokasiH2            = []
			formatKolomH2		= []
			# formulaH2 			= []
			for i in loadDetailH2:
			    namaKolomH2     = i['namaKolom']
			    lokasi2         = i['lokasi']
			    formatKolom2   	= i['formatKolom']
			    lebH2           = i['lebarKolom']
			    # formula2 		=i['formula']


			    # formulaH2.append(formula2)
			    listKolomHeader2.append(namaKolomH2)
			    lebarH2.append(lebH2)
			    lokasiH2.append(lokasi2)
			    formatKolomH2.append(formatKolom2)

			countHeaderH2 = len(listKolomHeader2)

			mCell = i['formatMerge'].replace('-',':').replace(' ','').split(',')

			for i in range(len(mCell)):
			    worksheet.merge_range('%s'%(mCell[i]),'%s'%(''), format_headerMid)


			lok = 0
			#HEADER 1
			for i in (listKolom): 
			    worksheet.write(lokasiHeader[lok],i,format_headerMid)
			    lok = lok + 1
			    count_header = count_header + 1

			#HEADER 2
			lok2 = 0
			for x in (listKolomHeader2):
			    worksheet.write(lokasiH2[lok2], x,format_header)
			    lok2 = lok2 + 1
			    count_header = count_header + 1


			lengthOfData2 = len(lengthOfData)



			#Mengatur bagian atas dari laporan

			listMaxCol = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
			maxCol = (listMaxCol[countHeaderH2])
		         

			listColWidth =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
			colWidth = (listColWidth[0:countHeader2])

			colWidth2 = (listColWidth[countHeaderH2-1])



			nOrg        = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
			orgResp     = json.dumps(nOrg.json())
			loadNamaOrg = json.loads(orgResp)
			for i in loadNamaOrg:
				namaOrg = i['org_name']

			worksheet.merge_range('A1:%s'%(maxCol),'%s'%(namaOrg), merge_format) 
			worksheet.write('A2','%s' % (loadDetailReport[1]),bold ) #nama report
			worksheet.write('A3','Report Code : %s' % (loadDetailReport[0]),font_size) #kode report
			worksheet.write('A4','PIC : %s' % (PIC),font_size)
			worksheet.write('A5','Penerima : %s' % (Penerima),font_size)
			worksheet.write('A6','Filter : %s' % (loadDetailReport[2]), bold ) #filter
			worksheet.write('A7','Period : %s' % (loadDetailReport[3]),font_size) #periode
			worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)


			worksheet.repeat_rows(7,8)

			#Untuk mengatur lebar Kolom
			for i in range(countHeader2):
			    worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))

			row = 0
			kol = 0

			kolom = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
			row2 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


			kolomList = (kolom[0:countHeader2])
			rowList = (row2[0:countHeader2])
			j = 1


			if countFooter == '1' or countFooter == '' or countFooter is None:
				print('FOOTER 1')
				num = 1
				for i in range(lengthOfData2+2): #untuk menulis penomoran 1 s/d banyak data
				    if (i == 0):
				        worksheet.write(row + 7,kol,'No',format_headerMid)
				        row = row + 1
				    elif (i == 1):
				    	worksheet.write(row + 7, kol, '', format_headerBot)
				    else:
				        worksheet.write(row + 8,kol,num,font_size)
				        row = row + 1
				        num = num + 1

				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':


					worksheet.merge_range('A10:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					row2 = 0
					row2 = row2 + 4

				else:

					m = 1
					row2 = 0

					######ZONE NEW
					rowString 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowInt 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDec 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowPer 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDate 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowTime 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					rowDateTime = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

					
					for i in range(lengthOfData2):
						for x in range(countHeaderH2):
							
							if formatKolomH2[x] == 'String':
								worksheet.write('%s%s'%(listColWidth[x],rowString[x]+10),data[i][x], string_format)
								rowString[x] = rowString[x] + 1
								
							elif formatKolomH2[x] == 'Integer':
								worksheet.write('%s%s'%(listColWidth[x],rowInt[x]+10),data[i][x], integer_format)
								rowInt[x] = rowInt[x] + 1
								
							elif formatKolomH2[x] == 'Decimal':
								worksheet.write('%s%s'%(listColWidth[x],rowDec[x]+10),data[i][x], decimal_format)
								rowDec[x] = rowDec[x] + 1
								
							elif formatKolomH2[x] == 'Percentage':
								worksheet.write('%s%s'%(listColWidth[x],rowPer[x]+10),data[i][x]*100, decimal_format)
								rowPer[x] = rowPer[x] + 1
								
							elif formatKolomH2[x] == 'Date':
								worksheet.write('%s%s'%(listColWidth[x],rowDate[x]+10),data[i][x], date_format)
								rowDate[x] = rowDate[x] + 1
								
							elif formatKolomH2[x] == 'Time':
								worksheet.write('%s%s'%(listColWidth[x],rowTime[x]+10),data[i][x], time_format)
								rowTime[x] = rowTime[x] + 1
								
							elif formatKolomH2[x] == 'Datetime':
								worksheet.write('%s%s'%(listColWidth[x],rowDateTime[x]+10),data[i][x], datetime_format)
								rowDateTime[x] = rowDateTime[x] + 1
								
						row2=row2+1
				
					######ENDZONE
					print('ASASASA')
					print(lokasiCurr2)
					print(formatFooter12)
					print(formula12)
					for i in range(countHeaderH2+1):
						worksheet.write(row2+9,i,'',format_header)
				
					for i in range(lokasiCurr2Len):
						if formatFooter12[i] == 'Integer' and formula12[i] == '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),integer_format2)
						elif formatFooter12[i] == 'Integer' and formula12[i] != '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=(%s%s%s%s%s)'% (formula12[i][0:1],totalRow+10,formula12[i][1:2],formula12[i][2:3],totalRow+10),integer_format2)

						elif formatFooter12[i] == 'Decimal' and formula12[i] == '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),decimal_format2)
						elif formatFooter12[i] == 'Decimal' and formula12[i] != '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=(%s%s%s%s%s)'% (formula12[i][0:1],totalRow+10,formula12[i][1:2],formula12[i][2:3],totalRow+10),decimal_format2)
						
						elif formatFooter12[i] == 'Percentage' and formula12[i] == '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),decimal_format2)
						elif formatFooter12[i] == 'Percentage' and formula12[i] != '':
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=(%s%s%s%s%s)'% (formula12[i][0:1],totalRow+10,formula12[i][1:2],formula12[i][2:3],totalRow+10),decimal_format2)

						else:
							worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),string_format2)

					


				#penulisan printed date

				worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)


				# Penulisan Process Time
				worksheet.write(row2+11,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(row2+12,1,'Since : %s' % (loadDetailReport[7]),font_size)


				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(row2+13,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(row2+13,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(row2+14,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(row2+14,1,'Schedule : -',font_size)
				#Penulisan Creator
				worksheet.write(row2+11,count_header - 3,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()

				try:
					selesaiRun      = datetime.datetime.now().strftime('%X')
					db      = databaseCMS.db_scheduling()
					cursor  = db.cursor()
					cursor.execute('UPDATE t_runningLog SET run_endTime = "'+selesaiRun+'",\
					                run_status="B" WHERE report_id = "'+kode_laporan+'"\
					                AND run_date ="'+str(tglRun)+'" ')
					db.commit()
				except Error as e :
				    print("Error while connecting file MySQL", e)
				finally:
				        #Closing DB Connection.
				            if(db.is_connected()):
				                cursor.close()
				                db.close()
				            print("MySQL connection is closed")
				eml = requests.get('http://127.0.0.1:5002/listPIC/'+kode_laporan)
				emlResp = json.dumps(eml.json())
				loadEml = json.loads(emlResp)

				listEmailPIC = []
				listEmailPen = []
				for k in loadEml:
				    listEmPIC = k['PIC']
				    listEmPen = k['Pen']
				    listEmailPIC.append(listEmPIC)
				    listEmailPen.append(listEmPen)

				dataSend = []
				dataUpdate= {
				'kode_laporan'  : kode_laporan,
				'org_id'        : loadDetailReport[5],
				'namaFile'      : namaFileExcel,
				'PIC'           : ', '.join(listEmailPIC),
				'Penerima'      : ', '.join(listEmailPen),
				'reportJudul'   : loadDetailReport[1]
				}
				dataSend.append(dataUpdate)
				dataSendMS4 =  json.dumps(dataSend)

				requests.post('http://127.0.0.1:5004/updateReport/'+dataSendMS4)

				return json.dumps(loadDetailReport[5]),200

			elif countFooter == '2':
				print('FOOTER 2')
				#UNTUK MENULIS PENOMORAN
				m = 1

				lengthOfData2 = len(lengthOfData)
				
				if str(lengthOfData2) == '0' or str(lengthOfData2) == '':

					worksheet.merge_range('A10:%s13'%(colWidth2),'Tidak ada detail untuk laporan %s, %s'%(loadDetailReport[0], loadDetailReport[1]), merge_formatEmpty)
					dataSub = 14
					
					
				else:

					try:
						dataSub = 9
						countAwal = 10
					    
					    ######ZONE NEW

						print(lengthOfData2)
						print(countHeaderH2)
						print(formatFooter22)
						print(formula22)
						for i in range(lengthOfData2):
							for x in range(countHeaderH2):

								if formatKolomH2[x] == 'String':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], string_format)
			
								elif formatKolomH2[x] == 'Integer':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], integer_format)

								elif formatKolomH2[x] == 'Decimal':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], decimal_format)
																
								elif formatKolomH2[x] == 'Percentage':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x]*100, decimal_format)
									
								elif formatKolomH2[x] == 'Date':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], date_format)
																	
								elif formatKolomH2[x] == 'Time':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], time_format)
									
								elif formatKolomH2[x] == 'Datetime':
									worksheet.write('%s%s'%(listColWidth[x],dataSub+1),data[i][x], datetime_format)
									

							dataSub = dataSub + 1

							if data[i][0] != data[i+1][0]:
								subTotal = 0
								
								# Untuk menulis footer
								
								for k in range(countHeaderH2+1):
									worksheet.write(dataSub,k,'',format_header)

								for k in range(lokasiCurr2Len):
									if formatFooter12[k] == 'Integer' and formula12[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
									elif formatFooter12[k] == 'Integer' and formula12[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),integer_format2)

									elif formatFooter12[k] == 'Decimal' and formula12[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter12[k] == 'Decimal' and formula12[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)

									elif formatFooter12[k] == 'Percentage' and formula12[k] == '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
									elif formatFooter12[k] == 'Percentage' and formula12[k] != '':
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)
									
									else:
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)

								
								dataSub = dataSub + 1
								countAwal = dataSub + 1

					######ENDZONE


					except IndexError as e:
						#SUBTOTAL TERAKHIR
						for k in range(countHeaderH2+1):
							worksheet.write(dataSub,k,'',format_header)
						# Untuk menulis footer
						for k in range(lokasiCurr2Len):
							if formatFooter12[k] == 'Integer' and formula12[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format2)
							elif formatFooter12[k] == 'Integer' and formula21[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),integer_format2)

							elif formatFooter12[k] == 'Decimal' and formula12[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter12[k] == 'Decimal' and formula12[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)
							
							elif formatFooter12[k] == 'Percentage' and formula12[k] == '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format2)
							elif formatFooter12[k] == 'Percentage' and formula12[k] != '':
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formula12[k][0:1],dataSub+1,formula12[k][1:2],formula12[k][2:3],dataSub+1),decimal_format2)

							else:
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format2)

							
						dataSub = dataSub + 1
						countAwal = dataSub + 1

						#GRANDTOTAL
						for k in range(countHeaderH2+1):
						    		worksheet.write(dataSub,k,'',format_header)
						
						for k in range(lokasiCurr4Len):
							if formatFooter22[k] == 'Integer' and formula22[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),integer_format2)	
							elif formatFooter22[k] == 'Integer' and formula22[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=(%s%s%s%s%s)'% (formula22[k][0:1],dataSub+1,formula22[k][1:2],formula22[k][2:3],dataSub+1),integer_format2)	

							elif formatFooter22[k] == 'Decimal' and formula22[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)
							elif formatFooter22[k] == 'Decimal' and formula22[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=(%s%s%s%s%s)'% (formula22[k][0:1],dataSub+1,formula22[k][1:2],formula22[k][2:3],dataSub+1),decimal_format2)	

							elif formatFooter22[k] == 'Percentage' and formula22[k] == '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format2)	
							elif formatFooter22[k] == 'Percentage' and formula22[k] != '':
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								worksheet.write(dataSub,lokasiCurr3[k],'=(%s%s%s%s%s)'% (formula22[k][0:1],dataSub+1,formula22[k][1:2],formula22[k][2:3],dataSub+1),decimal_format2)	

							else:
								worksheet.write(dataSub,k,'',format_header)
								worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
								if lokasiCurr3[k] in lokasiCurr:
									worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)/2'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)	
								else:
									worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format2)

						dataSub = dataSub+1
						countAwal = dataSub+1



					try:
						row=0
						num = 1
						for i in range(lengthOfData2+1): 
						    if (i == 0):
						        worksheet.write(row + 7,kol,'No',format_headerMid)
						        row = row + 1
						    elif data[i-1][0] == data[i][0]:
						    	worksheet.write(row + 8,kol,num,font_size)
						    	row = row+1
						    	num = num +1
						    else:
						        worksheet.write(row + 8,kol,num,font_size)
						        row = row + 2
						        num = num + 1

					except IndexError as e:
						worksheet.write(row + 8,kol,num,font_size)


			    # Penulisan Process Time
				worksheet.write(dataSub+1,1,'Process Time : %s s/d %s' % (waktuproses, datetime.datetime.now().strftime('%X')),font_size)

				#Penulisan Since
				worksheet.write(dataSub+2,1,'Since : %s' % (loadDetailReport[7]),font_size)

				#Penulisan Note
				getNote      = requests.get('http://127.0.0.1:5002/getNote/'+kode_laporan)
				getNoteResp = json.dumps(getNote.json())
				loadNote = json.loads(getNoteResp)

				if loadNote:
					worksheet.write(dataSub+3,1,'Note : %s' % (loadNote[0]),font_size)
				else:
					worksheet.write(dataSub+3,1,'Note : -',font_size)

				#Penulisan Schedule
				getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
				getSchResp = json.dumps(getSch.json())
				loadGetSch = json.loads(getSchResp)

				if loadGetSch:
				    worksheet.write(dataSub+4,1,'Schedule : %s / %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
				else:
					worksheet.write(dataSub+4,1,'Schedule : -',font_size)
				#Penulisan Creator
				worksheet.write(dataSub+1,count_header - 3,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()
				try:
					selesaiRun      = datetime.datetime.now().strftime('%X')
					db      = databaseCMS.db_scheduling()
					cursor  = db.cursor()
					cursor.execute('UPDATE t_runningLog SET run_endTime = "'+selesaiRun+'",\
					                run_status="B" WHERE report_id = "'+kode_laporan+'"\
					                AND run_date ="'+str(tglRun)+'" ')
					db.commit()
				except Error as e :
				    print("Error while connecting file MySQL", e)
				finally:
				        #Closing DB Connection.
				            if(db.is_connected()):
				                cursor.close()
				                db.close()
				            print("MySQL connection is closed")

				eml = requests.get('http://127.0.0.1:5002/listPIC/'+kode_laporan)
				emlResp = json.dumps(eml.json())
				loadEml = json.loads(emlResp)

				listEmailPIC = []
				listEmailPen = []
				for k in loadEml:
				    listEmPIC = k['PIC']
				    listEmPen = k['Pen']
				    listEmailPIC.append(listEmPIC)
				    listEmailPen.append(listEmPen)

				dataSend = []
				dataUpdate= {
				'kode_laporan'  : kode_laporan,
				'org_id'        : loadDetailReport[5],
				'namaFile'      : namaFileExcel,
				'PIC'           : ', '.join(listEmailPIC),
				'Penerima'      : ', '.join(listEmailPen),
				'reportJudul'   : loadDetailReport[1]
				}
				dataSend.append(dataUpdate)
				dataSendMS4 =  json.dumps(dataSend)

				requests.post('http://127.0.0.1:5004/updateReport/'+dataSendMS4)
				return json.dumps(loadDetailReport[5]),200


	except Exception as e:

		err = {
		'error' : str(e)
		}

		print('ERROR2:',err['error'])
		selesaiRun      = datetime.datetime.now().strftime('%X')
		db =databaseCMS.db_scheduling()
		cursor = db.cursor()
		cursor.execute('UPDATE t_runningLog SET run_endTime ="'+selesaiRun+'",\
		                run_status="G", error_deskripsi="'+str(e)+'" WHERE report_id = "'+kode_laporan+'"\
		                AND run_date ="'+str(tglRun)+'" ')
		db.commit()

		return  json.dumps(err), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port='5003')            
    scheduler.start()