import pandas
import mysql.connector
import sys
from Levenshtein import distance as levenshtein_distance

path = str(sys.argv[1])

mydb = mysql.connector.connect(
host="127.0.0.1",
user="root",
passwd="PigRabb@0773",
database="Cactus_Taxonomy_Retrieval",
raise_on_warnings = True)

mycursor = mydb.cursor(dictionary=True,buffered=True)

mycursor.execute('SELECT * FROM Predict_Data WHERE DataStatus = "1"')
dataQ = mycursor.fetchall()
mycursor.execute('SELECT * FROM Predict_Data WHERE DataStatus = "2"')
dataQ2 = mycursor.fetchall()

dataset = pandas.read_excel(path+"/dataset/train_new_dataset_cactus.xlsx")
cols = [col for col in dataset.columns if col not in ['class']] 
data = dataset[cols]
target = dataset['class']

StatusData = []
for i in range(len(dataQ)) :
    status2 = True
    status3 = True
    for j in range(len(data)) :
        if dataQ[i]['Result'] != target[j] :
            count2 = 0
            data1=''
            data2=''
            for k in range(13) :
                data1 = data1+dataQ[i]['Feature'][k]
                data2 = data2+str(data['f'+str(k+1)][j])
            count2 = 13-levenshtein_distance(data1,data2)

            if count2 >= 9 :
                status2 = False
                break

    if dataQ2 :
        for index in range(len(dataQ)) :
            for index2 in range(len(dataQ2)) :
                count3 = 0
                data1=''
                data2=''
                if dataQ[index]['Result'] != dataQ2[index2]['Result'] :
                    for k in range(13) :
                        data1=data1+dataQ[index]['Feature'][k]
                        data2=data2+dataQ2[index2]['Feature'][k]
                count4 = 13-int(levenshtein_distance(data1,data2))

            if count4 >=9 :
                status3 = False
                break
    StatusData.append(status2 and status3)


for i in range(len(dataQ)) :
    if StatusData[i] == True :
        dataStatus = '2'
    else :
        dataStatus = '3'
    mycursor.execute("UPDATE Predict_Data SET DataStatus = %s WHERE Transaction_id = %s",(dataStatus,dataQ[i]['Transaction_id']))
    mydb.commit()
    

mycursor.execute("UPDATE Sys_Status SET Status = %s WHERE Name = %s",('0',"preData"))
mydb.commit()


            
            
            
            