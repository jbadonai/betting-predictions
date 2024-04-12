import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


from sklearn.metrics import accuracy_score
import joblib



class RandomForestModelOld:
    def __init__(self, model_file='random_forest_model.pkl'):
        self.model_file = model_file
        self.model = None

    def train_model(self, data):
        # Splitting data into features and target
        X = data[['ho', 'ao', 'od']]
        y = data['result']

        # Splitting data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initializing Random Forest Classifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

        # Training the model
        self.model.fit(X_train, y_train)

        # Saving the model to disk
        joblib.dump(self.model, self.model_file)

        # Making predictions on the test set
        y_pred = self.model.predict(X_test)

        # Calculating accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print("Model trained with accuracy:", accuracy)

    def predict_result(self, new_data):
        if self.model is None:
            raise Exception("Model not trained yet. Please train the model first.")

        # Loading the trained model from disk
        self.model = joblib.load(self.model_file)

        # Making predictions on new data
        prediction = self.model.predict([new_data])[0]

        return prediction


class LogisticRegressionModel:
    def __init__(self, model_file='logistic_regression_model.pkl'):
        self.model_file = model_file
        self.model = None

    def clean_data(self, data_file):
        df = pd.read_excel(data_file)
        df.dropna(inplace=True)
        df = df[df['status'].isin(['H', 'D', 'A'])]
        df.drop(columns=['home', 'away'], inplace=True)  # Drop 'home' and 'away' columns
        # print(f"cleand df: {df}")
        # input(":::")
        return df

    def train_model(self, data_file):
        try:
            print("[DEBUG][LOGISTIC REGRESSION] Training model...")
            df = self.clean_data(data_file)
            X = df.drop(columns=['status'])
            y = df['status']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = LogisticRegression()
            self.model.fit(X_train, y_train)
            print(f"[DEBUG][LOGISTIC REGRESSION] dumping mode...")
            joblib.dump(self.model, self.model_file)
            print("[DEBUG][LOGISTIC REGRESSION] Model dumped successfully!")
            # print("[][] Training successful!")
        except Exception as e:
            print(f"[ERROR][LOGISTIC REGRESSION TRAIN MODEL]: {e}")
            pass


    def predict(self, data):
        if not self.model:
            self.model = joblib.load(self.model_file)
        X = pd.DataFrame([data])
        y_pred = self.model.predict(X)
        return y_pred[0]


class DecisionTreeModel:
    def __init__(self, model_file='decision_tree_model.pkl'):
        self.model_file = model_file
        self.model = None

    def clean_data(self, data_file):
        df = pd.read_excel(data_file)
        df.dropna(inplace=True)
        df = df[df['status'].isin(['H', 'D', 'A'])]
        df.drop(columns=['home', 'away'], inplace=True)  # Drop 'home' and 'away' columns

        return df

    def train_model(self, data_file):
        print("[DEBUG][DECISION TREE] Training model...")
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = DecisionTreeClassifier()
        self.model.fit(X_train, y_train)
        print("[DEBUG][DECISION TREE] dumping model...")
        joblib.dump(self.model, self.model_file)
        print("[DEBUG][DECISION TREE] model Dumped!")
    def predict(self, data):
        if not self.model:
            self.model = joblib.load(self.model_file)
        X = pd.DataFrame([data])
        y_pred = self.model.predict(X)
        return y_pred[0]


class RandomForestModel:
    def __init__(self, model_file='random_forest_model.pkl'):
        self.model_file = model_file
        self.model = None

    def clean_data(self, data_file):
        df = pd.read_excel(data_file)
        df.dropna(inplace=True)
        df = df[df['status'].isin(['H', 'D', 'A'])]
        df.drop(columns=['home', 'away'], inplace=True)  # Drop 'home' and 'away' columns

        return df

    def train_model(self, data_file):
        print("[DEBUG][RANDOM FOREST] Training model...")
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier()
        self.model.fit(X_train, y_train)
        print("[DEBUG][RANDOM FOREST] Dumping model...")
        joblib.dump(self.model, self.model_file)
        print("[DEBUG][RANDOM FOREST] Model Dumped...")

    def predict(self, data):
        if not self.model:
            self.model = joblib.load(self.model_file)
        X = pd.DataFrame([data])
        y_pred = self.model.predict(X)
        return y_pred[0]


