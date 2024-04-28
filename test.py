# # # testing result extractor
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.webdriver.common.keys import Keys
# # from selenium.common.exceptions import TimeoutException
# # import pandas as pd
# # import time
# #
# # main_url = 'https://www.sportybet.com/'
# # data_url = 'https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420045904ord28819061'
# #
# #
# # def login_to_sportybet(driver, username, password):
# #
# #     # Navigate to the main URL
# #     try:
# #         driver.get('https://www.sportybet.com/')
# #     except TimeoutException:
# #         pass
# #
# #     try:
# #         # Find the username field and enter the username
# #         username_field = WebDriverWait(driver, 10).until(
# #             EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="phone"]'))
# #         )
# #         username_field.send_keys(username)
# #
# #         # Find the password field and enter the password
# #         password_field = WebDriverWait(driver, 10).until(
# #             EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="psd"]'))
# #         )
# #         password_field.send_keys(password)
# #
# #         # Find the login button and click
# #         login_button = WebDriverWait(driver, 10).until(
# #             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="logIn"]'))
# #         )
# #         login_button.click()
# #         time.sleep(2)
# #
# #         # # Wait for the login process to complete
# #         # WebDriverWait(driver, 10).until(
# #         #     EC.url_changes(driver.current_url)
# #         # )
# #
# #         # Optional: You can add more actions after successful login
# #
# #     finally:
# #         # Close the browser session
# #         pass
# #
# #
# # def update_excel_data_old(new_data):
# #     # Load the Excel file
# #     excel_file = 'ml.xlsx'
# #     df = pd.read_excel(excel_file)
# #     # print(df)
# #
# #     # Unpack the new data tuple
# #     home, away, home_score, away_score, status = new_data
# #
# #     # Check if the home and away teams exist in the DataFrame
# #     match_index = df[(df['home'].str.strip() == home) & (df['away'].str.strip() == away)].index
# #
# #     if len(match_index) > 0:
# #         match_index = match_index[0]  # Get the first matching index
# #
# #         # Update the status column
# #         df.loc[match_index, 'status'] = status
# #
# #         # Add home_score and away_score columns if not already present
# #         if 'home_score' not in df.columns:
# #             df['home_score'] = ''
# #         if 'away_score' not in df.columns:
# #             df['away_score'] = ''
# #
# #         # Update home_score and away_score columns
# #         df.loc[match_index, 'home_score'] = home_score
# #         df.loc[match_index, 'away_score'] = away_score
# #
# #         # Write the updated DataFrame back to the Excel file
# #         df.to_excel(excel_file, index=False)
# #         print("Data updated successfully.")
# #     else:
# #         print("No matching data found.")
# #
# #
# # def update_excel_data(new_data_list):
# #     # Load the Excel file
# #     excel_file = 'ml.xlsx'
# #     df = pd.read_excel(excel_file)
# #
# #     for new_data in new_data_list:
# #         print(f"working on {new_data}....")
# #         # Unpack the new data tuple
# #         home, away, home_score, away_score, status = new_data
# #
# #         # Check if the home and away teams exist in the DataFrame
# #         match_index = df[(df['home'].str.strip() == home) & (df['away'].str.strip() == away)].index
# #
# #         if len(match_index) > 0:
# #             match_index = match_index[0]  # Get the first matching index
# #
# #             # Update the status column
# #             df.loc[match_index, 'status'] = status
# #
# #             # Add home_score and away_score columns if not already present
# #             if 'home_score' not in df.columns:
# #                 df['home_score'] = ''
# #             if 'away_score' not in df.columns:
# #                 df['away_score'] = ''
# #
# #             # Update home_score and away_score columns
# #             df.loc[match_index, 'home_score'] = home_score
# #             df.loc[match_index, 'away_score'] = away_score
# #
# #     # Convert 'home_score' and 'away_score' columns to numeric
# #     df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
# #     df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
# #
# #     # Remove rows with status 'pending'
# #     df = df[df['status'] != 'pending']
# #
# #     # Write the updated DataFrame back to the Excel file
# #     df.to_excel(excel_file, index=False)
# #     print("Data updated successfully.")
# #
# # '''
# # table: div.m-order-detail-wrap.list
# # each row: div.selection-detail-wrap
# # data: div.selection-body (this can replace each row as it's unique in each row)
# # home: p.team-label home (.text)
# # away: p.team-label (.text)
# # home score = div.home-score main (.text)
# # away score = div.away-score main (.text)
# # '''
# #
# # data_table_class = 'div.m-order-detail-wrap.list'
# # row_data_class = 'div.selection-body'
# # home_team_class = 'p.team-label.home'
# # away_team_class = 'p.team-label'
# # team_label_class = 'team-label'
# # home_score_class = 'div.home-score.main'
# # away_score_class = 'div.away-score.main'
# #
# # # load the web browser
# # driver = webdriver.Chrome()
# #
# # # got to the web page
# # driver.set_page_load_timeout(30)
# # print('trying to login...')
# # login_to_sportybet(driver, '8022224284', "Afolayemi1")
# # print('done logging in')
# # time.sleep(5)
# #
# # urls = [
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420045904ord28819061",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420051900ord29081319",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420134051ord52427015",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420141346ord54122793",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420143842ord55118646",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420152714ord57391458",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420192347ord66572238",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420192524ord66610824",
# #     "https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420195420ord67294812"
# # ]
# # data = []
# # for index, url in enumerate(urls):
# #     print(f"Loading and extracting data page {index}...")
# #     try:
# #         print('loading data url...')
# #         # print(data_url)
# #         driver.get(url)
# #     except TimeoutException:
# #         pass
# #
# #     # print('done loading data url....')
# #     WebDriverWait(driver, 60).until(
# #                 EC.presence_of_element_located((By.CSS_SELECTOR, data_table_class))
# #             )
# #     time.sleep(2)
# #     print('Extracting data')
# #     # get the table
# #     table = driver.find_element(By.CSS_SELECTOR, data_table_class)
# #
# #     # get all rows
# #     rows = table.find_elements(By.CSS_SELECTOR, row_data_class)
# #     # print(f">>>total row data: {len(rows)}")
# #
# #     # loop through the rows
# #
# #     for row in rows:
# #         # homeTeam = row.find_element(By.CSS_SELECTOR,home_team_class).text
# #         # awayTeam = row.find_element(By.CSS_SELECTOR, away_team_class).text
# #         try:
# #             homeScore = row.find_element(By.CSS_SELECTOR, home_score_class).text
# #             awayScore = row.find_element(By.CSS_SELECTOR, away_score_class).text
# #         except:
# #             homeScore = "-"
# #             awayScore = '-'
# #
# #         teams = row.find_elements(By.CLASS_NAME, team_label_class)
# #         homeTeam = teams[0].text
# #         awayTeam = teams[1].text
# #
# #         result = None
# #         try:
# #             if int(homeScore) > int(awayScore):
# #                 result = "H"
# #             elif int(homeScore) < int(awayScore):
# #                 result = "A"
# #             elif int(homeScore) == int(awayScore):
# #                 result = "D"
# #         except:
# #             result = None
# #             continue
# #
# #         data.append((homeTeam, awayTeam, homeScore, awayScore, result))
# #
# #
# # # for d in data:
# # #     print(d)
# #
# # update_excel_data(data)
#
#
# import Levenshtein
#
# def are_similar(string1, string2, threshold=0.3):
#     """
#     Check if two strings are similar based on Levenshtein distance.
#
#     Args:
#     string1 (str): First string.
#     string2 (str): Second string.
#     threshold (float): Similarity threshold. Default is 0.8.
#
#     Returns:
#     bool: True if the strings are similar, False otherwise.
#     """
#     distance = Levenshtein.distance(string1.lower(), string2.lower())
#
#     max_length = max(len(string1), len(string2))
#     similarity = 1 - (distance / max_length)
#     return similarity >= threshold
#
# # Test cases
# sample_data = [
#     ("Stade Lausanne Ouchy", "Stade Ls Ouchy"),
#     ("Grasshopper Club Zurich", "Grasshoppers"),
#     ("OFI Crete", "OFI"),
#     ("Volos NPS", "Volos"),
#     ("Kuwait", "Al-Kuwait"),
#     ("FC Vaduz", "Vaduz"),
#     ("FC Wil 1900", "FC Wil"),
#     ('FC Vaduz', 	'Baden'),
#     ('FC Metalist 1925 Kharkiv' ,	'Metalist 1925 U19')
# ]
#
# # for string1, string2 in sample_data:
# #     print(f"{string1} : {string2} -> Similar: {are_similar(string1, string2)}")
#
#
#
# def are_the_same(a, b):
#
#     small = None
#
#     if len(a) < len(b):
#         small = a
#         big = b
#     else:
#         small = b
#         big = a
#
#     big = big.replace("-", " ")
#     small = small.replace("-", " ")
#
#     small_list = str(small).split(" ")
#     big_list = str(big).split(" ")
#
#     trueCounter = 0
#     falseCounter = 0
#     for tester in small_list:
#         if tester in big_list:
#             trueCounter += 1
#         else:
#             found = False
#             if len(tester) > 2:
#                 for b in big_list:
#                     if tester[:-1] == b or b[:-1] == tester:
#                         trueCounter += 1
#                         found = True
#                         break
#
#                 if found is True:
#                     break
#                 else:
#                     falseCounter += 1
#
#     same = trueCounter > falseCounter
#     return same
#
#
#
# for data in sample_data:
#     a = data[0]
#     b = data[1]
#     print(f"{a}, {b} | same: {are_the_same(a,b)}")


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Embedded Chrome Browser")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.browser_widget = QWidget()
        self.browser_widget.setLayout(layout)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        self.setCentralWidget(self.browser_widget)

        self.init_browser()

    def init_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://www.example.com")  # Load a website
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for page to load
        html = driver.page_source
        self.webview.setHtml(html)

        driver.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
