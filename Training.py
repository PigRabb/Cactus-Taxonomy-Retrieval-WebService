import pandas
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_predict,cross_validate
from sklearn.feature_selection import SelectKBest
from sklearn_pandas import DataFrameMapper
from sklearn2pmml.pipeline import PMMLPipeline,Pipeline
from sklearn2pmml import sklearn2pmml
from sklearn2pmml.decoration import ContinuousDomain
from sklearn2pmml import SelectorProxy
from statistics import mean
import sys
import mysql.connector
import time
import requests 
import os
from pypmml import Model
from imblearn.over_sampling import SMOTE


mydb = mysql.connector.connect(
host="127.0.0.1",
user="root",
passwd="PigRabb@0773",
database="Cactus_Taxonomy_Retrieval",
raise_on_warnings = True)

mycursor = mydb.cursor(dictionary=True,buffered=True)

from openpyxl import load_workbook

path = str(sys.argv[1])

filename  = path+"/dataset/train_new_dataset_cactus.xlsx"
workbook = load_workbook(filename=filename)
sheet = workbook.active


mycursor.execute("SELECT * FROM Predict_Data WHERE DataStatus = '2' ")
dataStatus2 = mycursor.fetchall()

for item in dataStatus2 :
	FT = []
	FT.append(item['Result'])
	for i in range(13) :
		FT.append(int(item['Feature'][i]))

	sheet.append(FT)
	mycursor.execute("UPDATE Predict_Data SET DataStatus = %s WHERE Transaction_id = %s",('0',item['Transaction_id']))
	mydb.commit()

workbook.save(filename=filename)

mycursor.execute("SELECT * FROM Model_Data WHERE Status = '1'")
Model2 = mycursor.fetchone()

dataset = pandas.read_excel(filename)

cols = [col for col in dataset.columns if col not in ['class']] 
data = dataset[cols]
target = dataset['class']

sm = SMOTE() 
X,y = sm.fit_sample(data, target)

model = GradientBoostingClassifier(max_depth=2,n_estimators=1000,learning_rate=0.1)

mapper = DataFrameMapper(
	[([column], [ContinuousDomain()]) for column in ["f1", "f2", "f3","f4","f5","f6","f7","f8","f9","f10","f11","f12","f13"]])

pipeline1 = PMMLPipeline([
    ("mapper", mapper),
	("classifier", model),
    
])

pipeline1.fit(X,y)

mycursor.execute("SELECT COUNT(*) FROM Model_Data")
ModelCount = mycursor.fetchone()
totalModel = int(ModelCount['COUNT(*)'])
pmmlFilename = "Model"+str(totalModel+1)+".pmml"
sklearn2pmml(pipeline1, path+'/ModelGBT/'+pmmlFilename, with_repr = True)

scores = cross_validate(model, X, y,cv=10)
sorted(scores.keys())
Accuracy = mean(scores['test_score'])

mycursor.execute("INSERT INTO Model_Data (Name,Status,Created,Accuracy) VALUES (%s,%s,%s,%s)",(pmmlFilename,'0',str(int(time.time())),Accuracy))
mydb.commit()

if Accuracy > float(Model2['Accuracy']) :
	mycursor.execute("UPDATE Model_Data SET Status = %s WHERE Name = %s",('0',str(Model2['Name'])))
	mydb.commit()
	mycursor.execute("UPDATE Model_Data SET Status = %s WHERE Name = %s",('1',pmmlFilename))
	mydb.commit()

mycursor.execute("UPDATE Sys_Status SET Status = %s WHERE Name = %s",('0',"Training"))
mydb.commit()
requests.get(url="http://localhost:5000/reload")
os.system('exit')
exit()