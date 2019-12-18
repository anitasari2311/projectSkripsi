from flask import Flask, json, session, flash,send_from_directory
import datetime
import mysql.connector
from mysql.connector import Error
from db import databaseCMS
import json
import requests
import xlsxwriter
import os
# from flask_apscheduler import APScheduler
# from apscheduler.scheduler import BlockingScheduler
import socket



app = Flask(__name__, static_folder='app/static')


app.static_folder = 'static'
app.secret_key = 'ms3'


app.config['FOLDER_PREVIEW'] = 'previewReport'
app.config['FOLDER_SCHEDULE'] = 'Schedule'

micro2 = 'http://127.0.0.1:5002/'




@app.route('/runScheduleToday')
def runScheduleToday():
	def getScheduleToday():

		kodeToday 	= requests.get(micro2+'getKodeReportRunToday')
		resp 		= json.dumps(kodeToday.json())
		result 		= json.loads(resp)

		listKode = []
		for i in result:
			kode = i['reportId']
			listKode.append(kode)

		return listKode

	k=1
	while len(getScheduleToday()) > 1:
		print("Schedule ",k)
		k=k+1
		runScheduleToday()

	return 'Tidak ada report untuk dijalankan'








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
			formula1 	= i['formula']

			forFoot = {
			'lokasi' : str(lokasiKolom)[0:1],
			'format' : forKolom
			}
			formatFooterH.append(forFoot)

			listKolom.append(namaKolom)
			lokasiHeader.append(lokasiKolom)
			formatKolom.append(forKolom)
			lebar.append(leb)
			formulaH.append(formula1)
			countHeader.append(namaKolom)
			rataTengah.append(ratTengah)
			rataKanan.append(ratKanan)
		formatFooterH = {'data' : formatFooterH}
		listKolom2      = len(listKolom)
		countHeader2    = len(countHeader)
		print(formatFooterH)
		print('List Kolom : ',listKolom)
		print('Format Kolom : ',formatKolom)
		print('List Lebar : ',lebar)
	    #_________________________________________________________________________________________#

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

		print(formatFooter1)


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


		formatFooter2 = []
		for i in formatFooterH['data']:
			if i['lokasi'] in lokasiCurr4:
				formatFooter2.append(i['format'])
		print(formatFooter2)
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

		workbook = xlsxwriter.Workbook(app.config['FOLDER_PREVIEW']+'/%s.xls'% (namaFileExcel))
		worksheet = workbook.add_worksheet()

		#=======================[STYLE]========================================================
		font_size = workbook.add_format({'font_size':8,'font_name':'Times New Roman'})
		format_header = workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True,'font_name':'Times New Roman'})
		format_headerMid = workbook.add_format({'font_size':8,'top':1,'bold':True,'align' : 'center','valign' : 'center','font_name':'Times New Roman'})
		format_headerBot = workbook.add_format({'font_size':8,'bottom':1,'bold':True,'align' : 'center','valign' : 'center','font_name':'Times New Roman'})
		category_style = workbook.add_format({'font_size':8,'align':'right','font_name':'Times New Roman'})
		merge_format = workbook.add_format({
		    'bold':2,
		    'align' : 'center',
		    'valign' : 'vcenter',
		    'font_size':10,'font_name':'Times New Roman'})
		merge_formatEmpty = workbook.add_format({
		    'bold':2,
		    'align' : 'center',
		    'valign' : 'vcenter',
		    'font_size':10,
		    'top':1,
		    'bottom':1,'font_name':'Times New Roman'})
		bold = workbook.add_format({'bold':True,'font_size':8,'font_name':'Times New Roman'})
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
					

					string_format = workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman'})
					integer_format = workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman'})
					decimal_format = workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman'})
					date_format = workbook.add_format({'num_format': 15,'font_size':8,'font_name':'Times New Roman'})
					time_format = workbook.add_format({'num_format': 21,'font_size':8,'font_name':'Times New Roman'})
					datetime_format = workbook.add_format({'num_format': 22,'font_size':8,'font_name':'Times New Roman'})

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

					# for i in range(lengthOfData2): 
					#     worksheet.write_row(row2+8,kol+m,data[i],font_size)
					#     row2 = row2 + 1


					for i in range(countHeader2+1):
						worksheet.write(row2+8,i,'',format_header)

					for i in range(lokasiCurr2Len):
					    worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
					    worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),format_header)

				





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

					
						######ZONE NEW


						
						string_format = workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman'})
						integer_format = workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman'})
						decimal_format = workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman'})
						date_format = workbook.add_format({'num_format': 15,'font_size':8,'font_name':'Times New Roman'})
						time_format = workbook.add_format({'num_format': 21,'font_size':8,'font_name':'Times New Roman'})
						datetime_format = workbook.add_format({'num_format': 22,'font_size':8,'font_name':'Times New Roman'})
						
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
									

							dataSub = dataSub + 1

							if data[i][0] != data[i+1][0]:
								subTotal = 0
								for k in range(countHeader2+1):
									worksheet.write(dataSub,k,'',format_header)
								
								#NEWZONE
								for k in range(lokasiCurr2Len):
									
									if formatFooter1[k] == 'Integer':
										print('GOT INT')
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format)
									elif formatFooter1[k] == 'Decimal':
										print('GOT DEC')
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format)
									elif formatFooter1[k] == 'Percentage':
										print('GOT PER')
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format)
									else:
										worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
										worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format)
								#END NEW

								# Untuk menulis footer
								# for k in range(lokasiCurr2Len):
								# 	worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								# 	worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),format_header)
									# subTotal.append(lokasiCurr2[k]+str(dataSub+1))
								dataSub = dataSub + 1
								countAwal = dataSub + 1

					######ENDZONE
					    # for i in range(lengthOfData2):
					    #     worksheet.write_row(dataSub,kol+m,data[i],font_size)
					    #     dataSub = dataSub+1
					    #     if data[i][0] != data[i+1][0]:

					    #     	# Untuk menulis border footer
					    #     	for k in range(countHeader2+1):
					    #     		worksheet.write(dataSub,k,'',format_header)
					    #     	# Untuk menulis footer
					    #     	for k in range(lokasiCurr2Len):
					    #     		worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
					    #     		worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),format_header)
					        		
					    #     	dataSub = dataSub+1
					    #     	countAwal = dataSub+1

					except IndexError as e:
						
						#SUBTOTAL TERAKHIR
						for k in range(countHeader2+1):
							worksheet.write(dataSub,k,'',format_header)
						# Untuk menulis footer
						for k in range(lokasiCurr2Len):
							if formatFooter1[k] == 'Integer':
								print('GOT INT')
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),integer_format)
							elif formatFooter1[k] == 'Decimal':
								print('GOT DEC')
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format)
							elif formatFooter1[k] == 'Percentage':
								print('GOT PER')
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),decimal_format)
							else:
								worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),string_format)
						
						#GRANDTOTAL
						dataSub = dataSub + 1
						countAwal = dataSub + 1
						
						for k in range(countHeader2+1):
				    		worksheet.write(dataSub,k,'',format_header)

				    	#NEWZONE
				    	for k in range(lokasiCurr4Len):
				    		if formatFooter2[k] == 'Integer':
				    			worksheet.write(dataSub,k,'',format_header)
				    			worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
				    			worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),integer_format)	
				    		elif formatFooter2[k] == 'Decimal':
				    			worksheet.write(dataSub,k,'',format_header)
				    			worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
				    			worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format)
				    		elif formatFooter2[k] == 'Percentage':
				    			worksheet.write(dataSub,k,'',format_header)
				    			worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
				    			worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),decimal_format)	
				    		else:
				    			worksheet.write(dataSub,k,'',format_header)
				    			worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
				    			worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),string_format)	

						# for k in range(lokasiCurr4Len):
				  #           worksheet.write(dataSub,k,'',format_header)
				  #           worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
				  #           worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s9:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),format_header)
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


















































































		elif jmlHead == '2':
			print('HEAD 2')

			getDetH2    = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
			detHResp2   = json.dumps(getDetH2.json())
			loadDetailH2 = json.loads(detHResp2)


			listKolomHeader2    = []
			lebarH2             = []
			lokasiH2            = []
			formatKolomH2		= []
			formulaH2 			= []
			for i in loadDetailH2:
			    namaKolomH2     = i['namaKolom']
			    lokasi2         = i['lokasi']
			    formatKolom2   	= i['formatKolom']
			    lebH2           = i['lebarKolom']
			    formula2 		=i['formula']


			    formulaH2.append(formula2)
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
					

					string_format = workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman'})
					integer_format = workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman'})
					decimal_format = workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman'})
					date_format = workbook.add_format({'num_format': 15,'font_size':8,'font_name':'Times New Roman'})
					time_format = workbook.add_format({'num_format': 21,'font_size':8,'font_name':'Times New Roman'})
					datetime_format = workbook.add_format({'num_format': 22,'font_size':8,'font_name':'Times New Roman'})
					print(countHeaderH2)
					print(formatKolom)
					for i in range(lengthOfData2):
						print(data[i])
						for x in range(countHeaderH2):
							print(listColWidth)
							if formatKolomH2[x] == 'String':
								worksheet.write('%s%s'%(listColWidth[x],rowString[x]+10),data[i][x], string_format)
								rowString[x] = rowString[x] + 1
								print('STRING')
							elif formatKolomH2[x] == 'Integer':
								worksheet.write('%s%s'%(listColWidth[x],rowInt[x]+10),data[i][x], integer_format)
								rowInt[x] = rowInt[x] + 1
								print('INTEGER')
							elif formatKolomH2[x] == 'Decimal':
								worksheet.write('%s%s'%(listColWidth[x],rowDec[x]+10),data[i][x], decimal_format)
								rowDec[x] = rowDec[x] + 1
								print('DECIMAL')
							elif formatKolomH2[x] == 'Percentage':
								worksheet.write('%s%s'%(listColWidth[x],rowPer[x]+10),data[i][x]*100, decimal_format)
								rowPer[x] = rowPer[x] + 1
								print('PERCENTAGE')
							elif formatKolomH2[x] == 'Date':
								worksheet.write('%s%s'%(listColWidth[x],rowDate[x]+10),data[i][x], date_format)
								rowDate[x] = rowDate[x] + 1
								print('DATE')
							elif formatKolomH2[x] == 'Time':
								worksheet.write('%s%s'%(listColWidth[x],rowTime[x]+10),data[i][x], time_format)
								rowTime[x] = rowTime[x] + 1
								print('TIME')
							elif formatKolomH2[x] == 'Datetime':
								worksheet.write('%s%s'%(listColWidth[x],rowDateTime[x]+10),data[i][x], datetime_format)
								rowDateTime[x] = rowDateTime[x] + 1
								print('DATETIME')
						row2=row2+1
				
					######ENDZONE

					# for i in range(lengthOfData2): #untuk menulis data
					#     worksheet.write_row(row2+9,kol+m,data[i],font_size)
					#     row2 = row2 + 1

					for i in range(countHeaderH2+1):
						worksheet.write(row2+9,i,'',format_header)

					for i in range(lokasiCurr2Len):
						print(kolomFooter[0])
						worksheet.write(row2+9,i,'',format_header)
						worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
						worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s10:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+9),format_header)


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


						
						string_format = workbook.add_format({'num_format': '@','font_size':8,'font_name':'Times New Roman'})
						integer_format = workbook.add_format({'num_format': '0','font_size':8,'font_name':'Times New Roman'})
						decimal_format = workbook.add_format({'num_format': 2,'font_size':8,'font_name':'Times New Roman'})
						date_format = workbook.add_format({'num_format': 15,'font_size':8,'font_name':'Times New Roman'})
						time_format = workbook.add_format({'num_format': 21,'font_size':8,'font_name':'Times New Roman'})
						datetime_format = workbook.add_format({'num_format': 22,'font_size':8,'font_name':'Times New Roman'})
						
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
									worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)

									worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),format_header)
									# subTotal.append(lokasiCurr2[k]+str(dataSub+1))
									
								# for k in range(countHeaderH2+1):
								# 	worksheet.write(dataSub,k,'',format_header)
								# for k in range(lokasiCurr2Len):
								# 	worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
								# 	worksheet.write(dataSub,lokasiCurr[k],'=(%s%s%s%s%s)'% (formulaH2[j][0:1],dataSub+1,formulaH2[j][1:2],formulaH2[j][2:3],dataSub+1),format_header)
							dataSub = dataSub + 1
							countAwal = dataSub + 1



					######ENDZONE

					    # for i in range(lengthOfData2):
					    #     worksheet.write_row(dataSub,kol+m,data[i],font_size)
					    #     dataSub = dataSub+1
					    #     if data[i][0] != data[i+1][0]:

					    #     	# Untuk menulis border footer
					    #     	for k in range(countHeaderH2+1):
					    #     		worksheet.write(dataSub,k,'',format_header)
					    #     	# Untuk menulis footer
					    #     	for k in range(lokasiCurr2Len):
					    #     		worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
					    #     		worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),format_header)
					        		
					    #     	dataSub = dataSub+1
					    #     	countAwal = dataSub+1

					except IndexError as e:
						#SUBTOTAL TERAKHIR
						for k in range(countHeaderH2+1):
							worksheet.write(dataSub,k,'',format_header)
						# Untuk menulis footer
						for k in range(lokasiCurr2Len):
							worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
							worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),format_header)
						dataSub = dataSub + 1
						countAwal = dataSub + 1

						#GRANDTOTAL
						for k in range(countHeaderH2+1):
						    		worksheet.write(dataSub,k,'',format_header)
						for k in range(lokasiCurr4Len):
						            worksheet.write(dataSub,k,'',format_header)
						            worksheet.write(dataSub,1,'%s' % (kolomFooter[1]),format_header)
						            worksheet.write(dataSub,lokasiCurr3[k],'=SUM(%s10:%s%s)'% (lokasiCurr4[k],lokasiCurr4[k],dataSub),format_header)
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
				worksheet.write(dataSub+1,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


				workbook.close()
				return json.dumps(loadDetailReport[5]),200


	except Exception as e:

		err = {
		'error' : str(e)
		}

		print('ERROR2:',err['error'])

		return  json.dumps(err), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port='5003')            