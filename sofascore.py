from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from predict import FootballPrediction
import os
import pandas as pd
import ast  # To evaluate the string representation of the dictionary
import re


def initialize_browser():
    # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
    return webdriver.Chrome()


def load_url(driver, url):
    # Navigate to the webpage
    driver.get(url)


def search_text(driver, text_to_search):
    try:
        # Wait for the input element to be visible
        # print('waiting for input element')
        input_element = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'sc-30244387-0.hiFyBG'))
        )
        # print('input element ready! moving forward')

        # Clear any existing text in the input field
        input_element.clear()

        # Insert the desired text into the input field
        input_element.send_keys(text_to_search)

        # Perform the search (press Enter)
        input_element.send_keys(Keys.RETURN)

    except Exception as e:
        print(f"Error: {e}")


def get_first_href(driver):
    # # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
    # driver = webdriver.Chrome()
    #
    # # Navigate to the webpage
    # driver.get(url)

    try:
        # Locate the first anchor tag with the specified class
        first_href = driver.find_element(By.CSS_SELECTOR, 'div.sc-fqkvVR a.sc-bbd8cee0-0.jeQTnS').get_attribute('href')

        return first_href

    except Exception as e:
        print(f"Error: {e}")


def select_option(driver, option_text):
    # Find the button to open the dropdown
    # dropdown_button = driver.find_element(By.CLASS_NAME, 'sc-eeDRCY')

    WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.sc-eeDRCY.eGpxD'))
    )
    print('drop down button found on page! Proceeding....')
    # Find the button to open the dropdown
    # dropdown_button = driver.find_element(By.CLASS_NAME, 'sc-eeDRCY.eGpxD')
    dropdown_button = driver.find_elements(By.CSS_SELECTOR, '.sc-eeDRCY.eGpxD')[2]

    # Click the button to open the dropdown
    dropdown_button.click()
    time.sleep(2)

    print('wating for element list to show')
    # Wait for the dropdown options to be visible
    # WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, 'sc-fUnMCh')))
    # WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sc-koXPp.lhwueW')))

    # Find all the options in the dropdown
    # options = driver.find_elements(By.CSS_SELECTOR, '.sc-fUnMCh.iGqHmj li')
    options = driver.find_element(By.CSS_SELECTOR, '.sc-koXPp.lhwueW')
    options.click()

    # # Loop through the options and click the one that matches the given text
    # for option in options:
    #     print(option.text)
    #     if option.text == option_text:
    #         option.click()
    #         break


def extract_football_data_old(driver):
    # Get the HTML content
    html_content = driver.page_source

    # Initialize the dictionary to store extracted data
    football_data = {
        'tournaments': [],
        'matches': []
    }

    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup)

    input("::::")

    # Extract tournament information
    tournament_elements = soup.select('.tournament')
    print(f'\tTotal tournament: {len(tournament_elements)}')

    for tournament_element in tournament_elements:
        tournament_name = tournament_element.find('span', class_='tournament-name').text
        football_data['tournaments'].append({'name': tournament_name})

    # Extract match information
    match_elements = soup.select('.match')
    for match_element in match_elements:
        teams = match_element.find('div', class_='teams').text.split(' vs. ')
        match_date = match_element.find('div', class_='match-date').text
        match_status = match_element.find('div', class_='match-status').text

        match_data = {
            'teams': teams,
            'date': match_date,
            'status': match_status,
            'team_scores': {}
        }

        # Extract team scores
        score_elements = match_element.select('.team-score')
        for i, score_element in enumerate(score_elements):
            team_name = teams[i]
            score = score_element.text
            match_data['team_scores'][team_name] = score

        # Extract match outcome
        match_outcome = match_element.find('div', class_='match-outcome').text
        match_data['outcome'] = match_outcome

        football_data['matches'].append(match_data)

    return football_data
    pass