class SVMModel:
    def __init__(self, model_file='svm_model.pkl'):
        self.model_file = model_file
        self.model = None

    def clean_data(self, data_file):
        df = pd.read_excel(data_file)
        df.dropna(inplace=True)
        df = df[df['status'].isin(['H', 'D', 'A'])]
        df.drop(columns=['home', 'away'], inplace=True)  # Drop 'home' and 'away' columns

        return df

    def train_model(self, data_file):
        print("[DEBUG][SVM MODEL] Training model...")
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = SVC()
        self.model.fit(X_train, y_train)
        print("[DEBUG][SVM MODEL] Dumping Model...")
        joblib.dump(self.model, self.model_file)
        print("[DEBUG][SVM MODEL] Model Dumped...")

    def predict(self, data):
        if not self.model:
            self.model = joblib.load(self.model_file)
        X = pd.DataFrame([data])
        y_pred = self.model.predict(X)
        return y_pred[0]


class NaiveBayesModel:
    def __init__(self, model_file='naive_bayes_model.pkl'):
        self.model_file = model_file
        self.model = None

    def clean_data(self, data_file):
        df = pd.read_excel(data_file)
        df.dropna(inplace=True)
        df = df[df['status'].isin(['H', 'D', 'A'])]
        df.drop(columns=['home', 'away'], inplace=True)  # Drop 'home' and 'away' columns

        return df

    def train_model(self, data_file):
        print("[DEBUG][NAIVE BAYES MODEL] Training model...")
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = GaussianNB()
        self.model.fit(X_train, y_train)
        print("[DEBUG][NAIVE BAYES MODEL] Dumping Model...")
        joblib.dump(self.model, self.model_file)
        print("[DEBUG][NAIVE BAYES MODEL] Model Dumped!")

    def predict(self, data):
        if not self.model:
            self.model = joblib.load(self.model_file)
        X = pd.DataFrame([data])
        y_pred = self.model.predict(X)
        return y_pred[0]


class FootballPredictionModel:
    def __init__(self, file_path):
        self.data = pd.read_excel(file_path)

    def preprocess_data(self):
        X = self.data.drop(columns=['home', 'away', 'status', 'home_score', 'away_score'])
        y_status = self.data['status']
        y_home_score = self.data['home_score']
        y_away_score = self.data['away_score']
        return X, y_status, y_home_score, y_away_score

    def train_and_save_model(self, model_name):
        X, y_status, y_home_score, y_away_score = self.preprocess_data()
        if model_name == 'Logistic Regression':
            status_model = LogisticRegression()
            home_score_model = LogisticRegression()
            away_score_model = LogisticRegression()
        elif model_name == 'Decision Tree':
            status_model = DecisionTreeClassifier()
            home_score_model = DecisionTreeClassifier()
            away_score_model = DecisionTreeClassifier()
        elif model_name == 'Random Forest':
            status_model = RandomForestClassifier()
            home_score_model = RandomForestClassifier()
            away_score_model = RandomForestClassifier()
        elif model_name == 'SVM':
            status_model = SVC()
            home_score_model = SVC()
            away_score_model = SVC()
        elif model_name == 'Naive Bayes':
            status_model = GaussianNB()
            home_score_model = GaussianNB()
            away_score_model = GaussianNB()
        else:
            raise ValueError("Invalid model name")

        # Train the models
        status_model.fit(X, y_status)
        joblib.dump(status_model, f'{model_name}_status_model.joblib')

        home_score_model.fit(X, y_home_score)
        joblib.dump(home_score_model, f'{model_name}_home_score_model.joblib')

        away_score_model.fit(X, y_away_score)
        joblib.dump(away_score_model, f'{model_name}_away_score_model.joblib')

    def load_model(self, model_name, outcome):
        return joblib.load(f'{model_name}_{outcome}_model.joblib')

    def predict(self, data, expected_outcome, algorithm):
        X = pd.DataFrame([data])
        model_name = algorithm
        outcome_model = self.load_model(model_name, expected_outcome)
        return outcome_model.predict(X)

# # Example usage
# data = {'home_odd': 5.4, 'away_odd': 1.56, 'odd_difference': 3.84, 'strong_home': 1, 'strong_away': 0, 'strong_draw': 1, 'weak_home': 0, 'weak_away': 0}
#
# football_model = FootballPredictionModel('ml2.xlsx')
# status_prediction = football_model.predict(data, 'status', 'Logistic Regression')
# home_score_prediction = football_model.predict(data, 'home_score', 'Random Forest')
# away_score_prediction = football_model.predict(data, 'away_score', 'Decision Tree')
#
# print("Status prediction using Logistic Regression:", status_prediction[0])
# print("Home score prediction using Random Forest:", home_score_prediction[0])
# print("Away score prediction using Decision Tree:", away_score_prediction[0])
