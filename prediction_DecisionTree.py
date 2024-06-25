import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib


# Data Preparation
def prepare_data(file_path):
    df = pd.read_excel(file_path)
    df = df.drop(columns=['home', 'away'])  # Exclude 'home' and 'away' columns
    df = df[df['status'] != 'pending']  # Exclude rows where 'status' is 'pending'
    label_encoder = LabelEncoder()
    df['status'] = label_encoder.fit_transform(df['status'])  # Encode target variable
    X = df.drop(columns=['status'])
    y = df['status']
    return X, y, label_encoder


# Training and Saving the Model
def train_and_save_model(file_path, criterion='gini', max_depth=None, min_samples_split=2, random_state=42,
                         test_size=0.2, model_path='decision_tree_model.joblib'):
    X, y, label_encoder = prepare_data(file_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = DecisionTreeClassifier(criterion=criterion, max_depth=max_depth, min_samples_split=min_samples_split,
                                   random_state=random_state)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy}")

    joblib.dump((model, label_encoder), model_path)
    return model, accuracy


# Loading the Model and Predicting
def load_model_and_predict(model_path, new_data):
    model, label_encoder = joblib.load(model_path)
    predictions = model.predict(new_data)
    decoded_predictions = label_encoder.inverse_transform(predictions)
    return decoded_predictions


# Example Usage
file_path = 'ml_fb.xlsx'  # Path to the Excel file
model_path = 'model_DT.joblib'


'''
Parameters for Decision Tree:

criterion: The function to measure the quality of a split (
    'gini' for the Gini impurity and 
    'entropy' for the information gain).

max_depth: The maximum depth of the tree. 
    If None, nodes are expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.

min_samples_split: 
    The minimum number of samples required to split an internal node.
'''
# Training the model
# BEST: criterion='entropy', max_depth=None, min_samples_split=3, test_size=0.3
train_and_save_model(file_path, criterion='entropy', max_depth=None, min_samples_split=3, test_size=0.3,
                     model_path=model_path)

# Load the model and make predictions on new data
# new_data = pd.DataFrame(...)  # New data in the same format as training data without the 'status' column
# predictions = load_model_and_predict(model_path, new_data)
# print(predictions)
