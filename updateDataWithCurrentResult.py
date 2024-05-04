# testing result extractor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time

main_url = 'https://www.sportybet.com/'
data_url = 'https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420045904ord28819061'


def login_to_sportybet(driver, username, password):

    # Navigate to the main URL
    try:
        driver.get('https://www.sportybet.com/')
    except TimeoutException:
        pass

    try:
        # Find the username field and enter the username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="phone"]'))
        )
        username_field.send_keys(username)

        # Find the password field and enter the password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="psd"]'))
        )
        password_field.send_keys(password)

        # Find the login button and click
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="logIn"]'))
        )
        login_button.click()
        time.sleep(2)

        # # Wait for the login process to complete
        # WebDriverWait(driver, 10).until(
        #     EC.url_changes(driver.current_url)
        # )

        # Optional: You can add more actions after successful login

    finally:
        # Close the browser session
        pass


def update_excel_data_old(new_data):
    # Load the Excel file
    excel_file = 'ml.xlsx'
    df = pd.read_excel(excel_file)
    # print(df)

    # Unpack the new data tuple
    home, away, home_score, away_score, status = new_data

    # Check if the home and away teams exist in the DataFrame
    match_index = df[(df['home'].str.strip() == home) & (df['away'].str.strip() == away)].index

    if len(match_index) > 0:
        match_index = match_index[0]  # Get the first matching index

        # Update the status column
        df.loc[match_index, 'status'] = status

        # Add home_score and away_score columns if not already present
        if 'home_score' not in df.columns:
            df['home_score'] = ''
        if 'away_score' not in df.columns:
            df['away_score'] = ''

        # Update home_score and away_score columns
        df.loc[match_index, 'home_score'] = home_score
        df.loc[match_index, 'away_score'] = away_score

        # Write the updated DataFrame back to the Excel file
        df.to_excel(excel_file, index=False)
        print("Data updated successfully.")
    else:
        print("No matching data found.")


def update_excel_data(new_data_list):
    # Load the Excel file
    excel_file = 'ml.xlsx'
    df = pd.read_excel(excel_file)

    for new_data in new_data_list:
        print(f"working on {new_data}....")
        # Unpack the new data tuple
        home, away, home_score, away_score, status = new_data

        # Check if the home and away teams exist in the DataFrame
        match_index = df[(df['home'].str.strip() == home) & (df['away'].str.strip() == away)].index

        if len(match_index) > 0:
            match_index = match_index[0]  # Get the first matching index

            # Update the status column
            df.loc[match_index, 'status'] = status

            # Add home_score and away_score columns if not already present
            if 'home_score' not in df.columns:
                df['home_score'] = ''
            if 'away_score' not in df.columns:
                df['away_score'] = ''

            # Update home_score and away_score columns
            df.loc[match_index, 'home_score'] = home_score
            df.loc[match_index, 'away_score'] = away_score

    # Convert 'home_score' and 'away_score' columns to numeric
    df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
    df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')

    # Remove rows with status 'pending'
    df = df[df['status'] != 'pending']

    # Write the updated DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)
    print("Data updated successfully.")

'''
table: div.m-order-detail-wrap.list
each row: div.selection-detail-wrap
data: div.selection-body (this can replace each row as it's unique in each row)
home: p.team-label home (.text)
away: p.team-label (.text)
home score = div.home-score main (.text)
away score = div.away-score main (.text)
'''

data_table_class = 'div.m-order-detail-wrap.list'
row_data_class = 'div.selection-body'
home_team_class = 'p.team-label.home'
away_team_class = 'p.team-label'
team_label_class = 'team-label'
home_score_class = 'div.home-score.main'
away_score_class = 'div.away-score.main'

ans = input("Have you updated the url list for the last game? ")

if ans == 'y' or ans == 'Y' or ans == '':
    # load the web browser
    driver = webdriver.Chrome()

    # got to the web page
    driver.set_page_load_timeout(30)
    print('trying to login...')
    login_to_sportybet(driver, '8022224284', "Afolayemi1")
    print('done logging in')

    time.sleep(5)

    urls_string = """https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503080821ord92237722
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503115908ord98962774
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503122454ord99784272
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503170228ord09052998
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503170913ord09262411
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503171906ord09601558
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503172115ord09670679
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503172529ord09814755
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503174936ord10628367
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503215002ord19300820
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503215239ord19380176
https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240503215746ord19537281"""

    urls = urls_string.split("\n")
    data = []
    for index, url in enumerate(urls):
        print(f"Loading and extracting data page {index}...")
        try:
            print('loading data url...')
            # print(data_url)
            driver.get(url)
        except TimeoutException:
            pass

        # print('done loading data url....')
        WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, data_table_class))
                )
        time.sleep(2)
        print('Extracting data')
        # get the table
        table = driver.find_element(By.CSS_SELECTOR, data_table_class)

        # get all rows
        rows = table.find_elements(By.CSS_SELECTOR, row_data_class)
        # print(f">>>total row data: {len(rows)}")

        # loop through the rows

        for row in rows:
            # homeTeam = row.find_element(By.CSS_SELECTOR,home_team_class).text
            # awayTeam = row.find_element(By.CSS_SELECTOR, away_team_class).text
            try:
                homeScore = row.find_element(By.CSS_SELECTOR, home_score_class).text
                awayScore = row.find_element(By.CSS_SELECTOR, away_score_class).text
            except:
                homeScore = "-"
                awayScore = '-'

            teams = row.find_elements(By.CLASS_NAME, team_label_class)
            homeTeam = teams[0].text
            awayTeam = teams[1].text

            result = None
            try:
                if int(homeScore) > int(awayScore):
                    result = "H"
                elif int(homeScore) < int(awayScore):
                    result = "A"
                elif int(homeScore) == int(awayScore):
                    result = "D"
            except:
                result = None
                continue

            data.append((homeTeam, awayTeam, homeScore, awayScore, result))


    # for d in data:
    #     print(d)

    update_excel_data(data)
