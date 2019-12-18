import datetime
import mysql.connector
from flask import Flask, render_template, redirect, url_for, request, json, session, flash
from mysql.connector import Error
from db import databaseCMS
import requests
import datetime




def getUserId():
    username = request.form['username']

    try:
        db = databaseCMS.db_request()
        cursor = db.cursor()

        cursor.execute(''.join(['select user_id from m_user where user_id = "'+username+'"']))

        record = cursor.fetchone()

        userId = str(record).replace("('",'').replace("',)",'')
        
        return userId

    except Error as e:
        print("Error while conencting file MySQL", e)
    finally:
            #Closing DB Connection
        if(db.is_connected()):
            cursor.close()
            db.close()
        print("MySQL connection is closed")


def getPosition():
    username = request.form['username']
    try:
        db = databaseCMS.db_request()
        cursor = db.cursor()

        cursor.execute(''.join(['select user_flag from m_user where user_id = "'+username+'"']))

        record = cursor.fetchone()

        position = str(record).replace("('",'').replace("',)",'')
        
        return position

    except Error as e:
        print("Error while conencting file MySQL", e)
    finally:
            #Closing DB Connection
        if(db.is_connected()):
            cursor.close()
            db.close()
        print("MySQL connection is closed")


def getUserName():
    username = request.form['username']
    try:
        connection = mysql.connector.connect(
        host='localhost',
        database='cms_request',
        user='root',
        password='qwerty')
        if connection.is_connected():
            db_Info= connection.get_server_info()
        print("Connected to MySQL database...",db_Info)

        cursor = connection.cursor()

        cursor.execute(''.join(['select user_name from m_user where user_id = "'+username+'"']))

        record = cursor.fetchone()
        clear = str(record).replace("('",'').replace("',)",'')
        return clear

    except Error as e :
        print("Error while connecting file MySQL", e)
    finally:
            #Closing DB Connection.
                if(connection.is_connected()):
                    cursor.close()
                    connection.close()
                print("MySQL connection is closed")

#                             LOGIN

def auth_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        error = "Invalid username/password"
        #getId = getUserId()

        # try:
        connection = mysql.connector.connect(
        host='localhost',
        database='cms_request',
        user='root',
        password='qwerty')
        if connection.is_connected():
            db_Info= connection.get_server_info()
        print("Connected to MySQL database...",db_Info)

        cursor = connection.cursor()

        cursor.execute(''.join(['SELECT user_Id, user_name, user_password, user_flag, user_id  FROM m_user WHERE user_id ="'+username+'"']))
        user = cursor.fetchall()

        global row
        for row in user:
            global userId
            userId= row[0]
            global userName
            userName = row[1]
            global userPass
            userPass= row[2]
            global userFlag
            userFlag = row[3]


            if username == userId and password == userPass:
                error = None
            else:
                error = 'Invalid username / password'
            

            if error is None:
                # store the user id in a new session and return to the index
                session.clear()
                session['user_id'] = getUserId()
                session['username'] = getUserName()
                session['position'] = getPosition()


                data = {'SessionId' : session['user_id'],
                            'SessionName' : session['username'],
                            'SessionPos' : session['position']}

                # r = requests.post('http://127.0.0.1:5000/sendSession', data = data)
                
                #session["user_id"] = row[4]

                if userFlag == 'User':
                    print('==[ USER LOGIN ]==')
                    print('ID   : ',session['user_id'])
                    print('Name : ',session['username'])
                    print('Date : ',datetime.datetime.now().strftime('%x'))
                    print('Time : ',datetime.datetime.now().strftime('%X'))
                    print('==================')
                    flash('Login Successfull')
                    return redirect(url_for('user'))
                elif userFlag == 'Admin':
                    print('==[ ADMIN LOGIN ]==')
                    print('ID   : ',session['user_id'])
                    print('Name : ',session['username'])
                    print('Date : ',datetime.datetime.now().strftime('%x'))
                    print('Time : ',datetime.datetime.now().strftime('%X'))
                    print('==================')
                    flash('Login Successfull')
                    return redirect(url_for('admin'))
                else:
                    print('==[ SPV LOGIN ]==')
                    print('ID   : ',session['user_id'])
                    print('Name : ',session['username'])
                    print('Date : ',datetime.datetime.now().strftime('%x'))
                    print('Time : ',datetime.datetime.now().strftime('%X'))
                    print('==================')
                    flash('Login Successfull')
                    return redirect(url_for('spv'))

            flash(error)
            # except Error as e :
            #     print("Error while connecting file MySQL", e)
            # finally:
            #         #Closing DB Connection.
            #             if(connection.is_connected()):
            #                 cursor.close()
            #                 connection.close()
            #             print("MySQL connection is closed")
    
    #return redirect(url_for('login', error=error))
    
    return render_template("ms1login.html", error=error)


def logout():
    """Clear the current session, including the stored user id."""
    
    print('==[ LOGOUT ]==')
    # print('ID   : ',session['user_id'])
    print('Name : ',session['username'])
    print('Date : ',datetime.datetime.now().strftime('%x'))
    print('Time : ',datetime.datetime.now().strftime('%X'))
    print('==================')
    session.clear()
    return redirect(url_for("login"))