def get_tag(class_name):
    if str(class_name) == "sc-gFqAkR dclrdQ" or str(class_name) == "sc-gFqAkR gVQqGu":
        return "Home/Away"
    elif "diXcnv currentScore" in str(class_name):
        return "HomeScore"
    elif "brUINp currentScore" in str(class_name):
        return "AwayScore"
    elif str(class_name) == "sc-gFqAkR eUqojZ":
        return "League"
    else:
        return None


def extract_football_data(driver, team):
    parent_container = driver.find_element(By.CSS_SELECTOR, ".sc-fqkvVR.fZdvTU")
    elements = parent_container.find_elements(By.CSS_SELECTOR, "bdi")
    score_box = parent_container.find_elements(By.CSS_SELECTOR,
                                               "div.sc-fqkvVR.sc-dcJsrY.cMBRgs.fVCdFl.sc-e8bb5194-2.dpyLLS.score-box")
    wdls = parent_container.find_elements(By.CSS_SELECTOR, "div.sc-gFqAkR.iPZpuQ")

    # score by both teams
    boxScores = []
    for box in score_box:
        boxScores.append(box.find_elements(By.CSS_SELECTOR, 'span')[0].text)

    # wind draw loss list
    wdl_list = []
    for w in wdls:
        wdl_list.append(w.text)

    sub_dict = {}
    # Extract and print the text and class name of each element
    ha = None
    starting_league = None

    data_ha = None
    data_league = None
    data_homescore = None
    data_awayscore = None

    x = 0
    y = 0

    all_team_data = []

    for element in elements:
        text_content = element.text
        class_name = element.get_attribute('class')
        tag = get_tag(class_name)

        # get data into right container
        if tag is not None:
            if tag == 'Home/Away':
                # trying to set home or away tag
                if ha is None:
                    ha = "Home"
                else:
                    if tag == "Home/Away":
                        if ha == "Home":
                            ha = "Away"
                        else:
                            ha = "Home"

                data_ha = ha

            elif tag == 'League':
                data_league = text_content
            elif tag == "HomeScore":
                data_homescore = text_content
            elif tag == "AwayScore":
                data_awayscore = text_content
            else:
                continue

        if data_league != starting_league:
            starting_league = data_league
        else:
            sub_dict['league'] = data_league
            sub_dict['team'] = team
            if data_ha is not None:
                if data_ha == "Home":
                    sub_dict['home'] = text_content
                else:
                    sub_dict['away'] = text_content
                    data_ha = None
                    if x < len(boxScores):
                        sub_dict['home_score'] = boxScores[x]
                        sub_dict['away_score'] = boxScores[x + 1]
                        if y < len(wdl_list):
                            sub_dict['status'] = wdl_list[y]
                        y += 1
                        x += 2
                    else:
                        sub_dict['home_score'] = "N/A"
                        sub_dict['away_score'] = "N/A"
                    # print(f">> {sub_dict}")
                    all_team_data.append(str(sub_dict))

    return all_team_data


def get_all_team(driver):
    parent_container = driver.find_elements(By.CSS_SELECTOR, ".sc-fqkvVR.sc-dcJsrY.ijyhVl.fFmCDf.sc-4430bda6-0.dMmcA-D")

    teamList = []
    for players in parent_container:
        team_name = players.text.split("\n")[1]
        teamList.append(team_name)

    return teamList


def get_team_list_for(team_member):
    # Example usage:
    url = "https://www.sofascore.com/"
    text_to_search = team_member

    # 1. Initialize the browser
    print("initializing driver...")
    driver = initialize_browser()

    # 2. Load the URL
    print("loading url...")
    load_url(driver, url)

    # 3. Search for text
    print(f"Searching for {text_to_search}")
    search_text(driver, text_to_search)
    time.sleep(1)

    # 4. load the first url
    print(f"getting page url for {text_to_search}")
    href = get_first_href(driver)

    print(f"loading page for {text_to_search}...")
    driver.get(href)
    time.sleep(1)

    # 5. select a display option
    # print("selecting option...")
    # select_option(driver, "full")

    teamList = get_all_team(driver)

    return driver, teamList


# =============================================================================


