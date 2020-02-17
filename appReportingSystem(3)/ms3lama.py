from flask import Flask, render_template, redirect, url_for, request, json, session, flash, jsonify,send_from_directory
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

micro1 = 'http://127.0.0.1:5001/'
micro2 = 'http://127.0.0.1:5002/'
micro3 = 'http://127.0.0.1:5003/'
micro4 = 'http://127.0.0.1:5004/'

# def my_job(text):
#     print(text, str(datetime.datetime.now()))



@app.route('/generateRunId')
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
           
        print(runId)
        
        
        return runId
    except Error as e :
            print("Error while connecting file MySQL", e)
    finally:
            #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")

        

#Untuk di layar run schedule
@app.route('/getStatusRunSchedule',methods=['POST','GET'])
def getStatusRunSchedule():
    try:
        db = databaseCMS.db_scheduling()
        cursor = db.cursor()
        cursor.execute('SELECT report_id, org_id, ktgri_id, run_date, run_startTime,\
                        run_endTime, server_id, run_status, error_deskripsi\
                        FROM t_runningLog\
                        WHERE LEFT(run_date,2) = (SELECT MONTH(NOW()))\
                        AND MID(run_date,4,2) = (SELECT RIGHT(curdate(),2))\
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


@app.route('/runScheduleToday', methods=['POST','GET'])
def runScheduleToday():
    getKodeToday = requests.get('http://127.0.0.1:5002/getKodeReportRunToday')
    kodeTodayResp = json.dumps(getKodeToday.json())
    loadKodeToday = json.loads(kodeTodayResp)


    listKodeToday   = []
    organisasi      = []
    serverR         = []
    kategori        = []
    judulR          = []
    hariR           = []
    bulanR          = []
    tglR            = []

    for i in loadKodeToday:
        reportId    = i['reportId']
        server_id   = i['server_id']
        org_id      = i['org_id']
        ktgri_id    = i['ktgri_id']
        reportJudul = i['reportJudul']
        hari        = i['schHari']
        bulan       = i['schBulan']
        tanggal     = i['schTanggal']

        tglRun          = datetime.datetime.now().strftime('%x')
        waktuRun        = datetime.datetime.now().strftime('%X')
        selesaiRun      = ''
        runStatus       = ''
        error_deskripsi = ''
        run_hostname    = socket.gethostname()

        listKodeToday.append(reportId)
        organisasi.append(org_id)
        serverR.append(server_id)
        kategori.append(ktgri_id)
        judulR.append(reportJudul)
        hariR.append(hari)
        bulanR.append(bulan)
        tglR.append(tanggal)

    lengthOfReportId = len(listKodeToday)

    print('Report Run Hari ini : ',listKodeToday)




    try:
        db = databaseCMS.db_scheduling()
        cursor = db.cursor()

        for i in range (lengthOfReportId):
             
            cursor.execute("INSERT INTO t_runningLog (run_id, report_id, server_id, org_id, ktgri_id,\
                             report_judul, sch_hari, sch_bulan, sch_tanggal, run_date,\
                             run_startTime, run_endTime, run_status, error_deskripsi,\
                             run_hostname) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(generateRunId(), listKodeToday[i],\
                                serverR[i], organisasi[i], kategori[i], judulR[i], hariR[i], \
                                bulanR[i], tglR[i], tglRun, waktuRun, selesaiRun,\
                                runStatus, error_deskripsi, run_hostname))
            db.commit()

            

            # JALANKAN REPORT
            runSchedule(listKodeToday[i])



    except Error as e :
            print("Error while connecting file MySQL", e)
    finally:
            #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")








@app.route('/runSchedule/<kode_laporan>', methods=['POST','GET'])
def runSchedule(kode_laporan):
    tglRun          = datetime.datetime.now().strftime('%x')
    waktuRun        = datetime.datetime.now().strftime('%X')
    selesaiRun      = ''
    runStatus       = 'R'
    error_deskripsi = ''
    run_hostname    = socket.gethostname()

    # MENDAPATKAN DETAIL REPORT
    detReport           = requests.get('http://127.0.0.1:5002/getDetailReport/'+kode_laporan)
    detRResp            = json.dumps(detReport.json())
    loadDetailReport    = json.loads(detRResp)
    

    # MENDAPATKAN JUMLAH HEADER (1 / 2)
    jmlHead     = loadDetailReport[6]
    servId      = loadDetailReport[9]
    print('Jumlah Header: ',jmlHead)
    #=========================================================

    

    if jmlHead == '1':

        try:
            count_header = 0
            
            PIC = []
            Penerima = []
            # MENDAPATKAN LIST PIC / PENERIMA SESUAI DENGAN LAPORAN
            getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+kode_laporan)
            namaResp = json.dumps(getNama.json())
            loadNama = json.loads(namaResp)
            for i in loadNama:
                namaPIC = i['PIC']
                namaPen = i['Pen']
                PIC.append(namaPIC)
                Penerima.append(namaPen)
            PIC         = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")
            Penerima    = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")


           
            #==============================================================================

            dbs = databaseCMS.db_scheduling()
            dbsC = dbs.cursor()

            dbsC.execute('UPDATE t_runningLog SET run_startTime ="'+waktuRun+'",\
                                 run_status = "R" WHERE report_id = "'+kode_laporan+'"\
                                    AND run_date ="'+str(tglRun)+'" ')
            dbs.commit()

            dbs.close()
            dbsC.close()




            db = databaseCMS.db_request()
            cursor = db.cursor(buffered = True)


            # GET AND EXECUTE QUERY
            getQ = requests.get('http://127.0.0.1:5002/getQuery/'+kode_laporan)
            qResp = json.dumps(getQ.json())
            loadQ = json.loads(qResp)

            listQuery = []
            for i in loadQ:
                reportId    = i['reportId']
                quer        = i['query']
                qno         = i['query_no']

                listQuery.append(quer)

            print('list Query: ',listQuery)
            lengthOfQuery = len(listQuery)

            try:
                for i in range (lengthOfQuery):
                    sql2 = listQuery[i]
                    cursor.execute(sql2)
                    
                    
                result = cursor.fetchall()
            except Exception as e:
                err = {
                'error' : str(e)
                }

                print(err['error'])

                dbs = databaseCMS.db_scheduling()
                cursor = dbs.cursor()
                cursor.execute('UPDATE t_runningLog SET run_endTime ="'+waktuRun+'",\
                                run_status="G", error_deskripsi="'+str(e)+'" WHERE report_id = "'+kode_laporan+'"\
                                AND run_date ="'+str(tglRun)+'" ')
                dbs.commit()

                dbs.close()
                cursor.close()

                return  json.dumps(err),400

            #HASIL DARI EXECUTE QUERY
            toExcel = []
            for i in result:
                toExcel.append(i)


            namaFileExcel =  kode_laporan+'_'+loadDetailReport[5]+datetime.datetime.now().strftime('%d%m%Y')

            

            if not os.path.exists(app.config['FOLDER_SCHEDULE']):
                os.makedirs(app.config['FOLDER_SCHEDULE'])

            workbook = xlsxwriter.Workbook(app.config['FOLDER_SCHEDULE']+'/%s.xls'% (namaFileExcel))
            worksheet = workbook.add_worksheet()

            ##############style###############
            font_size       = workbook.add_format({'font_size':8})
            format_header   = workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True})
            category_style  = workbook.add_format({'font_size':8,'align':'right'})
            merge_format    = workbook.add_format({
                'bold':2,
                'align' : 'center',
                'valign' : 'vcenter',
                'font_size':10})
            bold            = workbook.add_format({'bold':True,'font_size':8})
            ##################################


            #=======================[HEADER]==================================

            getDetH     = requests.get('http://127.0.0.1:5002/getDetailH/'+kode_laporan)
            detHResp    = json.dumps(getDetH.json())
            loadDetailH = json.loads(detHResp)

            countHeader     = []
            lebar           = []
            listKolom       = []
            lokasiHeader    = []
            for i in loadDetailH:
                namaKolom   = i['namaKolom']
                lokasiKolom = i['lokasi']
                formatKolom = i['formatKolom']
                leb         = i['lebarKolom']
            
                listKolom.append(namaKolom)
                lebar.append(leb)
                lokasiHeader.append(lokasiKolom)
                countHeader.append(namaKolom)
            

            listKolom2 = len(listKolom)
            countHeader2 = len(countHeader)

            print('list Kolom: ',listKolom)
            print('list Lebar: ',lebar)

            
            data = []
            data = toExcel



            row = 0
            kol = 0

            kolom   = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
            row2    = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


            kolomList = (kolom[0:countHeader2])
            rowList = (row2[0:countHeader2])
            j = 1

            #ini untuk menulis header

            #sebelumnya for i in countHeader

            lok = 0
            for i in (listKolom): 
                worksheet.write(lokasiHeader[lok],i,format_header)
                lok = lok + 1
                count_header = count_header + 1

            #end menulis header
            ##########################
            lengthOfData = [x[0] for x in data]
            lengthOfData2 = len(lengthOfData)
            num = 1
            for i in range(lengthOfData2+1): #untuk menulis penomoran 1 s/d banyak data
                if (i == 0):
                    worksheet.write(row + 7,kol,'No',format_header)
                    row = row + 1
                else:
                    worksheet.write(row + 7,kol,num,font_size)
                    row = row + 1
                    num = num + 1

            m = 1
            row2 = 0



            for i in range(lengthOfData2): #untuk menulis data
                worksheet.write_row(row2+8,kol+m,data[i],font_size)
                row2 = row2 + 1





            ###########################################
            #Mengatur bagian atas dari laporan
            
            listMaxCol = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
            maxCol = (listMaxCol[countHeader2])

            

            nOrg = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
            orgResp = json.dumps(nOrg.json())
            loadNamaOrg = json.loads(orgResp)
            for i in loadNamaOrg:
                namaOrg = i['org_name']


            print('loadDetailReport: ',loadDetailReport)
            
            
            
            listColWidth =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
            colWidth = (listColWidth[0:countHeader2])
            
            print('colWidth: ',colWidth)
            print('CH: ',countHeader)
            print('CH2: ',countHeader2)
            print('MaxCol: ',maxCol)


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

            #Untuk mengatur lebar Kolom
            for i in range(countHeader2):
                worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))

            
            ###########################################

            #======================[ FOOTER ]================================

            getF = requests.get('http://127.0.0.1:5002/getDetailF/'+kode_laporan)
            FResp = json.dumps(getF.json())
            detailFooter = json.loads(FResp)

            kolomFooter     = []
            lokasiFooter    = []
            urutanFooter    = []
            for row in detailFooter:
                kodeReportF     = row['reportId']
                namaKolomF      = row['namaKolom']
                lokasi          = row['lokasi']
                urutan          = row['urutan'] 

                kolomFooter.append(namaKolomF)
                lokasiFooter.append(lokasi)
                urutanFooter.append(urutan)

            lokasiCurr = []
            countOfFooter = len(lokasiFooter)


            l = 0
            for i in range(countOfFooter):
                if (lokasi[l] == 'B'):
                    lokasiCurr.append(1)
                elif(lokasi[l] == 'C'):
                    lokasiCurr.append(2)
                elif(lokasi[l] == 'D'):
                    lokasiCurr.append(3)
                elif(lokasi[l] == 'E'):
                    lokasiCurr.append(4)
                elif(lokasi[l] == 'F'):
                    lokasiCurr.append(5)
                elif(lokasi[l] == 'G'):
                    lokasiCurr.append(6)
                elif(lokasi[l] == 'H'):
                    lokasiCurr.append(7)
                elif(lokasi[l] == 'I'):
                    lokasiCurr.append(8)
                elif(lokasi[l] == 'J'):
                    lokasiCurr.append(9)
                elif(lokasi[l] == 'K'):
                    lokasiCurr.append(10)
                elif(lokasi[l] == 'L'):
                    lokasiCurr.append(11)
                elif(lokasi[l] == 'M'):
                    lokasiCurr.append(12)
                elif(lokasi[l] == 'N'):
                    lokasiCurr.append(13)
                elif(lokasi[l] == 'O'):
                    lokasiCurr.append(14)
                elif(lokasi[l] == 'P'):
                    lokasiCurr.append(15)
                l = l + 1

            countFooter = loadDetailReport[4]
            lokasiCurr2 = []
            l = 0

            print(kolomFooter)

            for i in range(countOfFooter):
                if (lokasi[l] == 'B'):
                    lokasiCurr2.append('B')
                elif(lokasi[l] == 'C'):
                    lokasiCurr2.append('C')
                elif(lokasi[l] == 'D'):
                    lokasiCurr2.append('D')
                elif(lokasi[l] == 'E'):
                    lokasiCurr2.append('E')
                elif(lokasi[l] == 'F'):
                    lokasiCurr2.append('F')
                elif(lokasi[l] == 'G'):
                    lokasiCurr2.append('G')
                elif(lokasi[l] == 'H'):
                    lokasiCurr2.append('H')
                elif(lokasi[l] == 'I'):
                    lokasiCurr2.append('I')
                elif(lokasi[l] == 'J'):
                    lokasiCurr2.append('J')
                elif(lokasi[l] == 'K'):
                    lokasiCurr2.append('K')
                elif(lokasi[l] == 'L'):
                    lokasiCurr2.append('L')
                elif(lokasi[l] == 'M'):
                    lokasiCurr2.append('M')
                elif(lokasi[l] == 'N'):
                    lokasiCurr2.append('N')
                elif(lokasi[l] == 'O'):
                    lokasiCurr2.append('O')
                elif(lokasi[l] == 'P'):
                    lokasiCurr2.append('P')
                l = l + 1

            totalRow = len(lengthOfData)
            lokasiCurr2Len = len(lokasiCurr2)
            # print(lokasiCurr2[0])
            print(countFooter)

            if countFooter == '1':
                for i in range(lokasiCurr2Len):
                    print(kolomFooter[0])
                    worksheet.write(row2+8,i,'',format_header)
                    worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
                    worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),format_header)





            # Penulisan Process Time
            worksheet.write(row2+9,1,'Process Time : s/d %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

            #Penulisan Since
            worksheet.write(row2+10,1,'Since : %s' % (loadDetailReport[7]),font_size)

            #Penulisan Schedule
            getSch = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
            getSchResp = json.dumps(getSch.json())
            loadGetSch = json.loads(getSchResp)

            if loadGetSch:
                worksheet.write(row2+11,1,'Schedule : %s %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)

            #Penulisan Creator
            worksheet.write(row2+9,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


            workbook.close()


            try:
                db      = databaseCMS.db_scheduling()
                cursor  = db.cursor()
                cursor.execute('UPDATE t_runningLog SET run_endTime = "'+waktuRun+'",\
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

            
            print(listEmailPIC)
            print(listEmailPen)

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

        except Exception as e:
            
            err = {
            'error' : str(e)
            }

            print(err['error'])

            
            db =databaseCMS.db_scheduling()
            cursor = db.cursor()
            cursor.execute('UPDATE t_runningLog SET run_endTime ="'+waktuRun+'",\
                            run_status="G", error_deskripsi="'+str(e)+'" WHERE report_id = "'+kode_laporan+'"\
                            AND run_date ="'+str(tglRun)+'" ')
            db.commit()

            return  json.dumps(err)
            
            





    elif jmlHead == '2':
        try:
            count_header = 0


            PIC = []
            Penerima = []
            # MENDAPATKAN LIST PIC / PENERIMA SESUAI DENGAN LAPORAN
            getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+kode_laporan)
            namaResp = json.dumps(getNama.json())
            loadNama = json.loads(namaResp)
            for i in loadNama:
                namaPIC = i['PIC']
                namaPen = i['Pen']
                PIC.append(namaPIC)
                Penerima.append(namaPen)
            PIC         = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")
            Penerima    = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")

            dbs = databaseCMS.db_scheduling()
            dbsC = dbs.cursor()

            dbsC.execute('UPDATE t_runningLog SET run_startTime ="'+waktuRun+'",\
                                 run_status = "R" WHERE report_id = "'+kode_laporan+'"\
                                    AND run_date ="'+str(tglRun)+'" ')
            dbs.commit()

            dbs.close()
            dbsC.close()
            

            
            
            #==============================================================================

            db = databaseCMS.db_template()
            cursor = db.cursor(buffered = True)







            # GET AND EXECUTE QUERY
            getQ = requests.get('http://127.0.0.1:5002/getQuery/'+kode_laporan)
            qResp = json.dumps(getQ.json())
            loadQ = json.loads(qResp)

            listQuery = []
            for i in loadQ:
                reportId    = i['reportId']
                quer        = i['query']
                qno         = i['query_no']

                listQuery.append(quer)
            print('list Query: ',listQuery)
            lengthOfQuery = len(listQuery)

            try:
                for i in range (lengthOfQuery):
                    sql2 = listQuery[i]
                    cursor.execute(sql2)
                    
                    
                result = cursor.fetchall()
            except Exception as e:
                err = {
                'error' : str(e)
                }

                print(err['error'])

                dbs = databaseCMS.db_scheduling()
                cursor = dbs.cursor()
                cursor.execute('UPDATE t_runningLog SET run_endTime ="'+waktuRun+'",\
                                run_status="G", error_deskripsi="'+str(e)+'" WHERE report_id = "'+kode_laporan+'"\
                                AND run_date ="'+str(tglRun)+'" ')
                dbs.commit()

                return  json.dumps(err) 

            #HASIL DARI EXECUTE QUERY
            toExcel = []
            for i in result:
                toExcel.append(i)

             


            namaFileExcel =  kode_laporan+'_'+loadDetailReport[5]+datetime.datetime.now().strftime('%d%m%Y')

            

            if not os.path.exists(app.config['FOLDER_SCHEDULE']):
                os.makedirs(app.config['FOLDER_SCHEDULE'])

            workbook = xlsxwriter.Workbook(app.config['FOLDER_SCHEDULE']+'/%s.xls'% (namaFileExcel))
            worksheet = workbook.add_worksheet()

            ##############style###############
            font_size = workbook.add_format({'font_size':8})
            format_header = workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True})
            format_headerMid = workbook.add_format({'font_size':8,'top':1,'bold':True,'align' : 'center','valign' : 'center'})
            category_style = workbook.add_format({'font_size':8,'align':'right'})
            merge_format = workbook.add_format({
                'bold':2,
                'align' : 'center',
                'valign' : 'vcenter',
                'font_size':10})
            bold = workbook.add_format({'bold':True,'font_size':8})
            ##################################


            #=========================================================

            getDetH = requests.get('http://127.0.0.1:5002/getDetailH/'+kode_laporan)
            detHResp = json.dumps(getDetH.json())
            loadDetailH1 = json.loads(detHResp)

            getDetH2 = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
            detHResp2 = json.dumps(getDetH2.json())
            loadDetailH2 = json.loads(detHResp2)


            ########## HEADER 1 #############

            countHeader = []
            lebar       = []
            listKolom   = []
            lokasiH1    = []
            
            for i in loadDetailH1:
                namaKolom   = i['namaKolom']
                lokasiKolom = i['lokasi']
                formatKolom = i['formatKolom']
                leb         = i['lebarKolom']
            
            
                listKolom.append(namaKolom)
                lebar.append(leb)
                lokasiH1.append(lokasiKolom)
                
                countHeader.append(namaKolom)
            
            listKolom2  = len(listKolom)
            countHeader2 = len(countHeader)

            
            mCell = i['formatMerge'].replace('-',':').replace(' ','').split(',')
            

            

            print('merge Cell: ',mCell)
            print('list Kolom1: ',listKolom)
            print('list Lebar1: ',lebar)


            ##########  HEADER 2 ############



            listKolomHeader2    = []
            lebarH2             = []
            lokasiH2            = []
            for i in loadDetailH2:
                namaKolomH2     = i['namaKolom']
                lokasi2         = i['lokasi']
                formatKolomH2   = i['formatKolom']
                lebH2           = i['lebarKolom']

                listKolomHeader2.append(namaKolomH2)
                lebarH2.append(lebH2)
                lokasiH2.append(lokasi2)

            countHeaderH2 = len(listKolomHeader2)
            print('list Kolom2: ',listKolomHeader2)
            print('list Lebar2: ',lebarH2)
            print('lokasi2: ', lokasiH2)

            
            data = []
            data = toExcel



            row = 0
            kol = 0

            kolom   = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
            row2    = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


            kolomList   = (kolom[0:countHeader2])
            rowList     = (row2[0:countHeader2])
            j = 1



            # MERGE CELL
            for i in range(len(mCell)):
                worksheet.merge_range('%s'%(mCell[i]),'%s'%(''), format_headerMid)

            #ini untuk menulis header
            lok = 0
            #HEADER 1
            for i in (listKolom): 
                worksheet.write(lokasiH1[lok],i,format_headerMid)
                lok             = lok + 1
                count_header    = count_header + 1

            #HEADER 2
            lok2 = 0
            for x in (listKolomHeader2):
                worksheet.write(lokasiH2[lok2], x,format_header)
                lok2            = lok2 + 1
                count_header    = count_header + 1

            #end menulis header
            ##########################

            








            lengthOfData = [x[0] for x in data]
            lengthOfData2 = len(lengthOfData)


            num = 1
            for i in range(lengthOfData2+1): #untuk menulis penomoran 1 s/d banyak data
                if (i == 0):
                    worksheet.write(row + 7,kol,'No',format_header)
                    row = row + 1
                else:
                    worksheet.write(row + 8,kol,num,font_size)
                    row = row + 1
                    num = num + 1

            m = 1
            row2 = 0

            for i in range(lengthOfData2): #untuk menulis data
                worksheet.write_row(row2+9,kol+m,data[i],font_size)
                row2 = row2 + 1





            ###########################################
            #Mengatur bagian atas dari laporan
            
            listMaxCol = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
            maxCol = (listMaxCol[countHeader2])

            

            nOrg = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
            orgResp = json.dumps(nOrg.json())
            loadNamaOrg = json.loads(orgResp)
            for i in loadNamaOrg:
                namaOrg = i['org_name']


            print(loadDetailReport)
            
            
            
            listColWidth =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
            colWidth = (listColWidth[0:countHeader2])
            
            print(colWidth)
            print(countHeader)
            print(countHeader2)
            worksheet.merge_range('A1:%s'%(maxCol),'%s'%(namaOrg), merge_format) 
            worksheet.write('A2','%s' % (loadDetailReport[1]),bold ) #nama report
            worksheet.write('A3','Report Code : %s' % (loadDetailReport[0]),font_size) #kode report
            worksheet.write('A4','PIC : %s' % (PIC),font_size)
            worksheet.write('A5','Penerima : %s' % (Penerima),font_size)
            worksheet.write('A6','Filter : %s' % (loadDetailReport[2]), bold ) #filter
            worksheet.write('A7','Period : %s' % (loadDetailReport[3]),font_size) #periode
            

            worksheet.repeat_rows(7,8)
            #======================[ FOOTER ]================================
            
            getF = requests.get('http://127.0.0.1:5002/getDetailF/'+kode_laporan)
            FResp = json.dumps(getF.json())
            detailFooter = json.loads(FResp)

            kolomFooter     = []
            lokasiFooter    = []
            urutanFooter    = []
            for row in detailFooter:
                kodeReportF = row['reportId']
                namaKolomF  = row['namaKolom']
                lokasi      = row['lokasi']
                urutan      = row['urutan'] 

                kolomFooter.append(namaKolomF)
                lokasiFooter.append(lokasi)
                urutanFooter.append(urutan)

            lokasiCurr      = []
            countOfFooter   = len(lokasiFooter)


            l = 0
            for i in range(countOfFooter):
                if (lokasi[l] == 'B'):
                    lokasiCurr.append(1)
                elif(lokasi[l] == 'C'):
                    lokasiCurr.append(2)
                elif(lokasi[l] == 'D'):
                    lokasiCurr.append(3)
                elif(lokasi[l] == 'E'):
                    lokasiCurr.append(4)
                elif(lokasi[l] == 'F'):
                    lokasiCurr.append(5)
                elif(lokasi[l] == 'G'):
                    lokasiCurr.append(6)
                elif(lokasi[l] == 'H'):
                    lokasiCurr.append(7)
                elif(lokasi[l] == 'I'):
                    lokasiCurr.append(8)
                elif(lokasi[l] == 'J'):
                    lokasiCurr.append(9)
                elif(lokasi[l] == 'K'):
                    lokasiCurr.append(10)
                elif(lokasi[l] == 'L'):
                    lokasiCurr.append(11)
                elif(lokasi[l] == 'M'):
                    lokasiCurr.append(12)
                elif(lokasi[l] == 'N'):
                    lokasiCurr.append(13)
                elif(lokasi[l] == 'O'):
                    lokasiCurr.append(14)
                elif(lokasi[l] == 'P'):
                    lokasiCurr.append(15)
                l = l + 1

            countFooter = loadDetailReport[4]
            lokasiCurr2 = []
            l = 0

            print(kolomFooter)

            for i in range(countOfFooter):
                if (lokasi[l] == 'B'):
                    lokasiCurr2.append('B')
                elif(lokasi[l] == 'C'):
                    lokasiCurr2.append('C')
                elif(lokasi[l] == 'D'):
                    lokasiCurr2.append('D')
                elif(lokasi[l] == 'E'):
                    lokasiCurr2.append('E')
                elif(lokasi[l] == 'F'):
                    lokasiCurr2.append('F')
                elif(lokasi[l] == 'G'):
                    lokasiCurr2.append('G')
                elif(lokasi[l] == 'H'):
                    lokasiCurr2.append('H')
                elif(lokasi[l] == 'I'):
                    lokasiCurr2.append('I')
                elif(lokasi[l] == 'J'):
                    lokasiCurr2.append('J')
                elif(lokasi[l] == 'K'):
                    lokasiCurr2.append('K')
                elif(lokasi[l] == 'L'):
                    lokasiCurr2.append('L')
                elif(lokasi[l] == 'M'):
                    lokasiCurr2.append('M')
                elif(lokasi[l] == 'N'):
                    lokasiCurr2.append('N')
                elif(lokasi[l] == 'O'):
                    lokasiCurr2.append('O')
                elif(lokasi[l] == 'P'):
                    lokasiCurr2.append('P')
                l = l + 1

            totalRow = len(lengthOfData)
            lokasiCurr2Len = len(lokasiCurr2)
            # print(lokasiCurr2[0])
            print(countFooter)

            if countFooter == '1':
                for i in range(lokasiCurr2Len):
                    print(kolomFooter[0])
                    worksheet.write(row2+9,i,'',format_header)
                    worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
                    worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),format_header)




            #penulisan printed date

            worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

            #Untuk mengatur lebar Kolom
            for i in range(countHeader2):
                worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))



            # Penulisan Process Time
            worksheet.write(row2+11,1,'Process Time : s/d %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

            #Penulisan Since
            worksheet.write(row2+12,1,'Since : %s' % (loadDetailReport[7]),font_size)

            #Penulisan Schedule
            getSch = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
            getSchResp = json.dumps(getSch.json())
            loadGetSch = json.loads(getSchResp)

            if loadGetSch:

                worksheet.write(row2+13,1,'Schedule : %s %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
            else:
                worksheet.write(row2+13,1,'Schedule : -', font_size)
            #Penulisan Creator
            worksheet.write(row2+11,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


            workbook.close()

            eml     = requests.get('http://127.0.0.1:5002/listPIC/'+kode_laporan)
            emlResp = json.dumps(eml.json())
            loadEml = json.loads(emlResp)

            listEmailPIC = []
            listEmailPen = []
            for k in loadEml:
                listEmPIC = k['PIC']
                listEmPen = k['Pen']
                listEmailPIC.append(listEmPIC)
                listEmailPen.append(listEmPen)

            
            print(listEmailPIC)
            print(listEmailPen)

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


            try:
                db = databaseCMS.db_scheduling()
                cursor = db.cursor()
                cursor.execute('UPDATE t_runningLog SET run_endTime = "'+waktuRun+'",\
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


        except Exception as e:
            
            err = {
            'error' : str(e)
            }

            print(err['error'])

            
            db =databaseCMS.db_scheduling()
            cursor = db.cursor()
            cursor.execute('UPDATE t_runningLog SET run_endTime ="'+waktuRun+'",\
                            run_status="G", error_deskripsi="'+str(e)+'" WHERE report_id = "'+kode_laporan+'"\
                            AND run_date ="'+str(tglRun)+'" ')
            db.commit()

            return  json.dumps(err)
            
    

    
        
    


@app.route('/testPreviewLaporan/<kode_laporan>', methods=['POST','GET'])
def testPreviewLaporan(kode_laporan):
    
    # MENDAPATKAN DETAIL REPORT
    detReport       = requests.get('http://127.0.0.1:5002/getDetailReport/'+kode_laporan)
    detRResp        = json.dumps(detReport.json())
    loadDetailReport = json.loads(detRResp)
    

    # MENDAPATKAN JUMLAH HEADER (1 / 2)
    jmlHead = loadDetailReport[6]
    servId = loadDetailReport[9]

    print('Jumlah Header: ',jmlHead)
    #=========================================================


    if jmlHead == '1':
        try:
            count_header = 0
            
            PIC = []
            Penerima = []
            # MENDAPATKAN LIST PIC / PENERIMA SESUAI DENGAN LAPORAN
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

            print('PIC::::::::::::',PIC)
            print('PEN::::::::::::',Penerima)
            #==============================================================================

            db = databaseCMS.db_request()
            cursor = db.cursor(buffered = True)


            # GET AND EXECUTE QUERY
            getQ = requests.get('http://127.0.0.1:5002/getQuery/'+kode_laporan)
            qResp = json.dumps(getQ.json())
            loadQ = json.loads(qResp)

            listQuery = []
            for i in loadQ:
                reportId    = i['reportId']
                quer        = i['query']
                qno         = i['query_no']

                listQuery.append(quer)

            print('list Query: ',listQuery)
            lengthOfQuery = len(listQuery)

            try:
                for i in range (lengthOfQuery):
                    sql2 = listQuery[i]
                    cursor.execute(sql2)          
                result = cursor.fetchall()
                
                
                
                #HASIL DARI EXECUTE QUERY
                toExcel = []
                for i in result:
                    toExcel.append(i)


            except Exception as e:
                err = {
                'error' : str(e)
                }

                print('ERROR QUERY : ',err['error'])

                return  json.dumps(err),400


            tglSkrg = datetime.datetime.now().strftime('%d')
            blnSkrg = datetime.datetime.now().strftime('%B')
            thnSkrg = datetime.datetime.now().strftime('%Y')

            

            if not os.path.exists(app.config['FOLDER_PREVIEW']):
                os.makedirs(app.config['FOLDER_PREVIEW'])


            namaFileExcel =  kode_laporan+'_'+loadDetailReport[5]+datetime.datetime.now().strftime('%d%m%Y')

            workbook = xlsxwriter.Workbook(app.config['FOLDER_PREVIEW']+'/%s.xls'% (namaFileExcel))
            worksheet = workbook.add_worksheet()
            # worksheet.protect()
            ##############style###############
            font_size       = workbook.add_format({'font_size':8})
            format_header   = workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True})
            category_style  = workbook.add_format({'font_size':8,'align':'right'})
            merge_format    = workbook.add_format({
                'bold':2,
                'align' : 'center',
                'valign' : 'vcenter',
                'font_size':10})
            bold = workbook.add_format({'bold':True,'font_size':8})

            # cellString      = 
            cellInteger     = workbook.add_format({'num_format':'#,##0'})
            cellDecimal     = workbook.add_format({'num_format':'0.00'})
            cellPercentage  = workbook.add_format({'num_format':'0%'})
            cellDate        = workbook.add_format({'num_format':'d-mmm-yy'})
            cellTime        = workbook.add_format({'num_format':'h:mm:ss'})
            cellDatetime    = workbook.add_format({'num_format':'m/d/yy h:m'})
            
            ##################################


            #=========================================================

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
            for i in loadDetailH:
                namaKolom   = i['namaKolom']
                lokasiKolom = i['lokasi']
                forKolom    = i['formatKolom']
                leb         = i['lebarKolom']
                ratTengah   = i['rataTengah']
                ratKanan    = i['rataKanan']

                listKolom.append(namaKolom)
                lokasiHeader.append(lokasiKolom)
                formatKolom.append(forKolom)
                lebar.append(leb)
                
                countHeader.append(namaKolom)
                rataTengah.append(ratTengah)
                rataKanan.append(ratKanan)

            listKolom2      = len(listKolom)
            countHeader2    = len(countHeader)

            print('list Kolom: ',listKolom)
            print('format Kolom: ',formatKolom)
            print('list Lebar: ',lebar)

            
            data = []
            data = toExcel




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
            for i in (listKolom): 
                worksheet.write(lokasiHeader[lok],i,format_header)
                lok             = lok + 1
                count_header    = count_header + 1

            #end menulis header
            ##########################
            lengthOfData = [x[0] for x in data]
            lengthOfData2 = len(lengthOfData)
            num = 1
            for i in range(lengthOfData2+1): #untuk menulis penomoran 1 s/d banyak data
                if (i == 0):
                    worksheet.write(row + 7,kol,'No',format_header)
                    row = row + 1
                else:
                    worksheet.write(row + 7,kol,num,font_size)
                    row = row + 1
                    num = num + 1

            m = 1
            row2 = 0
                
            
                  
            print('lengthofData2  : ', lengthOfData2)

            ########COMEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEENT

            for i in range(lengthOfData2): #untuk menulis data
                worksheet.write_row(row2+8,kol+m,data[i],font_size)
                row2 = row2 + 1
                
                # print(data[i])


            ###########################################
            #Mengatur bagian atas dari laporan
            
            listMaxCol  = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
            maxCol      = (listMaxCol[countHeader2])

            

            nOrg        = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
            orgResp     = json.dumps(nOrg.json())
            loadNamaOrg = json.loads(orgResp)
            for i in loadNamaOrg:
                namaOrg = i['org_name']


            print('loadDetailReport: ',loadDetailReport)
            
            
            
            listColWidth    =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
            colWidth        = (listColWidth[0:countHeader2])
            
            print('colWidth: ',colWidth)
            print('CH: ',countHeader)
            print('CH2: ',countHeader2)
            print('MaxCol: ',maxCol)


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

            #Untuk mengatur lebar Kolom
            for i in range(countHeader2):
                worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))

            
                

            ###########################################

            #======================[ FOOTER ]================================

            getF        = requests.get('http://127.0.0.1:5002/getDetailF/'+kode_laporan)
            FResp       = json.dumps(getF.json())
            detailFooter = json.loads(FResp)

            kolomFooter     = []
            lokasiFooter    = []
            urutanFooter    = []
            for row in detailFooter:
                kodeReportF = row['reportId']
                namaKolomF  = row['namaKolom']
                lokasi      = row['lokasi']
                urutan      = row['urutan'] 

                kolomFooter.append(namaKolomF)
                lokasiFooter.append(lokasi)
                urutanFooter.append(urutan)

            lokasiCurr = []
            countOfFooter = len(lokasiFooter)
            print('KOLOMFOOTER====',kolomFooter)
            print('RANGECOUNTFOOTER====',countOfFooter)

            print(lokasiFooter)
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

            countFooter = loadDetailReport[4]
            lokasiCurr2 = []
            l = 0
        
            print(kolomFooter)

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

            totalRow        = len(lengthOfData)
            lokasiCurr2Len = len(lokasiCurr2)
            # print(lokasiCurr2[0])
            print('COUNTFOOTER',countFooter)

            if countFooter == '1':
                for i in range(lokasiCurr2Len):
                    print(kolomFooter[0])
                    worksheet.write(row2+8,i,'',format_header)
                    worksheet.write(row2+8,1,'%s' % (kolomFooter[0]),format_header)
                    worksheet.write(row2+8,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),format_header)


                # Penulisan Process Time
                worksheet.write(row2+10,1,'Process Time : s/d %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)
                
                #Penulisan Since
                worksheet.write(row2+11,1,'Since : %s' % (loadDetailReport[7]),font_size)

                #Penulisan Schedule
                getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
                getSchResp = json.dumps(getSch.json())
                loadGetSch = json.loads(getSchResp)

                if loadGetSch:
                    worksheet.write(row2+12,1,'Schedule : %s %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)

                #Penulisan Creator
                worksheet.write(row2+10,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


                workbook.close()

            elif countFooter == '2':
                try:
                    dataSub = 8
                    countAwal = 9
                    for i in range(lengthOfData2):
                        worksheet.write_row(dataSub,kol+m,data[i],font_size)
                        row2 = row2+1
                        dataSub = dataSub+1
                        if data[i][0] != data[i+1][0]:
                            # worksheet.write_row(dataSub,kol+m,'SUBTOTAL',font_size)
                            for k in range(lokasiCurr2Len):
                                worksheet.write(dataSub,k,'',format_header)
                                worksheet.write(dataSub,1,'%s' % (kolomFooter[0]),format_header)
                                worksheet.write(dataSub,lokasiCurr[k],'=SUM(%s%s:%s%s)'% (lokasiCurr2[k],countAwal,lokasiCurr2[k],dataSub),format_header)
                            dataSub = dataSub+1
                            countAwal = dataSub+1

                    # Penulisan Process Time
                    worksheet.write(row2+10,1,'Process Time : s/d %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)
                    
                    #Penulisan Since
                    worksheet.write(row2+11,1,'Since : %s' % (loadDetailReport[7]),font_size)

                    #Penulisan Schedule
                    getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
                    getSchResp = json.dumps(getSch.json())
                    loadGetSch = json.loads(getSchResp)

                    if loadGetSch:
                        worksheet.write(row2+12,1,'Schedule : %s %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)

                    #Penulisan Creator
                    worksheet.write(row2+10,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


                    workbook.close()

                except IndexError as e:
                    print('TOTALLLLLLLLLLL')
                    workbook.close()
            else:

                #Penulisan Process Time
                worksheet.write(row2+10,1,'Process Time : s/d %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)
                
                #Penulisan Since
                worksheet.write(row2+11,1,'Since : %s' % (loadDetailReport[7]),font_size)

                #Penulisan Schedule
                getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
                getSchResp = json.dumps(getSch.json())
                loadGetSch = json.loads(getSchResp)

                if loadGetSch:
                    worksheet.write(row2+12,1,'Schedule : %s %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)

                #Penulisan Creator
                worksheet.write(row2+10,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)

                workbook.close()

            # return send_from_directory(app.config['FOLDER_PREVIEW'],namaFileExcel+'.xls')
            return json.dumps(loadDetailReport[5]),200

        except Exception as e:
            
            err = {
            'error' : str(e)
            }

            print('ERROR2:',err['error'])

            return  json.dumps(err), 400




    elif jmlHead == '2':
        try:
            count_header = 0


            PIC         = []
            Penerima    = []
            # MENDAPATKAN LIST PIC / PENERIMA SESUAI DENGAN LAPORAN
            getNama     = requests.get('http://127.0.0.1:5001/getNamaUser/'+kode_laporan)
            namaResp    = json.dumps(getNama.json())
            loadNama    = json.loads(namaResp)
            for i in loadNama:
                namaPIC = i['PIC']
                namaPen = i['Pen']
                PIC.append(namaPIC)
                Penerima.append(namaPen)
            PIC         = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")
            Penerima    = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","").replace("[[[]]]","-")

           


            

            
            
            #==============================================================================

            db = databaseCMS.db_template()
            cursor = db.cursor(buffered = True)







            # GET AND EXECUTE QUERY
            getQ = requests.get('http://127.0.0.1:5002/getQuery/'+kode_laporan)
            qResp = json.dumps(getQ.json())
            loadQ = json.loads(qResp)

            listQuery = []
            for i in loadQ:
                reportId    = i['reportId']
                quer        = i['query']
                qno         = i['query_no']

                listQuery.append(quer)
            print('list Query: ',listQuery)
            lengthOfQuery = len(listQuery)

            try:
                for i in range (lengthOfQuery):
                    sql2 = listQuery[i]
                    cursor.execute(sql2)
                    
                    
                result = cursor.fetchall()
            

                #HASIL DARI EXECUTE QUERY
                toExcel = []
                for i in result:
                    toExcel.append(i)

                

            except Exception as e:
                err = {
                'ERROR QUERY : ' : str(e)
                }

                print(err['error'])

                return  json.dumps(err), 400



            if not os.path.exists(app.config['FOLDER_PREVIEW']):
                os.makedirs(app.config['FOLDER_PREVIEW'])


            namaFileExcel =  kode_laporan+'_'+loadDetailReport[5]+datetime.datetime.now().strftime('%d%m%Y')

            workbook    = xlsxwriter.Workbook(app.config['FOLDER_PREVIEW']+'/%s.xls'% (namaFileExcel))
            worksheet   = workbook.add_worksheet()

            ##############style###############
            font_size           = workbook.add_format({'font_size':8})
            format_header       = workbook.add_format({'font_size':8,'top':1,'bottom':1,'bold':True})
            format_headerMid    = workbook.add_format({'font_size':8,'top':1,'bold':True,'align' : 'center','valign' : 'center'})
            category_style      = workbook.add_format({'font_size':8,'align':'right'})
            merge_format        = workbook.add_format({
                'bold':2,
                'align' : 'center',
                'valign' : 'vcenter',
                'font_size':10})
            bold                = workbook.add_format({'bold':True,'font_size':8})
            ##################################


            #=========================================================

            getDetH     = requests.get('http://127.0.0.1:5002/getDetailH/'+kode_laporan)
            detHResp    = json.dumps(getDetH.json())
            loadDetailH1 = json.loads(detHResp)

            getDetH2    = requests.get('http://127.0.0.1:5002/getDetailH2/'+kode_laporan)
            detHResp2   = json.dumps(getDetH2.json())
            loadDetailH2 = json.loads(detHResp2)


            ########## HEADER 1 #############

            countHeader = []
            lebar       = []
            listKolom   = []
            lokasiH1    = []
            
            for i in loadDetailH1:
                namaKolom   = i['namaKolom']
                lokasiKolom = i['lokasi']
                formatKolom = i['formatKolom']
                leb         = i['lebarKolom']
            
            
                listKolom.append(namaKolom)
                lebar.append(leb)
                lokasiH1.append(lokasiKolom)
            
                countHeader.append(namaKolom)
            
            listKolom2      = len(listKolom)
            countHeader2    = len(countHeader)
            
            
            mCell = i['formatMerge'].replace('-',':').replace(' ','').split(',')
            
            
            
            
            print('merge Cell: ',mCell)
            print('list Kolom1: ',listKolom)
            print('list Lebar1: ',lebar)
            
            
            ##########  HEADER 2 ############



            listKolomHeader2    = []
            lebarH2             = []
            lokasiH2            = []
            for i in loadDetailH2:
                namaKolomH2     = i['namaKolom']
                lokasi2         = i['lokasi']
                formatKolomH2   = i['formatKolom']
                lebH2           = i['lebarKolom']

                listKolomHeader2.append(namaKolomH2)
                lebarH2.append(lebH2)
                lokasiH2.append(lokasi2)

            countHeaderH2 = len(listKolomHeader2)
            print('list Kolom2: ',listKolomHeader2)
            print('list Lebar2: ',lebarH2)
            print('lokasi2: ', lokasiH2)

            
            data = []
            data = toExcel



            row = 0
            kol = 0

            kolom = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
            row2 = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]


            kolomList = (kolom[0:countHeader2])
            rowList = (row2[0:countHeader2])
            j = 1



            # MERGE CELL
            for i in range(len(mCell)):
                worksheet.merge_range('%s'%(mCell[i]),'%s'%(''), format_headerMid)

            #ini untuk menulis header
            lok = 0
            #HEADER 1
            for i in (listKolom): 
                worksheet.write(lokasiH1[lok],i,format_headerMid)
                lok = lok + 1
                count_header = count_header + 1

            #HEADER 2
            lok2 = 0
            for x in (listKolomHeader2):
                worksheet.write(lokasiH2[lok2], x,format_header)
                lok2 = lok2 + 1
                count_header = count_header + 1

            #end menulis header
            ##########################


            lengthOfData = [x[0] for x in data]
            lengthOfData2 = len(lengthOfData)


            num = 1
            for i in range(lengthOfData2+1): #untuk menulis penomoran 1 s/d banyak data
                if (i == 0):
                    worksheet.write(row + 7,kol,'No',format_headerMid)
                    row = row + 1
                else:
                    worksheet.write(row + 8,kol,num,font_size)
                    row = row + 1
                    num = num + 1

            m = 1
            row2 = 0

            for i in range(lengthOfData2): #untuk menulis data
                worksheet.write_row(row2+9,kol+m,data[i],font_size)
                row2 = row2 + 1





            ###########################################
            #Mengatur bagian atas dari laporan
            
            listMaxCol = ['A1','B1','C1','D1','E1','F1','G1','H1','I1','J1','K1','L1','N1','O1','P1']
            maxCol = (listMaxCol[countHeader2])

            

            nOrg = requests.get('http://127.0.0.1:5001/getNamaOrg/'+loadDetailReport[5])
            orgResp = json.dumps(nOrg.json())
            loadNamaOrg = json.loads(orgResp)
            for i in loadNamaOrg:
                namaOrg = i['org_name']


            print(loadDetailReport)
            
            
            
            listColWidth =['B','C','D','E','F','G','H','I','J','K','L','N','O','P']
            colWidth = (listColWidth[0:countHeader2])
            
            print(colWidth)
            print(countHeader)
            print(countHeader2)
            worksheet.merge_range('A1:%s'%(maxCol),'%s'%(namaOrg), merge_format) 
            worksheet.write('A2','%s' % (loadDetailReport[1]),bold ) #nama report
            worksheet.write('A3','Report Code : %s' % (loadDetailReport[0]),font_size) #kode report
            worksheet.write('A4','PIC : %s' % (PIC),font_size)
            worksheet.write('A5','Penerima : %s' % (Penerima),font_size)
            worksheet.write('A6','Filter : %s' % (loadDetailReport[2]), bold ) #filter
            worksheet.write('A7','Period : %s' % (loadDetailReport[3]),font_size) #periode
            

            worksheet.repeat_rows(7,8)
            #======================[ FOOTER ]================================

            getF = requests.get('http://127.0.0.1:5002/getDetailF/'+kode_laporan)
            FResp = json.dumps(getF.json())
            detailFooter = json.loads(FResp)

            kolomFooter     = []
            lokasiFooter    = []
            urutanFooter    = []
            for row in detailFooter:
                kodeReportF = row['reportId']
                namaKolomF  = row['namaKolom']
                lokasi      = row['lokasi']
                urutan      = row['urutan'] 

                kolomFooter.append(namaKolomF)
                lokasiFooter.append(lokasi)
                urutanFooter.append(urutan)

            lokasiCurr      = []
            countOfFooter   = len(lokasiFooter)


            l = 0
            for i in range(countOfFooter):
                if (lokasi[l] == 'B'):
                    lokasiCurr.append(1)
                elif(lokasi[l] == 'C'):
                    lokasiCurr.append(2)
                elif(lokasi[l] == 'D'):
                    lokasiCurr.append(3)
                elif(lokasi[l] == 'E'):
                    lokasiCurr.append(4)
                elif(lokasi[l] == 'F'):
                    lokasiCurr.append(5)
                elif(lokasi[l] == 'G'):
                    lokasiCurr.append(6)
                elif(lokasi[l] == 'H'):
                    lokasiCurr.append(7)
                elif(lokasi[l] == 'I'):
                    lokasiCurr.append(8)
                elif(lokasi[l] == 'J'):
                    lokasiCurr.append(9)
                elif(lokasi[l] == 'K'):
                    lokasiCurr.append(10)
                elif(lokasi[l] == 'L'):
                    lokasiCurr.append(11)
                elif(lokasi[l] == 'M'):
                    lokasiCurr.append(12)
                elif(lokasi[l] == 'N'):
                    lokasiCurr.append(13)
                elif(lokasi[l] == 'O'):
                    lokasiCurr.append(14)
                elif(lokasi[l] == 'P'):
                    lokasiCurr.append(15)
                l = l + 1

            countFooter = loadDetailReport[4]
            lokasiCurr2 = []
            l = 0

            print(kolomFooter)

            for i in range(countOfFooter):
                if (lokasi[l] == 'B'):
                    lokasiCurr2.append('B')
                elif(lokasi[l] == 'C'):
                    lokasiCurr2.append('C')
                elif(lokasi[l] == 'D'):
                    lokasiCurr2.append('D')
                elif(lokasi[l] == 'E'):
                    lokasiCurr2.append('E')
                elif(lokasi[l] == 'F'):
                    lokasiCurr2.append('F')
                elif(lokasi[l] == 'G'):
                    lokasiCurr2.append('G')
                elif(lokasi[l] == 'H'):
                    lokasiCurr2.append('H')
                elif(lokasi[l] == 'I'):
                    lokasiCurr2.append('I')
                elif(lokasi[l] == 'J'):
                    lokasiCurr2.append('J')
                elif(lokasi[l] == 'K'):
                    lokasiCurr2.append('K')
                elif(lokasi[l] == 'L'):
                    lokasiCurr2.append('L')
                elif(lokasi[l] == 'M'):
                    lokasiCurr2.append('M')
                elif(lokasi[l] == 'N'):
                    lokasiCurr2.append('N')
                elif(lokasi[l] == 'O'):
                    lokasiCurr2.append('O')
                elif(lokasi[l] == 'P'):
                    lokasiCurr2.append('P')
                l = l + 1

            totalRow = len(lengthOfData)
            lokasiCurr2Len = len(lokasiCurr2)
            # print(lokasiCurr2[0])
            print(countFooter)

            if countFooter == '1':
                for i in range(lokasiCurr2Len):
                    print(kolomFooter[0])
                    worksheet.write(row2+9,i,'',format_header)
                    worksheet.write(row2+9,1,'%s' % (kolomFooter[0]),format_header)
                    worksheet.write(row2+9,lokasiCurr[i],'=SUM(%s9:%s%s)'% (lokasiCurr2[i],lokasiCurr2[i],totalRow+8),format_header)

            
            #penulisan printed date

            worksheet.write(2,2,'Printed Date : %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

            #Untuk mengatur lebar Kolom
            for i in range(countHeader2):
                worksheet.set_column('%s:%s'%(colWidth[i],colWidth[i]), int(lebar[i]))



            # Penulisan Process Time
            worksheet.write(row2+11,1,'Process Time : s/d %s' % (datetime.datetime.now().replace(microsecond=0)),font_size)

            #Penulisan Since
            worksheet.write(row2+12,1,'Since : %s' % (loadDetailReport[7]),font_size)

            #Penulisan Schedule
            getSch      = requests.get('http://127.0.0.1:5002/getSchedule/'+kode_laporan)
            getSchResp  = json.dumps(getSch.json())
            loadGetSch  = json.loads(getSchResp)

            if loadGetSch:

                worksheet.write(row2+13,1,'Schedule : %s %s %s' % (loadGetSch[1],loadGetSch[0],loadGetSch[2]),font_size)
            else:
                worksheet.write(row2+13,1,'Schedule : -', font_size)
            #Penulisan Creator
            worksheet.write(row2+11,count_header - 1,'CREATOR : %s' % (loadDetailReport[8]),font_size)


            workbook.close()


            return json.dumps(loadDetailReport[5]),200
        except Exception as e:
            
            err = {
            'error' : str(e)
            }

            print(err['error'])

            return  json.dumps(err), 400



if __name__ == "__main__":
    # scheduler = APScheduler()
    # scheduler.add_job(func=runScheduleToday, trigger='cron',id='runScheduleToday', hour='15', minute='46')

    

    # scheduler.start()



    app.run(host='0.0.0.0',debug=True, port='5003')

