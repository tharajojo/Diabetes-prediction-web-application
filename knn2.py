import pandas as pd
import pickle
from sklearn.neighbors import KNeighborsClassifier

names = ['Age','Blood Glucose Level(BGL)','clusters']
df= pd.read_excel('output.xlsx',names=names)
print(df)

cdf = df[['Age','Blood Glucose Level(BGL)','clusters']]
x = df.iloc[:, :2]
y = df.iloc[:, -1]
knn = KNeighborsClassifier()

knn.fit(x, y)
pickle.dump(knn, open('model1.pkl', 'wb'))
model = pickle.load(open('model1.pkl', 'rb'))
print(model.predict([[9,80]]))