def get_data_for_prediction(home):
    all_data = []
    # set one of the team name in a league required to get the league and all teams in the league
    league_member = home
    driver, team_list = get_team_list_for(league_member)

    team_list.append(league_member)

    for index, team in enumerate(team_list):
        # 3. Search for text
        while True:
            try:
                print(f"\r[{index + 1}/{len(team_list)}] Extracting Data for {team}", end="")
                search_text(driver, team)
                time.sleep(1)

                # 4. load the first url
                # print(f"getting page url for {team}")
                href = get_first_href(driver)

                # print(f"loading page for {team}...")
                driver.get(href)
                time.sleep(1)

                time.sleep(3)
                # print("Extracting Football data:")
                game_data = extract_football_data(driver, team)
                # print(game_data)
                all_data.extend(game_data)
                print(f'\t |\t saving data for {team}...')
                # print(game_data)
                # print('--------------------------------------')

                save_to_excel(game_data)
                # if ans is True:
                #     print("Saved successfully")
                #     break
                # else:
                #     print("Not saved! Data exists")
                #     break
                # time.sleep(1)
                break
            except:
                print(f"Failed to get {team}! Retrying...")
                time.sleep(2)
                pass

    # print("Saving extracted data to file...")
    #
    # existingData = load_data(use_string=True)
    # if len(str(existingData)) < 10:
    #     with open('datafile.txt', 'w') as f:
    #         f.write(str(all_data))
    # else:
    #     existingData.extend(all_data)
    #
    #     # all_data.extend(existingData)
    #     with open('datafile.txt', 'w', encoding='utf-8') as f:
    #         f.write(str(existingData))


def retrieve_from_excel(filename='datafile.xlsx'):
    try:
        # Load data from the Excel file
        df = pd.read_excel(filename)
    except FileNotFoundError:
        # If the file doesn't exist, return an empty list
        return []

    # Convert DataFrame to a list of dictionaries
    data_list = df.to_dict(orient='records')

    return data_list


def reconfirm_team_name(team_name, data):
    actual_team_name = None

    testlist = str(team_name).strip().split(" ")

    counter = str(data).count(team_name)

    if counter > 10 and len(testlist) > 1:
        return team_name

    if len(testlist) == 1:
        actual_team_name = team_name

    actual_team_name = team_name
    for l in testlist:
        lcount = str(data).count(l)
        if lcount > counter:
            actual_team_name = l

    counter2 = str(data).count(actual_team_name)

    if counter2 == 0:
        return None

    return actual_team_name


def is_data_valid_for(home, away, data):
    h = reconfirm_team_name(home, data)
    a = reconfirm_team_name(away, data)
    print(f"h: {h} --  a: {a}")

    if h is None or a is None:
        return False

    return True


def save_to_excel1(data_list, file_path='datafile.xlsx'):
    try:
        # Try loading existing file or create a new one
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        # Create a new DataFrame if the file doesn't exist
        df = pd.DataFrame()

        # Convert string representation of dictionaries to dictionaries
    data_list = [ast.literal_eval(data) for data in data_list]

    # Convert the list of dictionaries to a DataFrame
    new_data = pd.DataFrame(data_list)

    # Concatenate the existing DataFrame and the new data
    df = pd.concat([df, new_data], ignore_index=True)

    # Save DataFrame to Excel file
    df.to_excel(file_path, index=False)


def save_to_excel(data_list, file_path='datafile.xlsx'):
    try:
        # Try loading existing file
        df = pd.read_excel(file_path)

        # Convert string representation of dictionaries to dictionaries
        data_list = [ast.literal_eval(data) for data in data_list]

        # Convert the list of dictionaries to a DataFrame
        new_data = pd.DataFrame(data_list)

        # Check if the data to be saved already exists in the DataFrame
        if not new_data.equals(df[new_data.columns]):
            # Concatenate the existing DataFrame and the new data
            df = pd.concat([df, new_data], ignore_index=True)

            # Save DataFrame to Excel file
            df.to_excel(file_path, index=False)
            return True
        else:
            print("Data already exists. Skipping saving.")
            return False

    except FileNotFoundError:
        # Create a new DataFrame if the file doesn't exist
        df = pd.DataFrame(data_list)

        # Save DataFrame to Excel file
        df.to_excel(file_path, index=False)


