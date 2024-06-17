# testing result extractor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
from datetime import datetime


def get_today():
    # Get today's date
    today = datetime.today()

    # Extract the day component
    day = today.day

    return day


main_url = 'https://www.sportybet.com/'
data_url = 'https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets/detail/240420045904ord28819061'
sport = 'football'

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


def update_excel_data(new_data_list, sport, excel_file):
    # Load the Excel file
    # if sport == 'football':
    #     excel_file = 'ml.xlsx'
    #     # excel_file = 'ml_fb.xlsx'
    # elif sport == 'basketball':
    #     excel_file = 'ml_bb.xlsx'

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
            version1 = False
            if sport == 'football':
                if 'home_score' not in df.columns:
                    version1 = True
                    df['home_score'] = ''
                if 'away_score' not in df.columns:
                    df['away_score'] = ''
            # elif sport == 'basketball':
            #     if 'home_score_actual' not in df.columns:
            #         df['home_score_actual'] = ''
            #     if 'away_score_actual' not in df.columns:
            #         df['away_score_actual'] = ''



            # Update home_score and away_score columns
            if sport == 'football':
                if version1 is True:
                    df.loc[match_index, 'home_score'] = home_score
                    df.loc[match_index, 'away_score'] = away_score
            # elif sport == 'basketball':
            #     df.loc[match_index, 'home_score_actual'] = home_score
            #     df.loc[match_index, 'away_score_actual'] = away_score

    # Convert 'home_score' and 'away_score' columns to numeric
    if sport == 'football':
        df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
        df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
    elif sport == 'basketball':
        df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
        df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
        # df['home_score_actual'] = pd.to_numeric(df['home_score_actual'], errors='coerce')
        # df['home_score_actual'] = pd.to_numeric(df['home_score_actual'], errors='coerce')

    # Remove rows with status 'pending'
    # df = df[df['status'] != 'pending']updateDataWithCurrentResult.py:164

    # Write the updated DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)
    print("Data updated successfully.")
hdList = ["104", "500","302", '401','212', '203']    # code for home or draw
adList = [ '041']    # code for away or draw
haList = ["140", "311","050","320", '221','410']
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


def extract_data(driver):
    try:
        # print('done loading data url....')
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, data_table_class))
        )
        time.sleep(2)
        # print('Extracting data')
        # get the table
        table = driver.find_element(By.CSS_SELECTOR, data_table_class)

        # get all rows
        rows = table.find_elements(By.CSS_SELECTOR, row_data_class)
        # print(f">>>total row data: {len(rows)}")

        # loop through the rows
        bb_data = []
        fb_data = []
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

            # data.append((homeTeam, awayTeam, homeScore, awayScore, result))
            if int(homeScore) > 10 and int(awayScore) > 10:
                bb_data.append((homeTeam, awayTeam, homeScore, awayScore, result))
            else:
                fb_data.append((homeTeam, awayTeam, homeScore, awayScore, result))

        return fb_data, bb_data
    except Exception as e:
        print(f"An error occurred in Extract_Data(): {e}")
        pass


def get_urls_with_data(driver, currentDate, start_page=1):
    print(F"[DEBUG] using date:{currentDate} and starting page of: {start_page}")
    football_data = []
    basketball_data = []

    # current_date = int(currentDate)
    current_date = [int(x) for x in currentDate]
    cap = 0
    for page_no in range(start_page, 100):
        page_url = f"https://www.sportybet.com/ng/my_accounts/bet_history/sport_bets?page={page_no}"
        date_css = "span.m-order-left"
        bar_css = "div.m-order-bar"

        # print(f'loading page {page_url}')
        time.sleep(1)
        try:
            driver.get(page_url)
        except TimeoutException:
            pass

        for x in range(5):
            print(f"\rWorking on [{x+1}/5]: {page_url}", end="")

            # waiting for element to be visible
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, bar_css))
            )

            # get all bars gray or green on the page
            all_bars = driver.find_elements(By.CSS_SELECTOR, bar_css)

            # get all dates on the page
            all_dates = driver.find_elements(By.CSS_SELECTOR, date_css)

            time.sleep(1)

            # get day from the date on this current page
            dt = all_dates[x].text

            # click the bar (booked game to reveal all the games)
            all_bars[x].click()

            # extract day out of the date
            today = str(dt).split("/")[0]
            time.sleep(3)

            # Data Extraction on current page
            print(f"\rWorking on [{x + 1}/5][Extracting Data]: {page_url}", end="")
            fb_data, bb_data = extract_data(driver)

            football_data.extend(fb_data)
            basketball_data.extend(bb_data)

            # if str(today).strip() != str(current_date).strip():
            if int(today.strip()) not in current_date:
                # cap += 1
                # if cap < 5:
                #     print(f"DATE OUT OF RANGE, TRYING NEXT...")
                #     continue
                # else:
                print()
                print(f"CURRENT DATE SPECIFIED COMPLETED!")
                return football_data, basketball_data

            driver.back()
            time.sleep(3)
        print()

    # return url_list
    return football_data, basketball_data


#-----------------------------------------------------------------
# ENTRY
#-----------------------------------------------------------------
dt = input("Specify date(day): ")
if dt == "":
    dt =[get_today()]
else:
    if "," not in dt:
        dt = [dt]
    else:
        dt = dt.split(",")
    # dt = int(dt)

startPage = input("Specify start page: ")
if startPage == "":
    startPage = 1
else:
    startPage = int(startPage)

driver = webdriver.Chrome()

# got to the web page
driver.set_page_load_timeout(30)
print('trying to login...')
login_to_sportybet(driver, '8022224284', "Afolayemi1")
print('done logging in')

time.sleep(5)
footballData, basketballData = get_urls_with_data(driver, dt, startPage)
print()

if len(footballData) > 1:
    print("updating football data on file..")
    # update_excel_data(footballData, sport="football", excel_file="ml.xlsx")
    update_excel_data(footballData, sport="football", excel_file="ml_fb.xlsx")

if len(basketballData) > 1:
    print("updating basketball data on file..")
    update_excel_data(basketballData, sport="basketball", excel_file="ml_bb.xlsx")

