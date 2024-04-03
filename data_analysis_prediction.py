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
            # print("[] Training model...")
            df = self.clean_data(data_file)
            X = df.drop(columns=['status'])
            y = df['status']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = LogisticRegression()
            self.model.fit(X_train, y_train)
            joblib.dump(self.model, self.model_file)
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
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = DecisionTreeClassifier()
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, self.model_file)

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
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier()
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, self.model_file)

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
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = SVC()
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, self.model_file)

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
        df = self.clean_data(data_file)
        X = df.drop(columns=['status'])
        y = df['status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = GaussianNB()
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, self.model_file)

    def predict(self, data):
        if not self.model:
            self.model = joblib.load(self.model_file)
        X = pd.DataFrame([data])
        y_pred = self.model.predict(X)
        return y_pred[0]