def retrieve_data(file_path='datafile.xlsx'):
    # try:
    #     # Try loading existing file
    #     df = pd.read_excel(file_path)
    #     return df.to_dict('records')
    # except FileNotFoundError:
    #     # Return an empty list if the file doesn't exist
    #     return []

    try:
        # Try loading existing file
        df = pd.read_excel(file_path)

        # Convert 'home_score' and 'away_score' columns to integers
        df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce').astype('Int64')
        df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce').astype('Int64')

        # Exclude rows with blank, NaN, "N/A", or "?" values in 'home_score' and 'away_score'
        df = df.dropna(subset=['home_score', 'away_score'])
        df = df[~df['home_score'].isin(['', 'N/A', '?'])]
        df = df[~df['away_score'].isin(['', 'N/A', '?'])]

        # Return the filtered DataFrame as a list of dictionaries
        return df.to_dict('records')

    except FileNotFoundError:
        # Return an empty list if the file doesn't exist
        return []


def check_team_existence1(team_name, file_path='datafile.xlsx'):
    try:
        # Try loading existing file
        df = pd.read_excel(file_path)
        team_count = df['team'].eq(team_name).sum()
        return team_count > 0, team_count
    except FileNotFoundError:
        # Return False and 0 if the file doesn't exist
        return False, 0

def check_team_existence2(team_name, file_path='datafile.xlsx'):
    try:
        # Try loading existing file
        df = pd.read_excel(file_path)

        # Preprocess team names: remove special characters and convert to lowercase
        team_name = re.sub(r'[^a-zA-Z0-9]', '', team_name.lower())

        # Preprocess existing team names in the DataFrame
        df['team'] = df['team'].apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', str(x).lower()))

        # Check if the preprocessed team name exists in the DataFrame
        team_count = df['team'].eq(team_name).sum()

        return team_count > 0, team_count

    except FileNotFoundError:
        # Return False and 0 if the file doesn't exist
        return False, 0

def check_team_existence(team_name, file_path='datafile.xlsx'):
    try:
        # Try loading existing file
        df = pd.read_excel(file_path)

        # Preprocess team names: remove special characters and convert to lowercase
        team_name = re.sub(r'[^a-zA-Z0-9]', '', team_name.lower())

        # Preprocess existing team names in the DataFrame
        df['team'] = df['team'].apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', str(x).lower()))

        # Check if the preprocessed team name or its partial match exists in the DataFrame
        team_count = df['team'].apply(lambda x: team_name in x).sum()

        return team_count > 0, team_count

    except FileNotFoundError:
        # Return False and 0 if the file doesn't exist
        return False, 0


def predict(home, away):
    print("PREDICTING...")
    home = str(home).title()
    away = str(away).title()

    h, ch = check_team_existence(home)  # h-home, ch-count home
    a, ca = check_team_existence(away)  # a-away, ca-count away
    print(f"home: {home}::{h}")
    print(f"away: {away}::{a}")

    time.sleep(1)

    if bool(h) is False or bool(a) is False:
        print(f"No data for teams! Getting data online")
        if bool(h) is False:
            get_data_for_prediction(home)
        else:
            get_data_for_prediction(away)
    else:
        print('Everythin is alright!')

    newdata = retrieve_data()
    # print(newdata)

    predict_engine = FootballPrediction()
    home = reconfirm_team_name(home, newdata)
    away = reconfirm_team_name(away, newdata)

    prediction = predict_engine.analyze_matches(newdata, home, away)
    print(prediction)


# USAGE
# ------------


home = 'Peterborough United Reserve'
away = 'Crewe Alexandra'



predict(home, away)

# # Don't forget to close the browser when you are done
# # # driver.quit()
# # input('wait')
