import pandas
from sklearn.ensemble import GradientBoostingClassifier
import pickle



filename  = "dataset/train_new_dataset_cactus.xlsx"

dataset = pandas.read_excel(filename)

cols = [col for col in dataset.columns if col not in ['class']] 
data = dataset[cols]
target = dataset['class']

GBT = GradientBoostingClassifier(max_depth=2,n_estimators=1000,learning_rate=0.1)

model = GBT.fit(data,target)

pkl_filename = "cactus_model.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(model, file)