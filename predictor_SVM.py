import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
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
def train_and_save_model(file_path, C=1.0, kernel='rbf', gamma='scale', random_state=42, test_size=0.2,
                         model_path='svm_model.joblib'):
    X, y, label_encoder = prepare_data(file_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Standardize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = SVC(C=C, kernel=kernel, gamma=gamma, random_state=random_state)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy}")

    joblib.dump((model, label_encoder, scaler), model_path)
    return model, accuracy


# Loading the Model and Predicting
def load_model_and_predict(model_path, new_data):
    model, label_encoder, scaler = joblib.load(model_path)
    new_data = scaler.transform(new_data)
    predictions = model.predict(new_data)
    decoded_predictions = label_encoder.inverse_transform(predictions)
    return decoded_predictions


# Example Usage
file_path = 'ml_fb.xlsx'  # Path to the Excel file
model_path = 'model_SVM.joblib'

'''
Parameters for SVM:
C: Regularization parameter. The strength of the regularization is inversely proportional to C. Must be strictly positive.
kernel: Specifies the kernel type to be used in the algorithm ('linear', 'poly', 'rbf', 'sigmoid', 'precomputed').

'''
# BEST: C=2.0, kernel='rbf', gamma='scale', test_size=0.3,
# Training the model
train_and_save_model(file_path, C=2.0, kernel='rbf', gamma='scale', test_size=0.3, model_path=model_path)

# Load the model and make predictions on new data
# new_data = pd.DataFrame(...)  # New data in the same format as training data without the 'status' column
# predictions = load_model_and_predict(model_path, new_data)
# print(predictions)
