import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
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
def train_and_save_model(file_path, n_estimators=100, max_depth=None, random_state=42, test_size=0.2,
                         model_path='rf_model.joblib'):
    X, y, label_encoder = prepare_data(file_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)
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


from sklearn.model_selection import GridSearchCV


def tune_hyperparameters(file_path):
    X, y, label_encoder = prepare_data(file_path)
    param_grid = {
        'n_estimators': [100, 200, 300, 400],
        'max_depth': [None, 10, 20, 30, 40],
        'test_size': [0.2]  # This needs to be handled outside GridSearchCV
    }

    best_score = 0
    best_params = {}
    for test_size in param_grid['test_size']:
        print(f"starting test size: {test_size}")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid={
            'n_estimators': param_grid['n_estimators'],
            'max_depth': param_grid['max_depth']
        }, cv=3, scoring='accuracy')
        grid_search.fit(X_train, y_train)
        score = grid_search.best_score_
        print(f"{test_size}: score = {score}")
        if score > best_score:
            best_score = score
            best_params = grid_search.best_params_
            best_params['test_size'] = test_size

    print(f"Best Score: {best_score}")
    print(f"Best Parameters: {best_params}")
    return best_params




# Example Usage
file_path = 'ml_fb.xlsx'  # Path to the Excel file
model_path = 'model_RF.joblib'

# best_params = tune_hyperparameters(file_path)
# input('wait')
# Training the model

# Best Parameters: {'max_depth': 10, 'n_estimators': 100, 'test_size': 0.2}
# "Logistic Regression", "Decision Tree", "Random Forest", "SVM", "Naive Bayes"

# - BEST: n_estimators=85, max_depth=5, test_size=0.3

train_and_save_model(file_path, n_estimators=85, max_depth=5, test_size=0.3, model_path=model_path)

# Load the model and make predictions on new data
# new_data = pd.DataFrame(...)  # New data in the same format as training data without the 'status' column
# predictions = load_model_and_predict(model_path, new_data)
# print(predictions)
