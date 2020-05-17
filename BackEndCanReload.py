from datetime import datetime
import csv
from pypmml import Model
import pandas as pd
import json
from flask import Flask, request, send_file, send_from_directory, safe_join, abort, render_template,redirect
import string
import os
from flask_cors import CORS
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import math
import time
import uuid
import datetime
from werkzeug.serving import run_simple
import requests
import socket
import subprocess 


def get_app():

    BackEndApp = Flask(__name__)
    cors = CORS(BackEndApp, resources={r"/*": {"origins": "*"}})

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        passwd="",
        database="cactus",
        raise_on_warnings=True)

    mycursor = mydb.cursor(dictionary=True)
    mycursor1 = mydb.cursor()
    
    mycursor.execute("SELECT * FROM Model_Data WHERE Status = '1'")
    Model2 = mycursor.fetchone()

    model = Model.fromFile("ModelGBT/" + Model2['Name'])
    Accuracy = float(Model2['Accuracy'])
    print("LoadModel...({0})".format(Model2['Name']))
    
    with open('dataFT.json', encoding="utf8") as json_file:
        jsonFTData = json.load(json_file)

    print("====Server Start====")
        

    @BackEndApp.route('/')
    def hello():
        return '{"result" : "Hello","No" : 1}'
    
    @BackEndApp.route('/Model/Accuracy/')
    def ModelAccuracy():
        data = {
            "Accuracy" : Accuracy
        }
        return json.dumps(data)

    @BackEndApp.route('/countCactusName/')
    def countCactusName():
        sql = "SELECT Result, COUNT(Result) as count_result  FROM Predict_Data GROUP BY Result ORDER BY COUNT(Result) DESC"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        result = {
            "countCactusName" : data
        }
        return json.dumps(result)

    @BackEndApp.route('/countDataStatus/')
    def countDataStatus():
        sql = "SELECT DataStatus, COUNT(DataStatus) as count_datastatus FROM Predict_Data GROUP BY DataStatus "
        mycursor.execute(sql)
        data = mycursor.fetchall()
        result = {
            "countDataStatus" : data
        }
        return json.dumps(result)

    @BackEndApp.route('/countUserData/')
    def countUserData():
        sql = "SELECT EmV, COUNT(EmV) as count_countUserData FROM User_data GROUP BY EmV "
        mycursor.execute(sql)
        data = mycursor.fetchall()
        result = {
            "countUserData" : data
        }
        return json.dumps(result)

    @BackEndApp.route('/checkServer/') 
    def checkStatus():
        sql = "SELECT * FROM Sys_Status"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        status ={

            "status_server" : data
        }

        return json.dumps(status)
    
    @BackEndApp.route("/userAll/",methods=['GET'])
    def userAll():
        sql = "SELECT * FROM User_Data WHERE role = 'M'"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        user = {
            "user" : data
        }
        return json.dumps(user)

    @BackEndApp.route("/userAll/search/Email",methods=['GET'])
    def userAll_Email():
        sql = "SELECT * FROM User_Data WHERE role = 'M'AND Email LIKE '%{0}%'".format(request.args.get("email"))
        mycursor.execute(sql)
        data = mycursor.fetchall()
        user = {
            "user" : data
        }
        return json.dumps(user)

    @BackEndApp.route("/userAll/search/Name",methods=['GET'])
    def userAll_Name():
        sql = "SELECT * FROM User_Data WHERE role = 'M'AND Name LIKE '%{0}%'".format(request.args.get("name"))
        mycursor.execute(sql)
        data = mycursor.fetchall()
        user = {
            "user" : data
        }
        return json.dumps(user)
    
    @BackEndApp.route("/userAll/search/Surname",methods=['GET'])
    def userAll_Surname():
        sql = "SELECT * FROM User_Data WHERE role = 'M'AND Surname LIKE '%{0}%'".format(request.args.get("surname"))
        mycursor.execute(sql)
        data = mycursor.fetchall()
        user = {
            "user" : data
        }
        return json.dumps(user)

    @BackEndApp.route("/history/all/", methods=['POST'])
    def historyAll() :
        resp = request.get_json()
        sort = resp['sort']
        sortBy = resp['sortBy']
        memberId = int(resp['id'])
        cactusName = str(resp['CactusName'])
        if memberId > 0 :
            if cactusName == 'null':
                if sortBy == 'id':
                    if sort == 'asc':
                        sql = "SELECT *  FROM Predict_Data WHERE Member_code = {0} ORDER BY Transaction_id".format(
                        memberId)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Transaction_id DESC".format(
                        memberId)
                elif sortBy == 'result':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Result".format(
                        memberId)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Result DESC".format(
                        memberId)
                elif sortBy == 'time':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Timestamp".format(
                        memberId)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Timestamp DESC".format(
                        memberId)
            else:
                if sortBy == 'id':
                    if sort == 'asc':
                        sql = "SELECT *  FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%' ORDER BY Transaction_id".format(
                        memberId, cactusName)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%'  ORDER BY Transaction_id DESC".format(
                        memberId, cactusName)
                elif sortBy == 'result':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%'  ORDER BY Result".format(
                        memberId, cactusName)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%' ORDER BY Result DESC".format(
                        memberId, cactusName)
                elif sortBy == 'time':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%'  ORDER BY Timestamp".format(
                        memberId, cactusName)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%' ORDER BY Timestamp DESC".format(
                        memberId, cactusName)
        else : 
            if cactusName == 'null':
                if sortBy == 'id':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data ORDER BY Transaction_id"
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data ORDER BY Transaction_id DESC"
                elif sortBy == 'result':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data ORDER BY Result"
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data ORDER BY Result DESC"
                elif sortBy == 'time':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data ORDER BY Timestamp"
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data ORDER BY Timestamp DESC"
            else:
                if sortBy == 'id':
                    if sort == 'asc':
                        sql = "SELECT *  FROM Predict_Data WHERE Result LIKE '%{0}%' ORDER BY Transaction_id".format(cactusName)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Result LIKE '%{0}%'  ORDER BY Transaction_id DESC".format(cactusName)
                elif sortBy == 'result':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data WHERE Result LIKE '%{0}%'  ORDER BY Result".format(cactusName)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Result LIKE '%{0}%' ORDER BY Result DESC".format(cactusName)
                elif sortBy == 'time':
                    if sort == 'asc':
                        sql = "SELECT * FROM Predict_Data WHERE Result LIKE '%{0}%'  ORDER BY Timestamp".format(cactusName)
                    elif sort == 'desc':
                        sql = "SELECT * FROM Predict_Data WHERE Result LIKE '%{0}%' ORDER BY Timestamp DESC".format(cactusName)
        mycursor.execute(sql)

        data = mycursor.fetchall()
        for i in range(len(data)):
            FT = []
            for j in range(13):
                FT.append(jsonFTData['DataFT'][j]['FtList']
                          [int(data[i]['Feature'][j])-1]['Name'])
            data[i]['Feature'] = FT

        predict = {
            "predict": data
        }
        
        return json.dumps(predict)
    
    @BackEndApp.route("/history/", methods=['POST'])
    def history():
        resp = request.get_json()
        sort = resp['sort']
        sortBy = resp['sortBy']
        memberId = int(resp['id'])
        cactusName = str(resp['CactusName'])
        if cactusName == 'null':
            if sortBy == 'id':
                if sort == 'asc':
                    sql = "SELECT *  FROM Predict_Data WHERE Member_code = {0} ORDER BY Transaction_id".format(
                        memberId)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Transaction_id DESC".format(
                        memberId)
            elif sortBy == 'result':
                if sort == 'asc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Result".format(
                        memberId)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Result DESC".format(
                        memberId)
            elif sortBy == 'time':
                if sort == 'asc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Timestamp".format(
                        memberId)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} ORDER BY Timestamp DESC".format(
                        memberId)
        else:
            if sortBy == 'id':
                if sort == 'asc':
                    sql = "SELECT *  FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%' ORDER BY Transaction_id".format(
                        memberId, cactusName)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%'  ORDER BY Transaction_id DESC".format(
                        memberId, cactusName)
            elif sortBy == 'result':
                if sort == 'asc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%'  ORDER BY Result".format(
                        memberId, cactusName)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%' ORDER BY Result DESC".format(
                        memberId, cactusName)
            elif sortBy == 'time':
                if sort == 'asc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%'  ORDER BY Timestamp".format(
                        memberId, cactusName)
                elif sort == 'desc':
                    sql = "SELECT * FROM Predict_Data WHERE Member_code = {0} AND Result LIKE '%{1}%' ORDER BY Timestamp DESC".format(
                        memberId, cactusName)
        mycursor.execute(sql)

        data = mycursor.fetchall()
        for i in range(len(data)):
            FT = []
            for j in range(13):
                FT.append(jsonFTData['DataFT'][j]['FtList']
                          [int(data[i]['Feature'][j])-1]['Name'])
            data[i]['Feature'] = FT

        predict = {
            "predict": data
        }
        return json.dumps(predict)

    @BackEndApp.route('/predict-save/note/',methods = ['POST']) 
    def predictSavewithNote() : 
        resp = request.get_json()
        code = resp['memberCode']
        ft = resp['ft']
        result = resp['result']
        note = resp['note']
        timestamp = str(int(time.time()))
        mycursor1.execute("INSERT INTO Predict_Data (Member_code,Feature,Result,Timestamp,DataStatus,note) VALUES (%s,%s,%s,%s,%s,%s)",(code,ft,result,timestamp,'1',note))
        mydb.commit()
        return('{"Status" : 1}')

    @BackEndApp.route('/predict-save/', methods=['POST'])
    def predictSave():
        resp = request.get_json()
        code = resp['memberCode']
        ft = resp['ft']
        result = resp['result']
        timestamp = str(int(time.time()))
        mycursor1.execute("INSERT INTO Predict_Data (Member_code,Feature,Result,Timestamp,DataStatus) VALUES (%s,%s,%s,%s,%s)",
                          (code, ft, result, timestamp, '1'))

        mydb.commit()

        minPreProcess = 500
        minTraining = 500

        mycursor.execute(
            "SELECT COUNT(*) FROM Predict_Data WHERE DataStatus = '1' ")
        dataStatus1 = mycursor.fetchone()

        mycursor.execute(
            "SELECT COUNT(*) FROM Predict_Data WHERE DataStatus = '2' ")
        dataStatus2 = mycursor.fetchone()

        mycursor.execute('SELECT * FROM Sys_Status WHERE Name = "preData" ')
        preDataResult = mycursor.fetchone()

        mycursor.execute('SELECT * FROM Sys_Status WHERE Name = "Training" ')
        trainingResult = mycursor.fetchone()

        predataStatus = int(preDataResult['Status'])
        trainingStatus = int(trainingResult['Status'])

        countData1 = int(dataStatus1['COUNT(*)'])
        countData2 = int(dataStatus2['COUNT(*)'])
        #if predataStatus == 0:
        #    if countData1 >= minPreProcess:
        #       mycursor1.execute(
        #            "UPDATE Sys_Status SET Status = %s WHERE Name = %s", ('1', "preData"))
        #        mydb.commit()
        #        appscript.app('Terminal').do_script(
        #            "python /Users/admin/Documents/Project/preData.py /Users/admin/Documents/Project/")

        mycursor.execute('SELECT * FROM Sys_Status WHERE Name = "preData" ')
        preDataResult1 = mycursor.fetchone()
        predataStatus1 = int(preDataResult1['Status'])
        
        #if trainingStatus == 0 and predataStatus1 == 0:
        #    if countData2 >= minTraining:
        #        mycursor1.execute(
        #            "UPDATE Sys_Status SET Status = %s WHERE Name = %s", ('1', "Training"))
        #       mydb.commit()
        #        appscript.app('Terminal').do_script(
        #            "python /Users/admin/Documents/Project/Training.py /Users/admin/Documents/Project/")
        
        return('{"Status" : 1}')

    @BackEndApp.route('xxxxxxx', methods=['GET'])
    def predictV2():
        def partition(start, end):
            pivot = y['data'][0][start]
            low = start + 1
            high = end

            while True:
                while low <= high and y['data'][0][high] >= pivot:
                    high = high - 1

                while low <= high and y['data'][0][low] <= pivot:
                    low = low + 1

                if low <= high:
                    y['data'][0][low], y['data'][0][high] = y['data'][0][high], y['data'][0][low]
                    y['columns'][low], y['columns'][high] = y['columns'][high], y['columns'][low]

                else:
                    break

            y['data'][0][start], y['data'][0][high] = y['data'][0][high], y['data'][0][start]
            y['columns'][start], y['columns'][high] = y['columns'][high], y['columns'][start]

            return(high)

        def quick_sort(start, end):
            if start >= end:
                return

            p = partition(start, end)
            quick_sort(start, p-1)
            quick_sort(p+1, end)

        resp = str(request.args.get("ft"))
        ft = '[['
        for i in range(13):
            if i < 12:
                ft += str(float(resp[i]))+','
            if i == 12:
                ft += str(float(resp[i]))+']]}'

        result = model.predict(
            '{"columns": ["f1", "f2", "f3", "f4","f5","f6","f7", "f8", "f9", "f10","f11","f12","f13"], "data": '+ft)
        JsonData = str(result).replace('probability(', '')
        JsonData = JsonData.replace(')', '')
        y = json.loads(JsonData)
        for i in range(26):
            y['data'][0][i] = round(float(y['data'][0][i])*100, 2)

        quick_sort(0, 25)
        return json.dumps(y)

    @BackEndApp.route("/get-image/", methods=['GET'])
    def Get_Image():
        try:
            image_name = str(request.args.get("name"))
            return send_from_directory('IMG/', filename=image_name, as_attachment=True, mimetype='image/jpeg', attachment_filename="nom_image")
        except FileNotFoundError:
            pass

    @BackEndApp.route("/get-dataset/", methods=['GET'])
    def Get_Dataset():
        filename = "train_new_dataset_cactus.xlsx"
        try:
            return send_from_directory('dataset/', filename=filename,as_attachment=True)
        except FileNotFoundError:
            print("File not found")
    
    @BackEndApp.route('/register', methods=['POST'])
    def register():
        resp = request.get_json()
        email = str(resp["email"])
        password = str(resp["password"])
        name = str(resp["name"])
        surname = str(resp["surname"])
        uid = str(uuid.uuid4())
        role = 'M'
        sql = "INSERT INTO User_Data (Email,Password,Name,Surname,Role,Uid,isLogin,EmV) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)"
        val = (email, password, name, surname, role, uid, '0', '0')
        mycursor1.execute(sql, val)
        mydb.commit()
        sendEmail_EmV(email, name, surname, uid)
        return("ok")

    @BackEndApp.route('/edit/name', methods=['POST'])
    def editName():
        resp = request.get_json()
        nameOld = resp['nameOld']
        nameNew = resp['nameNew']
        userId = resp['userId']
        mycursor1.execute(
            "UPDATE User_Data SET Name = %s WHERE Code = %s", (nameNew, userId))
        mydb.commit()
        Time = int(time.time())
        Desciption = "Old Name is "+nameOld+",New Name is "+nameNew
        mycursor1.execute("INSERT INTO Log (JobName,Description,Time,User_id,IP) VALUES (%s,%s,%s,%s,%s)",
                          ("UPDATE SET Name", Desciption, Time, userId, request.remote_addr))
        mydb.commit()
        return('{"status" : 1}')

    @BackEndApp.route('/edit/surname', methods=['POST'])
    def editSurnName():
        resp = request.get_json()
        surnameOld = resp['surnameOld']
        surnameNew = resp['surnameNew']
        userId = resp['userId']
        mycursor1.execute(
            "UPDATE User_Data SET Surname = %s WHERE Code = %s", (surnameNew, userId))
        mydb.commit()
        Time = int(time.time())
        Desciption = "Old Surname is "+surnameOld+",New Surname is "+surnameNew
        mycursor1.execute("INSERT INTO Log (JobName,Description,Time,User_id,IP) VALUES (%s, %s, %s, %s,%s)",
                          ("UPDATE Surname", Desciption, Time, userId, request.remote_addr))
        mydb.commit()
        return('{"status" : 1}')

    gmail_user = 'pigrabbstudio@gmail.com'
    gmail_password = 'sirimongkon1280'

    def sendEmail_EmV(email, Name, Surname, Uid):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            send_from = gmail_user
            to = str(email)
            subject = 'ระบบยืนยันอีเมล์จากเว็ปไซต์การสืบค้นอนุกรมวิธานแคคตัส'
            url = "http://localhost:5000/email-verifier/?email={0}&uid={1}".format(
                email, Uid)
            name = "{0}  {1}".format(Name, Surname)

            email_text = """
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>
                เรียนคุณ {0} 
                <p>กรุณา<a href="{1}">คลิกที่นี่</a>เพื่อยืนยันอีเมล์</p>
        
                ขอแสดงความนับถือ<br>
                ทีมงานเว็ปไซต์การสืบค้นอนุกรมวิธานแคคตัส
             </body>
            </html>""".format(name, url)
            MESSAGE = MIMEMultipart('alternative')
            MESSAGE['subject'] = subject
            MESSAGE['To'] = to
            MESSAGE['From'] = send_from
            MESSAGE.preamble = """
            Your mail reader does not support the report format.
            Please visit us <a href="http://localhost:4200/">online</a>!"""
            HTML_BODY = MIMEText(email_text, 'html')
            MESSAGE.attach(HTML_BODY)
            server.sendmail(send_from, to, MESSAGE.as_string())
            server.quit()
        except:
            print('Something went wrong...')
    
    @BackEndApp.route('/forgot/',methods=['GET'])
    def forgot() :
        email = str(request.args.get("email"))
        mycursor.execute("SELECT * FROM User_Data WHERE Email = '"+email+"'")
        check = mycursor.fetchone()
        if check :
            statusSend = sendEmail_CPass(email,check['Name'],check['Surname'],check['Uid'])
            if statusSend == 1:
                status = {
                    "status": 1
                }
            elif statusSend == 0:
                status = {
                    "status": 2
                }
        else :
                status = {
                    "status": 0
                }         
        jsonData = json.dumps(status)
        return(jsonData)
        
    def sendEmail_CPass(email, Name, Surname, Uid):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            send_from = gmail_user
            to = str(email)
            subject = 'ระบบยืนยันอีเมล์จากเว็ปไซต์การสืบค้นอนุกรมวิธานแคคตัส'
            url = "http://localhost:5000/forgot/password/?email={0}&uid={1}".format(
                email, Uid)
            name = "{0}  {1}".format(Name, Surname)

            email_text = """
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>
                เรียนคุณ {0} 
                <p>กรุณา<a href="{1}">คลิกที่นี่</a>เพื่อไปยังเว็ปไซต์เปลี่ยนรหัสผ่าน</p>
        
                ขอแสดงความนับถือ<br>
                ทีมงานเว็ปไซต์การสืบค้นอนุกรมวิธานแคคตัส
             </body>
            </html>""".format(name, url)
            MESSAGE = MIMEMultipart('alternative')
            MESSAGE['subject'] = subject
            MESSAGE['To'] = to
            MESSAGE['From'] = send_from
            MESSAGE.preamble = """
            Your mail reader does not support the report format.
            Please visit us <a href="http://localhost:4200/">online</a>!"""
            HTML_BODY = MIMEText(email_text, 'html')
            MESSAGE.attach(HTML_BODY)
            server.sendmail(send_from, to, MESSAGE.as_string())
            server.quit()
            status = 1
        except:
            status = 0
        return(status)

    @BackEndApp.route('/forgot/password/',methods=['GET'])
    def forgotPassword() :
        email = str(request.args.get("email"))
        uid = str(request.args.get("uid"))
        mycursor.execute("SELECT * FROM User_Data WHERE Email = %s AND Uid = %s",(email,uid))
        check = mycursor.fetchone()
        if check :
            return render_template('CPass.html', text=email)
        else :
            return render_template('notFound.html')

    @BackEndApp.route('/changePasswordE', methods=['POST'])
    def changePasswordE():
        resp = request.get_json()
        email = resp['email']
        password = resp['password']
        mycursor1.execute("UPDATE User_Data SET Password = %s WHERE Email = %s", (password, email))
        mydb.commit()
        uid = str(uuid.uuid4())
        mycursor1.execute("UPDATE User_Data SET Uid = %s WHERE Email = %s", (uid, email))
        mydb.commit()   
        return('{"status" : 1}')

    @BackEndApp.route('/changePassword', methods=['POST'])
    def changePassword():
        resp = request.get_json()
        oldPassword = resp['oldPassword']
        newPassword = resp['newPassword']
        userID = int(resp['userId'])
        mycursor.execute("SELECT * FROM User_Data WHERE Code = "+str(userID))
        check = mycursor.fetchall()
        if check:
            if check[0]['Password'] == oldPassword:
                mycursor1.execute(
                    "UPDATE User_Data SET Password = %s WHERE Code = %s", (newPassword, userID))
                mydb.commit()
                status = {
                    "status": 1
                }
            else:
                status = {
                    "status": 0
                }
        else:
            status = {
                "status": 0
            }
        jsonData = json.dumps(status)

        return(jsonData)


    @BackEndApp.route('/email-verifier/', methods=['GET'])
    def email_verifier():
        email = str(request.args.get("email"))
        uid = str(request.args.get("uid"))
        mycursor.execute(
            'SELECT * FROM User_Data WHERE Email = %s AND Uid = %s', (email, uid))
        check = mycursor.fetchone()

        if check:
            text = "ยืนยันอีเมล์สำเร็จ ยินดีต้อนรับคุณ " + \
                check["Name"]+" เข้าเป็นสมาชิก"
            mycursor1.execute("UPDATE User_Data SET Emv = %s WHERE Code = %s", ('1', check["Code"]))
            mydb.commit()
            uid = str(uuid.uuid4())
            mycursor1.execute("UPDATE User_Data SET Uid = %s WHERE Code = %s", (uid, check["Code"]))
            mydb.commit()            
        else:
            text = "ยืนยันอีเมลล์ไม่สำเร็จกรุณาสมัครสมาชิกหรือตรวจสอบอีเมลล์อีกครั้ง"
        return render_template('Emv.html', text=text)

    @BackEndApp.route('/checkEmail/', methods=['GET'])
    def checkEmail():
        email = str(request.args.get("email"))
        mycursor.execute("SELECT * FROM User_Data WHERE Email = '"+email+"'")
        check = mycursor.fetchall()
        if check:
            status = {
                "status": 1
            }
        else:
            status = {
                "status": 0
            }
        jsonData = json.dumps(status)
        return(jsonData)

    
    @BackEndApp.route('/login', methods=['POST'])
    def login():
        resp = request.get_json()
        email = str(resp["email"])
        password = str(resp["password"])
        mycursor.execute(
            'SELECT * FROM User_Data WHERE Email = %s AND Password = %s', (email, password))
        account = mycursor.fetchone()

        if account:
            code = str(account["Code"])
            if int(account["EmV"]) == 0  :
                status = 1
            elif  int(account["EmV"]) == 1 :
                status = 2
            elif int(account["EmV"]) == 2 :
                status = 3

            mycursor1.execute(
                    "UPDATE User_Data SET isLogin = %s WHERE Code = %s", (str(int(time.time())),str(code)))
            mydb.commit()

            user = {
                "Code": code,
                "Email": account["Email"],
                "Name": account["Name"],
                "Surname": account["Surname"],
                "Role": account["Role"],
                "Uid": account["Uid"],
                "Status": status
            }
            Data = json.dumps(user)

        else:
            Data = '{"Code" : -1,"Email" : "null","Name" : "null","Surname" : "null","Role" : "null","Uid": "null","Status" : 0}'

        return(Data)

    @BackEndApp.route('/ban/account/',methods=['GET'])
    def banAccount():
        mycursor1.execute(
                    "UPDATE User_Data SET EmV = %s WHERE Code = %s", ('2',str(request.args.get("id"))))
        mydb.commit()
        return ('{"status" : 1}')

    @BackEndApp.route('/unban/account/',methods=['GET'])
    def UnbanAccount():
        mycursor1.execute(
                    "UPDATE User_Data SET EmV = %s WHERE Code = %s", ('1',str(request.args.get("id"))))
        mydb.commit()
        return ('{"status" : 1}')

    return BackEndApp


class AppReloader(object):
    def __init__(self, create_app):
        self.create_app = create_app
        self.app = create_app()

    def get_application(self):
        global to_reload
        if to_reload:
            self.app = self.create_app()
            to_reload = False

        return self.app

    def __call__(self, environ, start_response):
        app = self.get_application()
        return app(environ, start_response)


application = AppReloader(get_app)

if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
