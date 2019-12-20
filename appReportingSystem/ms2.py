from flask import Flask, render_template, redirect, url_for, request, json, session, flash, jsonify
import datetime
import pymysql
import random
import mysql.connector
from mysql.connector import Error
from db import databaseCMS
import json
import requests



app = Flask(__name__, static_folder='app/static')
app.static_folder = 'static'
app.secret_key = 'ms2'


micro1 = 'http://127.0.0.1:5001/'
micro2 = 'http://127.0.0.1:5002/'
micro3 = 'http://127.0.0.1:5003/'
micro4 = 'http://127.0.0.1:5004/'

class Template:

    def __init__(self):
        self.kode_laporan = ''
        self.nama_laporan = ''
        self.organisasi = ''
        self.kategori = ''
        self.server = ''
        self.deskripsi = ''
        self.jumlah_kolom = ''
        self.jumlah_header = ''
        self.jumlah_footer = ''
        self.periode = ''
        self.printAll = ''

    # def NewTemplate(self, kode_laporan, nama_laporan, organisasi, kategori, server, 
    #                 deskripsi, jumlah_kolom, jumlah_header, jumlah_footer, periode, print_allYN):

    # def EditTemplate


    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================

    #                            T    E   M   P   L   A   T   E


    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================


    #Menginput template baru
    @app.route('/addNewTemplate/<dataTemplate>', methods=['POST','GET'])
    def addNewTemplate(dataTemplate):
        report_createDate   = datetime.datetime.now()
        report_lastUpdate   = datetime.datetime.now()
        dataLoad = json.loads(dataTemplate)

        for x in dataLoad:
            kode_laporan        = dataLoad['kode_laporan']
            server_id           = dataLoad['server_id']
            report_judul        = dataLoad['report_judul'].upper()
            report_deskripsi    = dataLoad['report_deskripsi']
            report_header       = dataLoad['report_header']
            report_footer       = dataLoad['report_footer']
            report_jmlTampilan  = dataLoad['report_jmlTampilan']
            report_periode      = dataLoad['report_periode']
            # report_createDate = dataLoad['report_createDate']
            report_userUpdate   = dataLoad['report_userUpdate']
            # report_lastUpdate = dataLoad['report_lastUpdate']
            report_aktifYN      = dataLoad['report_aktifYN']
            org_id              = dataLoad['org_id']
            ktgri_id            = dataLoad['ktgri_id']
            report_printAllYN   = dataLoad['report_printAllYN']
            report_createdUser  = dataLoad['report_createdUser']
            report_scheduleYN   = dataLoad['report_scheduleYN']
            report_tujuan       = dataLoad['report_tujuan']


        
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('INSERT INTO m_report VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                        (kode_laporan, server_id, report_judul, report_deskripsi, report_header, 
                        report_footer, report_periode, report_createDate, report_userUpdate,
                        report_lastUpdate, report_aktifYN, org_id, ktgri_id, report_printAllYN,
                        report_createdUser, report_scheduleYN, report_jmlTampilan, report_tujuan))
            
            db.commit()
            print("Template berhasil dibuat")
            return 'OK'
            


        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    @app.route('/formatTemplate/<kode_laporan>', methods=['POST','GET']) 
    def formatTemplate(kode_laporan):
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute(' SELECT report_id, report_periode, report_printAllYN, report_judul, report_header, report_footer, report_jumlahTampilan, report_tujuan, report_deskripsi FROM m_report WHERE report_id = "'+kode_laporan+'" ')

            detailFormatTemplate = cursor.fetchall()

            detList = []
            for row in detailFormatTemplate:
                detDict={
                'reportId'          : row[0],
                'reportPeriode'     : row[1],
                'reportPrintAll'    : row[2],
                'reportJudul'       : row[3],
                'reportHeader'      : row[4],
                'reportFooter'      : row[5],
                'reportJmlTampilan' : row[6],
                'reportTujuan'      : row[7],
                'reportDeskripsi'   : row[8]
                }
                detList.append(detDict)

            detTemplate = json.dumps(detList)

            return detTemplate

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    #Pre -programmer melakukan format template
    #Menampilkan detail template yang dipilih
    @app.route('/detailFormatTemplate/<kode_laporan>', methods=['POST','GET'])
    def detailFormatTemplate(kode_laporan):
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            # cursor.execute(' SELECT c.report_id, c.report_periode, c.report_printAllYN, c.report_judul, c.report_header, c.report_footer, c.report_jumlahTampilan, c.report_deskripsi, a.nama_kolom, a.lokasi, a.format_kolom, a.lebar_kolom, b.nama_kolom as namaFooter, b.lokasi as lokasiFooter, a.format_merge, a.format_rataTengah, a.format_rataKanan,b.jenisFooter FROM m_report c LEFT JOIN m_detailF b ON c.report_id = b.report_id LEFT JOIN m_detailH a ON  c.report_id = a.report_id WHERE a.report_id = "'+kode_laporan+'"  ')
            cursor.execute(' SELECT c.report_id, c.report_periode, c.report_printAllYN, c.report_judul, c.report_header, c.report_footer, c.report_jumlahTampilan, c.report_deskripsi, a.nama_kolom, a.lokasi, a.format_kolom, a.lebar_kolom, a.format_merge, a.format_rataTengah, a.format_rataKanan, a.formula, c.report_tujuan FROM m_report c LEFT JOIN m_detailH a ON  c.report_id = a.report_id WHERE c.report_id = "'+kode_laporan+'"  ')

            detailFormatTemplate = cursor.fetchall()

            detList = []
            for row in detailFormatTemplate:
                detDict={
                'reportId'          : row[0],
                'reportPeriode'     : row[1],
                'reportPrintAll'    : row[2],
                'reportJudul'       : row[3],
                'reportHeader'      : row[4],
                'reportFooter'      : row[5],
                'reportJmlTampilan' : row[6],
                'reportDeskripsi'   : row[7],
                'namaKolomH'        : row[8],
                'lokasiH'           : row[9],
                'formatKolomH'      : row[10],
                'lebarKolomH'       : row[11],
                # 'namaKolomF'        : row[12],
                # 'lokasiF'           : row[13],
                'formatMerge'       : row[12],
                'formatTengah'      : row[13],
                'formatKanan'       : row[14],
                'formula'           : row[15],
                'reportTujuan'      : row[16]
                # 'urutanFooter'      : row[15]
                }
                detList.append(detDict)

            detTemplate = json.dumps(detList)

            return detTemplate

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    @app.route('/detailFooter/<kode_laporan>', methods=['GET', 'POST'])
    def detailFooter(kode_laporan):
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute(' SELECT nama_kolom, lokasi, urutan FROM m_detailF WHERE report_id = "'+kode_laporan+'"  ')

            detailFooterTemplate = cursor.fetchall()

            detList = []
            for row in detailFooterTemplate:
                detDict={
                'namaKolomF' : row[0],
                'lokasiF' : row[1],
                'jenisF' : row[2]
                }
                detList.append(detDict)

            detFooter = json.dumps(detList,indent=4)
            print(detFooter)
            return detFooter

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")



    #Menampilkan detail kolom pada menu format template
    @app.route('/detailKolom/<kode_laporan>', methods=['POST','GET'])
    def detailKolom(kode_laporan):

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT nama_kolom, lokasi, format_kolom, lebar_kolom FROM m_detailH WHERE report_id = "'+kode_laporan+'" ')

            detailK = cursor.fetchall()

            detailKol=[]
            for x in detailK:
                i = 0
                detDict = {
                'kolom' : x[0],
                'lokasi'            : x[1],
                'tipeData'          : x[2],
                'lebar'             : x[3]
                }
                detailKol.append(detDict)
                i += 1
            
            
            detK = json.dumps(detailKol,indent=4)

            json.loads(detK)
            a = detK[0]

            print(detDict)
            print(a)
            return detK

            # print(detailK[0][0])
            # print(detailK[1][0])
            
            



        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    # PROSES INSERT KE m_detailh dan m_detailF
    # @app.route('/saveFormatTemplate/<detailKolom>/<nama>/<posisi>/<tipe>/<lebar>/<formula>',  methods = ['GET', 'POST'])
    # def saveFormatTemplate(detailKolom, nama, posisi, tipe, lebar, formula):
    @app.route('/saveFormatTemplate', methods=['POST'])
    def saveFormatTemplate():
        
        
        
        print('OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
        
        formatHead      = request.get_json()
        formatKolom     = json.loads(formatHead)



        namaKolom       = json.loads(formatKolom['kolom'])
        posisiKolom     = json.loads(formatKolom['posisi'])
        tipeKolom       = json.loads(formatKolom['tipe'])
        lebarKolom      = json.loads(formatKolom['lebar'])
        formulaKolom    = json.loads(formatKolom['formula'])

        jmlHeader       = json.loads(formatKolom['jmlHeader'])
        jmlFooter       = json.loads(formatKolom['jmlFooter'])
        #HEADER
        for i in formatKolom:
            reportId        = formatKolom['reportId']
            mergeKolom      = formatKolom['mergeKolom']
            rataKanan       = formatKolom['rataKanan']
            rataTengah      = formatKolom['rataTengah']
            jmlTampilan     = formatKolom['jmlTampilan']
        
        #FOOTER
        for i in formatKolom:
            # reportId        = formatKolom['reportId']
            namaFooter1     = formatKolom['namaFooter1']
            namaFooter2     = formatKolom['namaFooter2']
            posisiFooter1   = formatKolom['posisiFooter1']
            posisiFooter2   = formatKolom['posisiFooter2']
        print(reportId)
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('DELETE FROM m_detailH WHERE report_id="'+reportId+'"')
            db.commit()
            print('delete m_detailH')

            cursor.execute('UPDATE m_report SET report_jumlahTampilan = "'+jmlTampilan+'", \
                            report_header="'+str(jmlHeader)+'", report_footer="'+str(jmlFooter)+'" WHERE\
                            report_id = "'+reportId+'"')
            db.commit()
            print('m_report updated')
            for i in range (len(namaKolom)):
                try:
                    cursor.execute('INSERT INTO m_detailH values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (reportId, namaKolom[i], posisiKolom[i], tipeKolom[i], lebarKolom[i], mergeKolom, rataKanan, rataTengah, formulaKolom[i]))                    
                    db.commit()

                except Exception as e:
                   print(e)

            cursor.execute('DELETE FROM m_detailF WHERE report_id="'+reportId+'"')
            db.commit()
            print('delete m_detailF')

            if (namaFooter2 != ''):
                cursor.execute(' INSERT INTO m_detailf VALUES (%s, %s, %s, %s)', (reportId, namaFooter1, posisiFooter1, "1"))
                db.commit()

                cursor.execute(' INSERT INTO m_detailf VALUES (%s, %s, %s, %s)', (reportId, namaFooter2, posisiFooter2, "2"))
                db.commit()

                cursor.execute('UPDATE m_report set report_footer = "2" WHERE report_id="'+reportId+'" ')
                db.commit()
            elif (namaFooter1 != '') and (namaFooter2 == ''):
                cursor.execute(' INSERT INTO m_detailf VALUES (%s, %s, %s, %s)', (reportId, namaFooter1, posisiFooter1, "1"))
                db.commit()

                cursor.execute('UPDATE m_report set report_footer = "1" WHERE report_id="'+reportId+'" ')
                db.commit()
            else:
                cursor.execute('DELETE FROM m_detailF WHERE report_id="'+reportId+'"')
                db.commit()

                cursor.execute('UPDATE m_report set report_footer = "0" WHERE report_id="'+reportId+'" ')
                db.commit()

        except Error as e :
            print("Error while connecting file MySQL", e)
        
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                cursor.close()
                db.close()
            print("MySQL connection is closed")

    @app.route('/saveFooterTemplate/<detailKolom>', methods=['GET', 'POST'])
    def saveFooterTemplate(detailKolom):
        
        formatKolom = json.loads(detailKolom)

        for i in formatKolom:
            reportId        = formatKolom['reportId']
            namaFooter1     = formatKolom['namaFooter1']
            namaFooter2     = formatKolom['namaFooter2']
            posisiFooter1   = formatKolom['posisiFooter1']
            posisiFooter2   = formatKolom['posisiFooter2']

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('DELETE FROM m_detailF WHERE report_id="'+reportId+'"')
            db.commit()
            print('delete m_detailF')

            if (namaFooter2 != ''):
                cursor.execute(' INSERT INTO m_detailf VALUES (%s, %s, %s, %s)', (reportId, namaFooter1, posisiFooter1, "1"))
                db.commit()

                cursor.execute(' INSERT INTO m_detailf VALUES (%s, %s, %s, %s)', (reportId, namaFooter2, posisiFooter2, "2"))
                db.commit()

                cursor.execute('UPDATE m_report set report_footer = "2" WHERE report_id="'+reportId+'" ')
                db.commit()
            elif (namaFooter1 != '') and (namaFooter2 == ''):
                cursor.execute(' INSERT INTO m_detailf VALUES (%s, %s, %s, %s)', (reportId, namaFooter1, posisiFooter1, "1"))
                db.commit()

                cursor.execute('UPDATE m_report set report_footer = "1" WHERE report_id="'+reportId+'" ')
                db.commit()
            else:
                cursor.execute('DELETE FROM m_detailF WHERE report_id="'+reportId+'"')
                db.commit()

                cursor.execute('UPDATE m_report set report_footer = "0" WHERE report_id="'+reportId+'" ')
                db.commit()

        except Error as e :
            print("Error while connecting file MySQL", e)
        
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                cursor.close()
                db.close()
            print("MySQL connection is closed")

    # MENGINPUT COPY TEMPLATE
    @app.route('/saveCopyTemplate/<detailKolom>/<nama>/<posisi>/<tipe>/<lebar>', methods = ['POST', 'GET'])
    def saveCopyTemplate(detailKolom, nama, posisi, tipe, lebar):
        formatKolom     = json.loads(detailKolom)
        namaKolom       = json.loads(nama)
        posisiKolom     = json.loads(posisi)
        tipeKolom       = json.loads(tipe)
        lebarKolom      = json.loads(lebar)

        report_createDate   = datetime.datetime.now()
        report_lastUpdate   = datetime.datetime.now()

        for x in formatKolom:
            kode_laporan        = formatKolom['reportId']
            org_id              = formatKolom['orgId']
            ktgri_id            = formatKolom['ktgriId']
            server_id           = formatKolom['serverId']
            report_judul        = formatKolom['reportJudul'].upper()
            report_deskripsi    = formatKolom['reportDeskripsi']
            report_tujuan       = formatKolom['reportTujuan']
            report_periode      = formatKolom['reportPeriode']
            report_printAllYN   = formatKolom['reportPrintAll']
            report_header       = formatKolom['reportHeader']
            report_footer       = formatKolom['reportFooter']
            report_jmlTampilan  = formatKolom['jmlTampilan']
            report_userUpdate   = formatKolom['reportUserUpdate']
            report_createdUser  = formatKolom['reportCreatedUser']
            kolom_merge         = formatKolom['mergeKolom']
            kolom_kanan         = formatKolom['rataKanan']
            kolom_tengah        = formatKolom['rataTengah']        

        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('INSERT INTO m_report VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                        (kode_laporan, server_id, report_judul, report_deskripsi, report_header, 
                        report_footer, report_periode, report_createDate, report_userUpdate,
                        report_lastUpdate, "Y", org_id, ktgri_id, report_printAllYN,
                        report_createdUser, "N", report_jmlTampilan, report_tujuan))
            db.commit()

            for i in range (len(namaKolom)):
                try:
                    cursor.execute('INSERT INTO m_detailh values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (kode_laporan, namaKolom[i], posisiKolom[i], tipeKolom[i], lebarKolom[i], kolom_merge, kolom_kanan, kolom_tengah, "")) 
                    db.commit()

                except Exception as e:
                   print(e)

            print("Template berhasil dibuat")
            return 'OK'
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================

    #                            Q  U   E   R   Y


    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================


    #Pre - Programmer ingin melakukan insert Query
    #Menampilkan list kode Laporan yang belum ada querynya
    @app.route('/getKodeNewQuery')
    def getKodeNewQuery():
        try: 
            db      = databaseCMS.db_template()
            cursor  = db.cursor()

            cursor.execute(''' SELECT UPPER(a.report_id) AS report_id FROM m_report a
                            LEFT JOIN m_query b on a.report_id = b.report_id
                            WHERE a.report_id NOT IN (Select report_id from m_query) ''')

            nQuery = cursor.fetchall()

            qList = []

            for i in nQuery:
                qDict={
                'reportId' : i[0]
                }
                qList.append(qDict)

            qDump = json.dumps(qList,indent=4)

            return qDump

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    #Proses insert Query
    @app.route('/addQuery/<kode_laporan>/<dataQuery>', methods=['POST','GET'])
    def addQuery(kode_laporan,dataQuery):

        quer = json.loads(dataQuery)

        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('DELETE FROM m_query WHERE report_id ="'+kode_laporan+'"  ')
            
            for i in range (len(quer)):
                
                try:
                    # print(quer[i]+' '+str(i+1)+' '+str(datetime.datetime.now())+' '+'Y'+' '+kode_laporan)
                    
                    cursor.execute('INSERT INTO m_query VALUES (%s,%s,%s,%s,%s)',( str(i+1), quer[i], datetime.datetime.now(), 'Y', kode_laporan))
                    db.commit()



                    
                except Exception as e:
                    print(e)
                

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")        


    #Pre - programmer ingin melakukan edit Query
    #Menampilkan list kode report yang sudah memiliki query
    @app.route('/getKodeEditQuery', methods=['POST','GET'])
    def getKodeEditQuery():
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('select distinct UPPER(report_id) AS report_id from m_query')
            #listKodeReport = cursor.execute('select report_id, server_nama from M_report  a left join M_server b ON b.server_id = a.server_id;')

            listKodeReportQuery = cursor.fetchall()

            kodeL = []

            for i in listKodeReportQuery:
                kodeDict = {
                'reportId' : i[0]
                }
                kodeL.append(kodeDict)

            kodeD = json.dumps(kodeL,indent=4)
            
            return kodeD
        
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")


    # Untuk menampilkan query yang ada pada template yang dipilih
    @app.route('/viewEditQuery/<kode_laporan>')
    def viewEditQuery(kode_laporan):
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT query_query from m_query WHERE report_id="'+kode_laporan+'" ')

            editQ = cursor.fetchall()

            editL = []

            if (len(editQ)!= 14):
                for i in range (len(editQ),14):
                    editQ.append("")

            
            dumpE = json.dumps(editQ,indent=4)

            print(len(editQ))
            print(editQ)
            return dumpE


    
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")



    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================

    #                            G  E  T


    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================




    #Untuk mendapatkan ID Organisasi & Kategori saat programmer menambahkan schedule baru
    #app.py /sendAddNewSchedule
    @app.route('/getIdOrgKat/<kode_laporan>', methods = ['POST','GET'])
    def getIdOrgKat(kode_laporan):
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()
            
            cursor.execute('SELECT report_id, org_id, ktgri_id FROM M_report WHERE report_id = "'+kode_laporan+'" ')
            orgKat = cursor.fetchall()

            

            getList = []
            for row in orgKat:
                x = {
                "report_id" : row[0],
                "report_org": row[1],
                "report_kat": row[2]
                }
                getList.append(x)

            namaOrgKat = json.dumps(getList,indent=4)
             
            
            return namaOrgKat
            
        
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")
    

    #Untuk menampilkan seluruh report yang ada
    #app.py /listReport
    @app.route('/getListReport', methods = ['POST','GET'])
    def getListReport():
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()
            
            cursor.execute('SELECT a.report_id, org_id, report_judul,\
                            report_deskripsi, report_aktifYN, sch_hari,\
                            sch_bulan, sch_tanggal, server_id\
                            FROM m_report a LEFT JOIN t_schedule b\
                            ON a.report_id = b.report_id \
                            ORDER BY a.report_id')
            
            listReport = cursor.fetchall()

            


            listList = []
            for row in listReport:
                a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+row[1])
                b = json.dumps(a.json())
                c = json.loads(b)
                for x in c:
                    orgName = x['org_name']


                listDict = {
                'reportId'          : row[0],
                'orgId'             : orgName,
                'reportJudul'       : row[2],
                'reportDeskripsi'   : row[3],
                'reportAktifYN'     : row[4],
                'schHari'           : row[5],
                'schBulan'          : row[6],
                'schTanggal'        : row[7],
                'serverId'          : row[8]
                }
                listList.append(listDict)
            resultListReport = json.dumps(listList,indent=4)

            return resultListReport

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")




    #Mengambil semua list Kode Report
    #app.py /editSchedule /formatTemplate
    @app.route('/getKodeReportAll')
    def getKodeReportAll():
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('select UPPER(report_id) AS report_id from m_report')
            

            listKodeReportAll = cursor.fetchall()

            kodeReportList = []

            for x in listKodeReportAll:
                kodeDict = {
                'report_id' : x[0]
                }
                kodeReportList.append(kodeDict)

            kodeReportAll = json.dumps(kodeReportList,indent=4)
                

            
            return kodeReportAll
        
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")

    


    
    #Untuk melihat laporan milik user tsb.
    @app.route('/viewReport/<email>', methods=['POST','GET'])
    def viewReport(email):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT a.report_id, org_id, report_judul, report_deskripsi\
                            FROM m_report a LEFT JOIN t_schedule b ON a.report_id = b.report_id WHERE sch_reportPIC\
                            LIKE "%'+email+'%" OR sch_penerima LIKE "%'+email+'%" ')

            listReport = cursor.fetchall()

            LR = []
            for row in listReport:
                listDict={
                'reportId'          : row[0],
                'orgId'             : row[1],
                'reportJudul'       : row[2],
                'reportDeskripsi'   : row[3]
                }
                LR.append(listDict)

            result = json.dumps(LR,indent=4)

            return result

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")
   
    #Pre - saat programmer ingin membuat template baru
    #Menampilkan list server
    #app.py /addTemplate
    @app.route('/getServer', methods=['POST','GET'])
    def getServer():
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            listServer = cursor.execute('SELECT server_id, server_nama from m_server where server_aktifYN ="Y" order by server_nama')

            listServer = cursor.fetchall()

            serL = []

            for i in listServer:
                serDict = {
                'serverId'      : i[0],
                'serverName'    : i[1]
                }
                serL.append(serDict)

            serD = json.dumps(serL,indent=4)

            return serD

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")
   
    @app.route('/allServer', methods=['POST', 'GET'])
    def allServer():
        try: 
            db = databaseCMS.db_template()

            cursor = db.cursor()
     
            cursor.execute('SELECT server_id, server_nama from m_server ORDER BY server_nama')
            
            resultServer = cursor.fetchall()

            serverList = []
            for row in resultServer:
                serverDict = {
                'Id' : row[0],
                'Nama' : row[1]
                }
                serverList.append(serverDict)
            serverResult = json.dumps(serverList)

            print("=== [ allServer ] ===")
            print("==========================")
            
            return serverResult

        except Error as e :
                print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")

    @app.route('/getNamaServer/<idServer>', methods=['POST', 'GET'])
    def getNamaServer(idServer):
        try: 
            db = databaseCMS.db_template()

            cursor = db.cursor()
     
            cursor.execute('SELECT server_id, server_nama, server_loginName, server_password, server_host, server_port, server_jenis, server_aktifYN from m_server WHERE server_id = "'+idServer+'" ')
            
            resultServer = cursor.fetchall()

            serverList = []
            for row in resultServer:
                serverDict = {
                'Id' : row[0],
                'Name' : row[1],
                'LoginName' : row[2],
                'Pass' : row[3],
                'Host' : row[4],
                'Port' : row[5],
                'Jenis' : row[6],
                'AktifYN' : row[7]
                }
                serverList.append(serverDict)
            serverResult = json.dumps(serverList)

            print("=== [ allServer ] ===")
            print("==========================")
            
            return serverResult

        except Error as e :
                print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")

    @app.route('/insertDataServer/<data>', methods=['POST', 'GET'])
    def insertDataServer(data):
        if request.method == 'POST' :
            dataServer = json.loads(data)

            for x in dataServer:
                id_server = dataServer['serverId']
                nama_server = dataServer['serverName']
                login_server = dataServer['serverLoginName']
                pass_server = dataServer['serverPass']
                host_server = dataServer['serverHost']
                port_server = dataServer['serverPort']
                jenis_server = dataServer['serverJenis']
                aktif_YN = dataServer['serverAktif']


            try:
                db = databaseCMS.db_template()
                cursor = db.cursor()

                cursor.execute(' DELETE FROM m_server WHERE server_id = "'+id_server+'" ')
                db.commit()

                cursor.execute(' INSERT INTO m_server VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (id_server, nama_server, login_server, pass_server, aktif_YN, host_server, port_server, jenis_server))
                db.commit()

                print("berhasil")
            except Error as e:
                print("Error while connecting file MySQL", e)
                flash('Error,', e)

            finally:
                    #Closing DB Connection.
                if(db.is_connected()):
                    cursor.close()
                    db.close()
                print("MySQL connection is closed")

          


#=========================================================================================
#=========================================================================================
#===================================[    SCHEDULING     ]================================
#=========================================================================================
#=========================================================================================

class Schedule:
    def __init__(self):
        self.kode_laporan = ''
        self.organisasi = ''
        self.server = ''
        self.kategori = ''
        self.header = ''
        self.keterangan = ''
        self.note = ''
        self.reportPenerima = ''
        self.reportPIC = ''
        self.grouping = ''
        self.jadwalBln = ''
        self.jadwalHari = ''
        self.jadwalTgl = ''
        self.orderby = ''
        self.aktifYN = ''
    
    
    
    
    def listMaker(self , kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            
            cursor.execute('SELECT sch_tanggal from t_schedule WHERE report_id = "'+kode_laporan+'" ')
            sch_tanggal = cursor.fetchall()
            cursor.execute('SELECT sch_hari from t_schedule WHERE report_id = "'+kode_laporan+'" ')
            sch_hari = cursor.fetchall()
            cursor.execute('SELECT sch_bulan from t_schedule WHERE report_id = "'+kode_laporan+'" ')
            sch_bulan = cursor.fetchall()


            print(sch_tanggal)
            print(sch_hari)
            print(sch_bulan)
            return sch_tanggal

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")


    #Hanya menampilkan kode report dimana scheduleYN = "Y" dan "D"
    @app.route('/listKodeReportEditSchedule', methods = ['POST','GET'])
    def listKodeReportEditSchedule():
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            listKodeEditSchedule = cursor.execute(' select distinct report_id from t_schedule where sch_aktifYN IN ("D", "Y") ')
            listKodeEditSchedule = cursor.fetchall()

            listKodeEdit = []

            for x in listKodeEditSchedule:
                listDict = {
                'reportId' : x[0]
                }
                listKodeEdit.append(listDict)

            kodeReportEdit = json.dumps(listKodeEdit,indent=4)

            
            return kodeReportEdit
        
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")


    #Hanya menampilkan kode report dimana scheduleYN = N
    #app.py /addNewSchedule
    @app.route('/listKodeReportAddNewSchedule', methods = ['POST','GET'])
    def listKodeReportAddNewSchedule():
        try: 
            db = databaseCMS.db_template()
            cursor = db.cursor()

            listKodeReport = cursor.execute('select report_id from m_report where report_scheduleYN = "N" ')
            listKodeReport = cursor.fetchall()

            listKode = []

            for x in listKodeReport:
                listDict = {
                'reportId' : x[0]
                }
                listKode.append(listDict)

            kodeReport = json.dumps(listKode,indent=4)

            
            return kodeReport
        
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
            #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")


    #Proses input schedule baru
    @app.route('/addSchedule/<dataSchedule>', methods=['POST','GET'])
    def addSchedule(dataSchedule):
        if request.method == 'POST':

            queryId = ''
            sch_id = ''
            aktifYN = 'Y'
            lastUpdate = datetime.datetime.now() 


            loadDataSchedule = json.loads(dataSchedule)
            for x in loadDataSchedule:
                kode_laporan    = loadDataSchedule['report_id']
                jadwalHari      = loadDataSchedule['sch_hari']
                jadwalBln       = loadDataSchedule['sch_bulan']
                jadwalTgl       = loadDataSchedule['sch_tanggal']
                grouping        = loadDataSchedule['sch_grouping']
                reportPIC       = loadDataSchedule['sch_reportPIC']
                org             = loadDataSchedule['sch_org']
                kategori        = loadDataSchedule['sch_kategori']
                # header          = loadDataSchedule['sch_header']
        
                
                # keterangan      = loadDataSchedule['sch_keterangan']
                note            = loadDataSchedule['sch_note']
                reportPenerima  = loadDataSchedule['sch_reportPen']
        
            

            try:
                db = databaseCMS.db_template()
                cursor = db.cursor()
                cursor.execute('SELECT report_deskripsi FROM m_report WHERE report_id ="'+kode_laporan+'"')
                res = cursor.fetchall()
                keterangan = str([x[0] for x in res]).replace("['","").replace("']","")


                cursor.execute('DELETE FROM t_schedule WHERE report_id = "'+kode_laporan+'" ')
                

                cursor.execute('INSERT INTO t_schedule VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (kode_laporan, jadwalHari, jadwalBln, jadwalTgl, grouping,
                        reportPIC, org, kategori, lastUpdate, aktifYN, keterangan, note, reportPenerima))
                db.commit()

                cursor.execute('UPDATE m_report SET report_scheduleYN = "Y"  WHERE report_id = "'+kode_laporan+'" ')
                db.commit()


                return 'Success'

            except Error as e :
                print("Error while connecting file MySQL", e)
            finally:
                    #Closing DB Connection.
                        if(db.is_connected()):
                            cursor.close()
                            db.close()
                        print("MySQL connection is closed")


    #Pre - saat programmer ingin melakukan edit schedule
    #Menampilkan schedule dari report yang telah dipilih untuk diedit
    @app.route('/showDetailSchedule/<kode_laporan>', methods =['POST','GET'])                        
    def showDetailSchedule(kode_laporan):
        # kode_laporan = request.form['valKode']
        
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT report_judul, report_deskripsi, sch_note, sch_reportPIC, sch_penerima, sch_groupBy, sch_bulan, sch_hari, sch_tanggal, sch_aktifYN from t_schedule a LEFT JOIN m_report b ON b.report_id = a.report_id WHERE b.report_id = "'+kode_laporan+'" ')

            detailSch = cursor.fetchall()

            detList = []

            
            for x in detailSch:
                detDict={
                'report_judul'      : x[0],
                'report_deskripsi'  : x[1],
                'sch_note'          : x[2],
                'sch_PIC'           : x[3],
                'sch_Pen'           : x[4],
                'sch_groupBy'       : x[5],
                'sch_bulan'         : x[6],
                'sch_hari'          : x[7],
                'sch_tanggal'       : x[8],
                'sch_aktifYN'       : x[9]
                }
                detList.append(detDict)

            detailSchedule = json.dumps(detList)


            
            return detailSchedule

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
        #Closing DB Connection.
            if(db.is_connected()):
                    cursor.close()
                    db.close()
            print("MySQL connection is closed")



    #Proses input edit schedule
    @app.route('/editSched/<data>', methods=['POST','GET'])
    def editSched(data):

        loadData = json.loads(data)
        for i in loadData:
            # header          = loadData['header']
            # keterangan      = loadData['keterangan']
            kode_laporan    = loadData['reportId']
            jadwalHari      = loadData['jadwalHari']
            jadwalTgl       = loadData['jadwalTgl']
            jadwalBln       = loadData['jadwalBln']
            reportPIC       = loadData['PIC']
            reportPenerima  = loadData['Penerima']
            note            = loadData['note']
            lastUpdate      = loadData['lastUpdate']
            grouping        = loadData['grouping']
            aktifYN         = loadData['aktifYN']
        print(kode_laporan)
        print(reportPIC)
        print(reportPenerima)
        print(jadwalHari)
        print(jadwalBln)
        print(jadwalTgl)
        print(aktifYN)

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            # cursor.execute('UPDATE m_report SET report_judul = "'+header+'", report_deskripsi="'+keterangan+'" WHERE report_id ="'+kode_laporan+'" ')
            # db.commit()

            cursor.execute( 'UPDATE t_schedule SET sch_hari = "'+jadwalHari+'", sch_tanggal= \
                            "'+jadwalTgl+'", sch_bulan= "'+jadwalBln+'", sch_reportPIC= \
                            "'+reportPIC+'", sch_penerima= "'+reportPenerima+'", sch_note=\
                            "'+note+'", sch_lastUpdate = "'+lastUpdate+'", sch_groupBy = \
                            "'+grouping+'", sch_aktifYN = "'+aktifYN+'" WHERE report_id = \
                            "'+kode_laporan+'"')
            db.commit()

            
            return 'Edit Schedule Success'

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")








    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================

    #                         P  R   E   V   I   E   W


    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================
    #=========================================================================================





    #Mengambil detail report yang akan di preview
    @app.route('/getDetailReport/<kode_laporan>', methods=['POST','GET'])
    def getDetailReport(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT report_id, report_judul, report_deskripsi, report_periode, report_footer, org_id, report_header, LEFT(report_createdDate,11), report_userUpdate, server_id, ktgri_id FROM m_report WHERE report_id = "'+kode_laporan+'" ')

            result = cursor.fetchone()
            

            return json.dumps(result,indent=4)
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")


    #Mengambil query untuk menjalankan report yang akan di preview MS3
    @app.route('/getQuery/<kode_laporan>', methods=['POST','GET'])
    def getQuery(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT report_id, query_query, query_no FROM m_query WHERE report_id= "'+kode_laporan+'" ')

            result = cursor.fetchall()

            qList = []

            for row in result:
                qDict = {
                'reportId'  : row[0],
                'query'     : row[1],
                'query_no'  : row[2]
                }
                qList.append(qDict)

            resultQuery = json.dumps(qList,indent=4)

            return resultQuery
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")


    #Mengambil detail footer
    #MS3
    @app.route('/getDetailF/<kode_laporan>', methods=['POST','GET'])
    def getDetailF(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT * FROM m_detailF WHERE report_id = "'+kode_laporan+'" ')

            res = cursor.fetchall()

            detF = []

            for row in res:
                detDict = {
                'reportId'  : row[0],
                'namaKolom' : row[1],
                'lokasi'    : row[2],
                'urutan'    : row[3]
                }
                detF.append(detDict)

            detailFooter = json.dumps(detF,indent=4)


            return detailFooter

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")


    #Mengambil detail header jika report_header = 1 MS3
    @app.route('/getDetailH/<kode_laporan>', methods = ['POST','GET'])
    def getDetailH(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT * FROM m_detailH WHERE RIGHT(lokasi,1) = "8" AND report_id = "'+kode_laporan+'" ORDER BY lokasi')

            res = cursor.fetchall()

            detL = []

            for row in res:
                detDict = {
                'reportId'      : row[0],
                'namaKolom'     : row[1],
                'lokasi'        : row[2],
                'formatKolom'   : row[3],
                'lebarKolom'    : row[4],
                'formatMerge'   : row[5],
                'rataTengah'    : row[6],
                'rataKanan'     : row[7],
                'formula'       : row[8]
                }
                detL.append(detDict)
            detailH = json.dumps(detL,indent=4)

            return detailH
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")


    #Mengambil detail header jika report_header = 2 MS3
    @app.route('/getDetailH2/<kode_laporan>', methods = ['POST','GET'])
    def getDetailH2(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT * FROM m_detailH WHERE RIGHT(lokasi,1) = "9" AND report_id = "'+kode_laporan+'" ORDER BY lokasi')

            res = cursor.fetchall()
            
            detL = []

            for row in res:
                detDict = {
                'reportId'      : row[0],
                'namaKolom'     : row[1],
                'lokasi'        : row[2],
                'formatKolom'   : row[3],
                'lebarKolom'    : row[4],
                'formatMerge'   : row[5],
                'rataTengah'    : row[6],
                'rataKanan'     : row[7],
                'formula'       : row[8]
                }
                detL.append(detDict)
            detailH2 = json.dumps(detL,indent=4)

            return detailH2
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")



    #Menampilkan list PIC report MS3
    @app.route('/listPIC/<kode_laporan>', methods=['POST','GET'])
    def listPIC(kode_laporan):

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT sch_reportPIC, sch_penerima FROM t_schedule WHERE report_id = "'+kode_laporan+'" ')
            resultPIC = cursor.fetchall()

            picL = []
            for row in resultPIC:
                picDict = {
                'PIC'   : row[0],
                'Pen'   : row[1]
                }
                picL.append(picDict)

            resultPIC = json.dumps(picL,indent=4)

            

            return resultPIC
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")

    
    


    #Untuk penulisan footer excel MS3
    @app.route('/getSchedule/<kode_laporan>', methods=['POST','GET'])
    def getSchedule(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT sch_hari, sch_bulan, sch_tanggal FROM t_schedule WHERE report_id = "'+kode_laporan+'" ')

            result = cursor.fetchone()

            return json.dumps(result,indent=4)

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")

    @app.route('/getNote/<kode_laporan>')
    def getNote(kode_laporan):
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()

            cursor.execute('SELECT sch_note FROM t_schedule WHERE report_id = "'+kode_laporan+'" ')

            result = cursor.fetchone()

            return json.dumps(result,indent=4)

        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")

    #DISPLAY RUN SCHEDULE
    @app.route('/getKodeReportRunAll', methods=['POST','GET'])
    def getKodeReportRunAll():
        hari    = datetime.datetime.now().strftime('%A') #ex. Monday
        tanggal = datetime.datetime.now().strftime('%d') #ex. 01
        bulan   = datetime.datetime.now().strftime('%B') #ex. January

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()
            
            cursor.execute('SELECT a.report_id, server_id, org_id, ktgri_id,\
                            report_judul, sch_hari, sch_bulan, sch_tanggal,\
                            sch_penerima, sch_reportPIC, sch_prioritas, sch_jam\
                            FROM t_schedule a\
                            LEFT JOIN m_report b\
                            ON a.report_id = b.report_id\
                            WHERE \
                            sch_hari LIKE "%'+hari+'%" AND sch_bulan LIKE "%'+bulan+'%"\
                            OR \
                            sch_bulan LIKE "%'+bulan+'%" AND sch_tanggal LIKE "%'+tanggal+'%" \
                            ORDER BY sch_prioritas, report_id ASC')
            result = cursor.fetchall()

            getRunSched = requests.get('http://127.0.0.1:5003/getStatusRunSchedule')
            getRunSched = json.loads(json.dumps(getRunSched.json()))
            resKode = []
            finishRun = []
            for i in getRunSched:
                repId = i['reportId']
                finishRun.append(repId)
                

            for i in result:
                g = requests.get('http://127.0.0.1:5002/getNamaServer/'+i[1])
                h = json.dumps(g.json())
                j = json.loads(h)
                for x in j:
                    serName = x['Name']

                a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+str(i[2]))
                b = json.dumps(a.json())
                c = json.loads(b)
                for x in c:
                    orgName = x['org_name']
            
                d = requests.get('http://127.0.0.1:5001/getNamaKat/'+str(i[3]))
                e = json.dumps(d.json())
                f = json.loads(e)
                for kat in f:
                    katName = kat['kat_name']

                PIC=[]
                Penerima=[]
                getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+i[0])
                namaResp = json.dumps(getNama.json())
                loadNama = json.loads(namaResp)
                for k in loadNama:
                    namaPIC = k['PIC']
                    namaPen = k['Pen']
                    PIC.append(namaPIC)
                    Penerima.append(namaPen)
                namaPIC         = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","")
                namaPenerima    = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","")

                resD={
                'reportId'      : i[0],
                'server_id'     : i[1],
                'serNama'       :serName,
                'org_id'        : i[2],
                'orgNama'       : orgName,
                'ktgri_id'      : i[3],
                'kateNama'      : katName,
                'reportJudul'   : i[4],
                'schHari'       : i[5],
                'schBulan'      : i[6],
                'schTanggal'    : i[7],
                'schPenerima'   : i[8],
                'namaPenerima'  : namaPenerima,
                'schPIC'        : i[9],
                'namaPIC'       : namaPIC,
                'prioritas'     : i[10],
                'jam'           : str(i[11])
                }
                if resD['reportId'] not in finishRun:
                    resKode.append(resD)
            resultKode = json.dumps(resKode,indent=4)
            
            return resultKode
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")

    @app.route('/getKodeReportRunToday', methods=['POST','GET'])
    def getKodeReportRunToday():
        hari    = datetime.datetime.now().strftime('%A') #ex. Monday
        tanggal = datetime.datetime.now().strftime('%d') #ex. 01
        bulan   = datetime.datetime.now().strftime('%B') #ex. January

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()
            
            cursor.execute('SELECT a.report_id, server_id, org_id, ktgri_id,\
                            report_judul, sch_hari, sch_bulan, sch_tanggal,\
                            sch_penerima, sch_reportPIC\
                            FROM t_schedule a\
                            LEFT JOIN m_report b\
                            ON a.report_id = b.report_id\
                            WHERE \
                            sch_jam ="" or sch_jam is null  AND\
                            sch_hari LIKE "%'+hari+'%" AND sch_bulan LIKE "%'+bulan+'%"\
                            OR \
                            sch_bulan LIKE "%'+bulan+'%" AND sch_tanggal LIKE "%'+tanggal+'%" \
                            ORDER BY sch_prioritas ASC')
            result = cursor.fetchall()
            
            resKode = []
            for i in result:
                a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+str(i[2]))
                b = json.dumps(a.json())
                c = json.loads(b)
                for x in c:
                    orgName = x['org_name']
            
                d = requests.get('http://127.0.0.1:5001/getNamaKat/'+str(i[3]))
                e = json.dumps(d.json())
                f = json.loads(e)
                for kat in f:
                    katName = kat['kat_name']

                PIC=[]
                Penerima=[]
                getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+i[0])
                namaResp = json.dumps(getNama.json())
                loadNama = json.loads(namaResp)
                for k in loadNama:
                    namaPIC = k['PIC']
                    namaPen = k['Pen']
                    PIC.append(namaPIC)
                    Penerima.append(namaPen)
                namaPIC         = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","")
                namaPenerima    = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","")

                resD={
                'reportId'      : i[0],
                'server_id'     : i[1],
                'org_id'        : i[2],
                'orgNama'       : orgName,
                'ktgri_id'      : i[3],
                'kateNama'      : katName,
                'reportJudul'   : i[4],
                'schHari'       : i[5],
                'schBulan'      : i[6],
                'schTanggal'    : i[7],
                'schPenerima'   : i[8],
                'namaPenerima'  : namaPenerima,
                'schPIC'        : i[9],
                'namaPIC'       : namaPIC
                }
                resKode.append(resD)
            resultKode = json.dumps(resKode,indent=4)
            
            return resultKode
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")

    @app.route('/getKodeReportRunJam', methods=['POST','GET'])
    def getKodeReportRunJam():
        hari    = datetime.datetime.now().strftime('%A') #ex. Monday
        tanggal = datetime.datetime.now().strftime('%d') #ex. 01
        bulan   = datetime.datetime.now().strftime('%B') #ex. January

        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()
            
            cursor.execute('SELECT a.report_id, server_id, org_id, ktgri_id,\
                            report_judul, sch_hari, sch_bulan, sch_tanggal,\
                            sch_penerima, sch_reportPIC, sch_jam\
                            FROM t_schedule a\
                            LEFT JOIN m_report b\
                            ON a.report_id = b.report_id\
                            WHERE \
                            sch_jam <> "" AND\
                            sch_hari LIKE "%'+hari+'%" AND sch_bulan LIKE "%'+bulan+'%"\
                            OR \
                            sch_bulan LIKE "%'+bulan+'%" AND sch_tanggal LIKE "%'+tanggal+'%" \
                            ')
            result = cursor.fetchall()
            
            resKode = []
            for i in result:
                a = requests.get('http://127.0.0.1:5001/getNamaOrg/'+str(i[2]))
                b = json.dumps(a.json())
                c = json.loads(b)
                for x in c:
                    orgName = x['org_name']
            
                d = requests.get('http://127.0.0.1:5001/getNamaKat/'+str(i[3]))
                e = json.dumps(d.json())
                f = json.loads(e)
                for kat in f:
                    katName = kat['kat_name']

                PIC=[]
                Penerima=[]
                getNama = requests.get('http://127.0.0.1:5001/getNamaUser/'+i[0])
                namaResp = json.dumps(getNama.json())
                loadNama = json.loads(namaResp)
                for k in loadNama:
                    namaPIC = k['PIC']
                    namaPen = k['Pen']
                    PIC.append(namaPIC)
                    Penerima.append(namaPen)
                namaPIC         = str(PIC).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","")
                namaPenerima    = str(Penerima).replace("[[[['","").replace("']]]]","").replace("[['","").replace("']]","")

                resD={
                'reportId'      : i[0],
                'server_id'     : i[1],
                'org_id'        : i[2],
                'orgNama'       : orgName,
                'ktgri_id'      : i[3],
                'kateNama'      : katName,
                'reportJudul'   : i[4],
                'schHari'       : i[5],
                'schBulan'      : i[6],
                'schTanggal'    : i[7],
                'schPenerima'   : i[8],
                'namaPenerima'  : namaPenerima,
                'schPIC'        : i[9],
                'namaPIC'       : namaPIC,
                'jamRun'        : str(i[10])
                }
                resKode.append(resD)
            resultKode = json.dumps(resKode,indent=4)
            
            return resultKode
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")

    @app.route('/countReportToday')
    def countReportToday():
        hari    = datetime.datetime.now().strftime('%A') #ex. Monday
        tanggal = datetime.datetime.now().strftime('%d') #ex. 01
        bulan   = datetime.datetime.now().strftime('%B') #ex. January
        try:
            db = databaseCMS.db_template()
            cursor = db.cursor()
            cursor.execute('SELECT COUNT(report_id) FROM t_schedule WHERE\
                            sch_hari LIKE "%'+hari+'%" AND sch_bulan LIKE "%'+bulan+'%"\
                            OR \
                            sch_bulan LIKE "%'+bulan+'%" AND sch_tanggal LIKE "%'+tanggal+'%" ')
            result = cursor.fetchone()

            result = str(result).replace("(","").replace(",)","")
            return result
        except Error as e :
            print("Error while connecting file MySQL", e)
        finally:
                #Closing DB Connection.
                    if(db.is_connected()):
                        cursor.close()
                        db.close()
                    print("MySQL connection is closed")




if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port='5002')