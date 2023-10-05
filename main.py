import pandas as pd
import pickle
from sklearn.neighbors import KNeighborsClassifier

names = ['Age', 'Urea', 'Cr', 'HbA1c', 'Chol', 'TG', 'HDL', 'LDL', 'VLDL', 'BMI', 'CLASS']
df = pd.read_excel('data 1 final.xlsx', names=names)
print(df)
cdf = df[['Age', 'Urea', 'Cr', 'HbA1c', 'Chol', 'TG', 'HDL', 'LDL', 'VLDL', 'BMI', 'CLASS']]
# Training Data and Predictor Variable
# Use all data for training (train-test-split not used)
x = df.iloc[:, :10]
y = df.iloc[:, -1]
knn = KNeighborsClassifier()

# Fitting model with training data
knn.fit(x, y)

# Saving model to current directory
# Pickle serializes objects, so they can be saved to a file, and loaded in a program again later on.
pickle.dump(knn, open('model.pkl', 'wb'))

# Loading model to compare the results
model = pickle.load(open('model.pkl', 'rb'))
print(model.predict([[63, 2.5, 52, 7.1, 2.3, 1.3, 0.4, 1.2, 0.9, 35.6]]))