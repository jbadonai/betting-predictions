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
from difflib import SequenceMatcher
from selenium.common.exceptions import TimeoutException


from pattern import CombinationAnalyzer
from data_extractor import PreviousRecordExtractor
from data_analysis_prediction import *

# timeout = 15
teamData = 'teamList.txt'

def initialize_browser():
    # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
    return webdriver.Chrome()


def load_url(driver, url, set_timeout=True):
    # global timeout
    # Navigate to the webpage
    # driver.get(url)
    # if set_timeout is True:
    #     print(">>> using timeout")
    #     driver.set_page_load_timeout(timeout)
    # else:
    #     print(">>> Not using timeout")

    try:
        # Attempt to navigate to the URL within the specified timeout period
        driver.get(url)

        # print("Checking if page loads successfully. Please wait....")
        # wait_for_element(driver, 'sc-30244387-0.hiFyBG')

        return True
    except TimeoutException:
        # Handle the timeout exception here (e.g., print an error message)
        print("Page load timed out")
        return True
        pass
    except Exception as e:
        print(f"Error! Retrying[timeout ={timeout}] [url: {url}]...")
        timeout += 5
        return False
        # time.sleep(5)
        # load_url(driver, url)


def search_text(driver, text_to_search):
    try:
        # Wait for the input element to be visible
        # print('waiting for input element')
        input_element = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'sc-30244387-0.hiFyBG'))
        )
        print('input element ready! moving forward')

        # Clear any existing text in the input field
        input_element.clear()

        # Insert the desired text into the input field
        input_element.send_keys(text_to_search)

        # Perform the search (press Enter)
        input_element.send_keys(Keys.RETURN)

    except Exception as e:
        print(f"Error: {e}")


def wait_for_element(driver, element_class, selector = 'class'):
    try:
        if selector == 'class':
            input_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, element_class))
            )
        if selector == 'css':
                input_element = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, element_class))
            )


    except Exception as e:
        pass


def get_first_href(driver):
    all_search_list_class = 'sc-fqkvVR.sc-fUnMCh.esJGSi.hkwHv.ps ps--active-y'
    each_team_link_class = 'sc-bbd8cee0-0.jeQTnS'  # has href and other data
    game_confirmation_class = 'sc-gFqAkR.hzPof'  # under each team lnk class

    try:
        # wait for all list to be visible
        # print('waiting for list links to apperar...')
        wait_for_element(driver, all_search_list_class)

        # print('getting all links in the list')
        all_links = driver.find_elements(By.CLASS_NAME, each_team_link_class)
        # print(f"total links obtained: {len(all_links)}")
        # print('scanning the links...')
        for link in all_links:
            game = link.find_element(By.CLASS_NAME, game_confirmation_class).text
            # print(f"game: {game}")

            if str(game).lower() == 'football':
                team_url = link.get_attribute('href')
                print(f"Team URL: {team_url}")
                # print("FOUND!!!!!!")
                return team_url

    except Exception as e:
        return None
        pass

    # try:
    #     print('WAITING FOR SEARCH LIST...')
    #     wait_for_element(driver, 'div.sc-fqkvVR', 'css')
    #
    #     # Locate the first anchor tag with the specified class
    #     first_href = driver.find_element(By.CSS_SELECTOR, 'div.sc-fqkvVR a.sc-bbd8cee0-0.jeQTnS').get_attribute('href')
    #
    #     return first_href
    # except Exception as e:
    #     print(f"Error: {e}")


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
    gameData = []
    data_table_class = "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.iGqHmj a.sc-631ef08b-0"
    # data_table_class = "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.buMHXe"
    ha_class = "sc-gFqAkR"

    table = driver.find_elements(By.CSS_SELECTOR, data_table_class)
    singleGameData = {}
    for table_data in table:
        try:
            ha = table_data.find_elements(By.CLASS_NAME, ha_class)

            # for index, h in enumerate(ha):
            #     print(f"{index} <> {h.text}")
            #
            # input('waiting..................')

            home = ha[4].text
            away = ha[5].text
            home_score = ha[6].text
            away_score = ha[8].text
            wld = ha[10].text

            singleGameData['league'] = "my league"
            singleGameData['team'] = team
            singleGameData['home'] = home
            singleGameData['away'] = away
            singleGameData['home_score'] = home_score
            singleGameData['away_score'] = away_score
            singleGameData['status'] = wld

            gameData.append(str(singleGameData))

            # print(f"[{len(ha)}]home: {home}, away: {away}, home score: {home_score}, away score: {away_score}, wLD: {wld}")
        except Exception as e:
            print(f"error:-----------")
            continue


    return gameData
    pass


def extract_football_data_old(driver, team):
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
    re_structure = False

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

                    # check if team name is the same as either home or away. to ensure consistency in the name
                    if sub_dict['team'] == sub_dict['home'] or sub_dict['team'] == sub_dict['away']:
                        all_team_data.append(str(sub_dict))
                        pass
                    else:
                        # if team name is not the same as the home or away team check:
                        # 1. if both name are not empty
                        if sub_dict['home'] == "" and sub_dict['away'] == "":
                            # if both happen to be empty the data is wrong. skip it and continue
                            continue

                        # 2. if any of the name is not empty and fix if empty
                        # tryi and see if home or away team name is missing, then fix
                        if sub_dict['home'] == "":
                            sub_dict['home'] = sub_dict['team']
                            all_team_data.append(str(sub_dict))
                            print(f"[DOCTOR] Gap in home Filled")
                            continue
                        elif sub_dict['away'] == "":
                            sub_dict['away'] = sub_dict['team']
                            all_team_data.append(str(sub_dict))
                            print(f"[DOCTOR] Gap in Away Filled")
                            continue


                        # 3. if none of them is empty there there is conflict in the names
                        # a. first detect which name is common to all and that will be the team name
                        # b. change the team name to this
                        # these can only be done if we have all the data. but in this loop only one data is available
                        # so we will do this step outside this loop when all data has been obained
                        # but we need to set a trigger to do this check using restructure

                        re_structure = True
                        all_team_data.append(str(sub_dict))

    if re_structure is True:
        # print(f"RESTRUCTURING..............")
        # print(all_team_data)
        # print('----------------------------------------------------------------------------------------------')
        new_all_team_data = []
        # restructure: sychronize team name properly with home / away before returning data.
        # get and use the first 3 element to do comparism and correction
        actual_team = None

        first = eval(all_team_data[0])
        second = eval(all_team_data[1])
        third = eval(all_team_data[2])

        if second['home'] == third['home']:
            actual_team = second['home']
        elif second['home'] == third['away']:
            actual_team = second['home']
        elif second['away'] == third['home']:
            actual_team = second['away']
        elif second['away'] == third['away']:
            actual_team = second['away']

        # now loop through all the list to effect the actual team name
        if actual_team is not None:
            for team in all_team_data:
                new_team = eval(team)
                new_team['team'] = actual_team
                new_all_team_data.append(str(new_team))

            print('[DOCTOR] Data Fixed! There is consistency in the name now')
            return new_all_team_data
            pass
        else:
            print("This one mad ooooooooooo. How can it still happen! we'll stick to normal")
            return all_team_data
        pass

    else:
        return all_team_data


def get_all_team(driver):
    parent_container = driver.find_elements(By.CSS_SELECTOR, ".sc-fqkvVR.sc-dcJsrY.ijyhVl.fFmCDf.sc-4430bda6-0.dMmcA-D")

    teamList = []
    for players in parent_container:
        team_name = players.text.split("\n")[1]
        teamList.append(team_name)

    return teamList


def get_team_list_for(team_member):
    # GOTO URL
    # -----------------------------------------------------------------------------
    url = "https://www.sofascore.com/"

    # INSTANTIATE TEXT TO SEARCH
    # -----------------------------------------------------------------------------
    text_to_search = team_member

    # 1. INITIALIZEING BROWSER
    # -----------------------------------------------------------------------------
    print("initializing driver...")
    driver = initialize_browser()

    # 2. LOADING URL
    # -----------------------------------------------------------------------------
    print("loading url...")
    while True:
        ans = load_url(driver, url)
        if ans is True:
            break
        else:
            time.sleep(2)

    # 3. SEARCH FOR THE TEAM (which updates the driver with the list of searched results
    # -----------------------------------------------------------------------------
    print(f"Searching for {text_to_search}")
    search_text(driver, text_to_search)
    time.sleep(5)

    # 4. GET TEAM URL: SCAN THE SEARCH LIST FOR RIGHT TEAM URL
    # -----------------------------------------------------------------------------
    print(f"getting page url for {text_to_search}")
    href = get_first_href(driver)

    if href is not None:
        # 5. LOAD THE UNIQUE TEAM PAGE IN OTHER TO EXTRACT THEIR DATA
        # -----------------------------------------------------------------------------
        print(f"loading page for {text_to_search}...")
        while True:
            try:
                # driver.get(href)
                print(1)
                load_url(driver, href)
                print(2)

                wait_for_element(driver, "div.sc-fqkvVR.fZdvTU", "css")
                print(3)
                break
            except:
                print("Error loading page! Retrying...")
                driver.refresh()
                time.sleep(2)
        time.sleep(1)

        # 6. EXTRACT DATA FROM THE URL
        # -----------------------------------------------------------------------------
        teamList = get_all_team(driver)

        return driver, teamList
    else:
        get_team_list_for(team_member)


def load_team_page(team_name):
    # GOTO URL
    # -----------------------------------------------------------------------------
    url = "https://www.sofascore.com/"

    # INSTANTIATE TEXT TO SEARCH
    # -----------------------------------------------------------------------------
    text_to_search = team_name

    # 1. INITIALIZEING BROWSER
    # -----------------------------------------------------------------------------
    print("initializing driver...")
    driver = initialize_browser()

    # 2. LOADING URL
    # -----------------------------------------------------------------------------
    print("loading url...")
    while True:
        ans = load_url(driver, url)
        if ans is True:
            break
        else:
            time.sleep(2)

    # 3. SEARCH FOR THE TEAM (which updates the driver with the list of searched results
    # -----------------------------------------------------------------------------
    time.sleep(5)
    print(f"Searching for {text_to_search}")
    search_text(driver, text_to_search)
    time.sleep(5)

    # 4. GET TEAM URL: SCAN THE SEARCH LIST FOR RIGHT TEAM URL
    # -----------------------------------------------------------------------------
    print(f"getting page url for {text_to_search}")
    href = get_first_href(driver)

    # 5. LOAD THE UNIQUE TEAM PAGE IN OTHER TO EXTRACT THEIR DATA
    # -----------------------------------------------------------------------------
    print(f"loading page for {text_to_search}...")
    while True:
        try:
            # driver.get(href)
            load_url(driver, href, False)
            break
        except:
            print("Error loading page! Retrying...")
            driver.refresh()
            time.sleep(2)
    time.sleep(1)

    return driver


# =============================================================================
def get_data_for_prediction_old(team_name, no_team = False):
    all_data = []
    team_list = []

    # set one of the team name in a league required to get the league and all teams in the league
    # league_member = home

    # driver, team_list_temp = get_team_list_for(league_member)
    # LOAD PAGE FOR THE TEAM  IN READINES FOR DATA EXTRACTION
    driver = load_team_page(team_name)

    while True:
        try:
            # TRYING TO EXTRACT GAME DATA
            print(f"\r Extracting Data for {team_name}", end="")
            game_data = extract_football_data(driver, team_name)

            all_data.extend(game_data)
            print(f'\t |\t saving data for {team_name}...')

            save_to_excel(game_data)
            return eval(game_data[0])['team']

        except Exception as e:
            # print(e)
            print(f"Failed to get {team_name}! Refreshing and Retrying...")
            driver.refresh()
            time.sleep(10)
            pass

def get_data_for_prediction(team_name, no_team = False):
    all_data = []

    # LOAD PAGE FOR THE TEAM  IN READINES FOR DATA EXTRACTION
    driver = load_team_page(team_name)
    time.sleep(2)

    while True:
        try:
            # TRYING TO EXTRACT GAME DATA
            print(f"\r Extracting Data for {team_name}", end="")
            game_data = extract_football_data(driver, team_name)
            # print(game_data)
            # input("::::::::::::::::::::::::::::::::::::::::::::::::::::")

            all_data.extend(game_data)
            print(f'\t |\t saving data for {team_name}...')

            save_to_excel(game_data)
            return eval(game_data[0])['team']

        except Exception as e:
            # print(e)
            print(f"Failed to get {team_name}! Refreshing and Retrying...")
            driver.refresh()
            time.sleep(10)
            pass


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


def reconfirm_team_name1(team_name, data):
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


def reconfirm_team_name2(team_name, data):
    print(data)


    for team_details in data:
        homeTeam = ""
        awayTeam = ""

        noMatch = 0

        team = team_details['team']
        home = team_details['home']
        away = team_details['away']

        if team == home or team == away:
            continue
        else:
            print(team, "<>", home, "<>", away)
            noMatch += 1


    print(f"Total No match: {noMatch}")
    input('wait')

    pass


def is_data_valid_for(home, away, data):
    h = reconfirm_team_name(home, data)
    a = reconfirm_team_name(away, data)
    print(f"h: {h} --  a: {a}")

    if h is None or a is None:
        return False

    return True


def save_to_excel(data_list, file_path='datafile.xlsx'):
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


def save_to_excel1(data_list, file_path='datafile.xlsx'):
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


def check_team_existence(team_name, file_path='datafile.xlsx'):
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


def check_team_existence3(team_name, file_path='datafile.xlsx'):
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
    # home = str(home).title()
    # away = str(away).title()

    #  CHECKING IF HOME AND AWAY TEAM ALREADY EXIST IN THE EXCEL SSHEET
    # -----------------------------------------------------------------------------
    h, ch = check_team_existence(home)  # h-home, ch-count home
    a, ca = check_team_existence(away)  # a-away, ca-count away

    time.sleep(1)

    # if bool(h) is False or bool(a) is False:
    #     print(f"No data for teams! Getting data online")
    #     if bool(h) is False:
    #         get_data_for_prediction(home, True)
    #     else:
    #         get_data_for_prediction(away, True)
    # INITIALIZE NEW HOME AND NEW AWAY WITH THE PASSED IN VALUES
    # -----------------------------------------------------------------------------
    new_home = home
    new_away = away

    teamsWithMissingData = []

    # IF HOME OR AWAY IS NOT IN THE DATA BASE, EXTRACT THEIR DATA AND SAVE IN DATABASE
    # -----------------------------------------------------------------------------
    if bool(h) is False:
        # new_home = get_data_for_prediction(home, True)
        teamsWithMissingData.append(home)

    if bool(a) is False:
        # new_away = get_data_for_prediction(away, True)
        teamsWithMissingData.append(away)

    if bool(h) is False or bool(a) is False:
        dataExtractor = PreviousRecordExtractor()
        newTeamName = dataExtractor.start_data_extraction(teamsWithMissingData)

        if newTeamName is None:
            return None

        # print(f"NEW TEAM NAME: {newTeamName}")
        # input("Waiting first..............")
        if len(newTeamName) == 2:
            new_home = newTeamName[0]
            new_away = newTeamName[1]
        elif len(newTeamName) == 1:
            if bool(h) is False:
                new_home = newTeamName[0]
            elif bool(a) is False:
                new_away = newTeamName[0]





    # print(f"{home} ==> {new_home}")
    # print(f"{away} ==> {new_away}")

    # =================================================
    # PREDICTION ACTUALLY STARTS HERE
    # =================================================


    # LOAD DATA FROM THE DATABASE (I.E THE EXCEL SHEET)
    # -----------------------------------------------------------------------------
    newdata = retrieve_data()

    # CREATE AN INSTANCE OF THE PREDICTING ENGINE
    # -----------------------------------------------------------------------------
    predict_engine = FootballPrediction()

    time.sleep(1)

    # PASS THE SAME DATA TO 3 DIFFERENT ALGORITHMS FOR ANALYSIS
    # -----------------------------------------------------------------------------
    a = predict_engine.analyze_matches(newdata, new_home, new_away)
    b = predict_engine.analyze_by_average_goal_scored(newdata, new_home, new_away)
    c = predict_engine.analyze_by_poisson_analysis(newdata, new_home, new_away)

    # EVALUATING THE RESULT FROM THE ALGORITHMS TO MAKE INFORMED DECISION
    # -----------------------------------------------------------------------------
    all = a + b + c
    h_count = all.count("Home")
    a_count = all.count("Away")
    d_count = all.count("Draw")

    def evaluate(text):
        ans = None
        awaycount = str(text).count("Away")
        homecount = str(text).count("Home")
        drawcount = str(text).count("Draw")

        if awaycount == 2:
            return "Strong Away"
        elif homecount == 2:
            return  "Strong Home"
        elif homecount == 1 and drawcount == 1:
            return  "Weak Home"
        elif awaycount == 1 and drawcount == 1:
            return  "Weak Away"
        elif drawcount == 2:
            return "Strong Draw"

    analyzer = CombinationAnalyzer()
    suggestion = analyzer.analyze(evaluate(a), evaluate(b), evaluate(c))

    # print(a, "-", evaluate(a))
    # print(b, "-", evaluate(b))
    # print(c, "-", evaluate(c))
    # print()
    # print(f"H:A:D: {h_count}:{a_count}:{d_count}")
    # print(f"PLAY: {suggestion}")

    # {a} - {evaluate(a)}
    # {b} - {evaluate(b)}
    # {c} - {evaluate(c)}

    odds = get_home_away_odds(home, away)

    deepCheck = deep_check(odds, suggestion)


    ml ={}

    def check_evaluation(test, all_evaluation):
        if str(all_evaluation).strip().lower().__contains__(str(test).lower().strip()):
            return 1
        else:
            return 0

    def save_ml_to_excel(data, filename='ml.xlsx'):
        # Check if file exists
        file_exists = os.path.isfile(filename)

        # Create DataFrame from data
        df = pd.DataFrame([data])

        # Add 'status' column with default value 'pending'
        df['status'] = 'pending'

        # Reorder columns to ensure 'status' is the last column
        column_order = list(df.columns)
        column_order.remove('status')
        column_order.append('status')
        df = df[column_order]

        # Check if file exists and has data
        if file_exists:
            existing_data = pd.read_excel(filename)
            if not existing_data.empty:
                df = pd.concat([existing_data, df], ignore_index=True)

        # Save DataFrame to Excel
        df.to_excel(filename, index=False)

    def save_ml_to_excel_not_working(data, filename='ml.xlsx'):
        # Check if file exists
        file_exists = os.path.isfile(filename)

        # Create DataFrame from data
        df = pd.DataFrame([data])

        # Add 'status' column with default value 'pending'
        df['status'] = 'pending'

        # Reorder columns to ensure 'status' is the last column
        column_order = list(df.columns)
        column_order.remove('status')
        column_order.append('status')
        df = df[column_order]

        # Check if file exists and has data
        if file_exists:
            existing_data = pd.read_excel(filename)
            if not existing_data.empty:
                # Check if any row in the new data already exists in the Excel file
                existing_data_no_status = existing_data.drop(columns=['status'])
                df_no_status = df.drop(columns=['status'])
                if (existing_data_no_status.values == df_no_status.values).any():
                    print("Data already exists in the Excel file. Skipping...")
                    return
                else:
                    with pd.ExcelWriter(filename, mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, index=False, header=False)
            else:
                df.to_excel(filename, index=False)
        else:
            df.to_excel(filename, index=False)

    allEvaluation = f"{evaluate(a)},{evaluate(b)},{evaluate(c)}"

    ml['home'] = home
    ml['away'] = away
    ml['home_odd'] = round(float(odds[0]), 2)
    ml['away_odd'] = round(float(odds[1]), 2)
    ml['odd_difference'] = abs(ml['home_odd'] - ml['away_odd'])
    ml['strong_home'] = check_evaluation('strong home', allEvaluation)
    ml['strong_away'] = check_evaluation('strong away', allEvaluation)
    ml['strong_draw'] = check_evaluation('strong draw', allEvaluation)
    ml['weak_home'] = check_evaluation('weak home', allEvaluation)
    ml['weak_away'] = check_evaluation('weak away', allEvaluation)

    # predict using machine learning based on supplied data ml
    mlData = ml.copy()
    mlData.pop('home')
    mlData.pop('away')
    # print(f"ML: {ml}")
    # print(f"ML Data: {mlData}")
    # input(":::::::::::::::::")
    mlPrediction = ml_prediction(mlData)

    result = f"""
    {a.split("|")[0].split(":")[0].strip()}: {a.split("|")[0].split(":")[1]} | {evaluate(a)},{evaluate(b)},{evaluate(c)}
    Play (deep check): {deepCheck}
    ML: {mlPrediction}
    PLAY: {suggestion}

    ===========================================================================================================
    ===========================================================================================================
        """


    save_ml_to_excel(ml)

    with open("result.txt", 'a', encoding='utf-8') as f:
        f.write(result)

def ml_prediction(data):
    try:
        predictionData = []

        logisticRegression = LogisticRegressionModel()
        decisionTree = DecisionTreeModel()
        randomForest = RandomForestModel()
        svm = SVMModel()
        naiveBayes = NaiveBayesModel()

        # logistic regression
        logisticRegression.train_model('ml.xlsx')
        predictions = logisticRegression.predict(data)
        predictionData.append(predictions)


        # decision tree
        print('checking decision tree...')
        decisionTree.train_model('ml.xlsx')
        predictions = decisionTree.predict(data)
        predictionData.append(predictions)

         # random forest
        print('checking random forest...')
        randomForest.train_model('ml.xlsx')
        predictions = randomForest.predict(data)
        predictionData.append(predictions,)

         # SVM
        print('checking SVM')
        svm.train_model('ml.xlsx')
        predictions = svm.predict(data)
        predictionData.append(predictions)

         # Naive bayes
        print('Checking Naive bayes...')
        naiveBayes.train_model('ml.xlsx')
        predictions = naiveBayes.predict(data)
        predictionData.append(predictions)


        print(f"PREDICTIONS IN ML_PREDICTION: {predictionData}")

        def calculate_outcome(lst):
            h_count = lst.count('H')
            a_count = lst.count('A')
            d_count = lst.count('D')
            total_count = len(lst)

            h_percentage = (h_count / total_count) * 100
            a_percentage = (a_count / total_count) * 100
            d_percentage = (d_count / total_count) * 100

            max_count = max(h_count, a_count, d_count)
            percentages = {'H': h_percentage, 'A': a_percentage, 'D': d_percentage}
            non_zero_percentages = {key: value for key, value in percentages.items() if value != 0}

            # if h_count == a_count == d_count:
            #     return 'Stalemate', 33.33, {'H': h_percentage, 'A': a_percentage, 'D': d_percentage}
            #
            # elif h_count == max_count:
            #     if a_count == max_count:
            #         if d_count == max_count:
            #             return 'H/A/D', h_percentage, percentages
            #         else:
            #             return 'H/A', h_percentage, percentages
            #     elif d_count == max_count:
            #         return 'H/D', h_percentage, percentages
            #     else:
            #         return 'H', h_percentage, percentages
            #
            # elif a_count == max_count:
            #     if d_count == max_count:
            #         return 'A/D', a_percentage, percentages
            #     else:
            #         return 'A', a_percentage, percentages
            #
            # elif d_count == max_count:
            #     return 'D', d_percentage, percentages

            result = '/'.join(non_zero_percentages.keys())
            percentages_str = '/'.join([f"{key}: {value}%" for key, value in non_zero_percentages.items()])
            return f"{result} ({percentages_str})"

        outcome = calculate_outcome(predictionData)
        return outcome


    except Exception as e:
        print(f"[ERROR][ml_prediction] {e}")


# ==============================================================================================================
# EXTRACT
# 000000000000000

def element_exists(driver, selector_name, selector='class'):
    if selector == 'class':
        try:
            input_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, selector_name))
            )
            return True
        except:
            return False


def extract_team_info(url):
    # variable declarations
    no_bet_class = "m-sport-bet-no-data"
    match_league = "match-league"
    league_title = "league-title"
    match_table_class = "m-table.match-table"
    match_content_row_class = "m-table-row.m-content-row.match-row"
    game_time_class = "clock-time"
    home_team_class = "home-team"
    away_team_class = "away-team"
    odd_market_class = "m-market.market" # 2 available pick the first one
    outcome_odds_class = "m-outcome-odds"
    no_bet = None

    all_leagues_data = []

    '''
    MATCH LEAGUE (Multiple)
        - league title
        - MATCH TABLE
            - MATCH CONTENT ROW (MULTIPLE)
                * game time
                * home team
                * away team
                * odd market (2 available pick the first one)
                    ** outcome odds: ( 3 available first is home, second is draw and third is for away
    '''

    try:
        # initialize driver
        driver = initialize_browser()
        # load url
        load_url(driver, url)
        # check if team data is available on page
        no_bet = element_exists(driver, no_bet_class)
        if no_bet is True:
            raise Exception

        # get list of all leagues available
        leagues = driver.find_elements(By.CLASS_NAME, match_league)
        print(f'total leagues: {len(leagues)}')

        if len(leagues) == 0:
            raise Exception

        # Loop through the leagues
        # -----------------------------
        for index, league in enumerate(leagues):
            league_details = {}
            # GET THE LEAGUE TITLE
            # ---------------------
            title = get_league_title(league, league_title)
            league_details['title'] = clean_text(title).strip()

            # GET MATCH TABLE
            # -----------------
            matchTableData = get_match_table(league, match_table_class)

            # GET THE NUMBER OF ROWS IN THE MATCH TABLE
            #------------------------------------------
            tableRows = get_table_rows(matchTableData, match_content_row_class)

            # LOOP THROUGH THE ROWS IN THE TABLE TO EXTRACT DATA
            # ---------------------------------------------------
            # print(f"{index}/{len(leagues)} looping through roes to get data for {title}")
            gameDetails =[]
            for row in tableRows:
                try:
                    single_game_detail = {}

                    gameTime = row.find_element(By.CLASS_NAME, game_time_class).text
                    single_game_detail['game_time'] = gameTime

                    homeTeam = row.find_element(By.CLASS_NAME, home_team_class).text
                    single_game_detail['home_team'] = homeTeam

                    awayTeam = row.find_element(By.CLASS_NAME, away_team_class).text
                    single_game_detail['away_team'] = awayTeam

                    oddMarkets = row.find_element(By.CLASS_NAME, odd_market_class) # trying to select the first one only
                    outcomeOdds = oddMarkets.find_elements(By.CLASS_NAME, outcome_odds_class)

                    homeWinOdd = outcomeOdds[0].text
                    single_game_detail['home_odd'] = homeWinOdd

                    drawOdd = outcomeOdds[1].text
                    single_game_detail['draw_odd'] = drawOdd

                    awayWinOdd = outcomeOdds[2].text
                    single_game_detail['away_odd'] = awayWinOdd

                    gameDetails.append(single_game_detail)
                except Exception as e:
                    print(f"Error in row loop: {e}")
                    continue

            league_details['data'] = gameDetails

            all_leagues_data.append(league_details)
            # print(f"{index}/{len(leagues)} >. data added for {title}")

        # print(f"total all league data = {len(all_leagues_data)}")
        return all_leagues_data
    except Exception as e:
        if no_bet is True:
            print("Bet is not available for current period. change the period or try again latter!")

        if len(leagues) == 0:
            print("No league found")
        pass


def clean_text(text):
    # Remove non-character elements using regular expression
    clean = re.sub(r'[^\w\s]', '', text)
    return clean


def get_league_title(driver, class_name):
    title = driver.find_element(By.CLASS_NAME, class_name)
    return title.text


def get_match_table(driver, class_name):
    table = driver.find_element(By.CLASS_NAME, class_name)
    return table


def get_table_rows(driver, class_name):
    rows = driver.find_elements(By.CLASS_NAME, class_name)
    return rows


def reset_file(filename):
    with open(filename, 'w') as f:
        f.write("")


def write_append_to_file(filename, data):
    with open(filename, 'a') as f:
        f.write(data)

def get_all_odds_data():
    oddData = []
    with open('teamOnlyData.txt', 'r') as f:
        data = f.read()

    with open('oddOnlyData.txt', 'r') as f:
        data2 = f.read()

    dataList = data.split("\n\n")
    dataList2 = data2.split("\n\n")

    for index, d in enumerate(dataList):
        nd = d.split("\n")
        nd2 = dataList2[index].split("\n")

        result = f"{' | '.join(nd)} | {' | '.join(nd2)}"
        oddData.append(result)

    return oddData

def get_home_away_odds(home, away):
    '''

    :param home:
    :param away:
    :return: homeOdd, AwayOdd, LoweestOdd
    '''

    allOdds = get_all_odds_data()
    final_home_odd = None
    final_away_odd = None
    lowest = None

    for odd in allOdds:
        try:

            test_home = odd.split("|")[0].strip()
            test_away = odd.split("|")[1].strip()
            home_odd = odd.split("|")[2].strip()
            away_odd = odd.split("|")[3].strip()

            # print(f">> checking {home} VS {test_home}")

            if test_home.lower().strip() == str(home).lower().strip():
                # print("\t Found!!!!!!!!!!")
                final_home_odd = home_odd
                final_away_odd = away_odd

                if float(final_home_odd) < float(final_away_odd):
                    lowest = "Home"
                else:
                    lowest = "Away"

                return final_home_odd, final_away_odd, lowest
        except:
            continue

def deep_check(odd_info, suggestion):
    homeOdd = round(float(odd_info[0]),2)
    awayOdd = round(float(odd_info[1]), 2)

    oddDiff = round(abs(homeOdd - awayOdd), 2)
    lowestOdd = odd_info[2]

    # {'Home/Draw' : [1.43 -  5.5] |'LO/Draw':  [0.5 - 0.65] |'Home/Away':  [0.1 -0.25]} WR: (67%)
    # print(f"SUGGESTION HERE: {suggestion}")
    mainData, wr = suggestion.split('WR:')

    # print(f"maindata b4: {mainData} --- {type(mainData)}")

    mainData = eval(str(mainData).replace("|", ",").replace("-", ","))

    # print(f"maindata after: {mainData} - {type(mainData)}")

    finalPlay = None

    # print(f"Deep check Begins............................>>>>>>>>")
    # print()

    for data in mainData:
        tempPlay = data

        option = eval(str(mainData[tempPlay]))
        if len(option) == 0:
            finalPlay = tempPlay
            # print(1)
            continue
        elif len(option) == 1:
            if oddDiff == round(float(option[0]), 2):
                finalPlay = tempPlay
                # print(2)
                continue
        elif len(option) == 2:
            lowerBand = round(float(option[0]), 2)
            upperBand = round(float(option[1]), 2)

            if lowerBand <= oddDiff <= upperBand:
                # print(f"Exact range found! ")
                finalPlay = tempPlay
                # print(3)
                break

    if "LO" in str(finalPlay):
        print(f"Lowest odd found................................")
        finalPlay = str(finalPlay).replace("LO", lowestOdd)
        finalPlay =f"{finalPlay} [H/A: {homeOdd}/{awayOdd}]"

    if finalPlay == f"{lowestOdd}/Draw":
        return f"[SWAPPED] Home/Away | [{oddDiff}]"
    else:
        return f"{finalPlay} | [{oddDiff}] "

    pass



# ==============================================================================================================
# MAINS
# ==============================================================================================================

action = input("[A] Add pattern | [P] Predict: ")

if action.lower() == 'p' or action == '':

    with open('teamOnlyData.txt', 'r') as f:
        raw = f.read()

    teamList = []
    rawsplit = raw.strip().split("\n\n")
    # print(rawsplit)
    for split in rawsplit:
        h = split.split("|")[0]
        a = split.split("|")[1]
        #  h = split.split("\n")[0]
        # a = split.split("\n")[1]
        #

        value = (h, a)
        teamList.append(value)

    for team in teamList:
        home = team[0]
        away = team[1]
        predict(home, away)
        print("------>>>>>>> NEXT")
        print()
        time.sleep(2)

    print("DONE!DONE!DONE!DONE!")

elif action.lower() == 'a':
    analyzer = CombinationAnalyzer()
    error = False

    compbinedData = """Strong Home,Strong Home,Strong Home,{'Home/Draw' : [0.45]} WR: (0%)
Strong Home,Strong Home,Strong Away,{'Home/Draw' : [1.42] } WR: (0%)
Strong Home,Strong Home,Strong Draw,{'Home/Draw' : ['LO'] | 'Home/Away': ['LO']} WR: (0%)
Strong Home,Strong Home,Weak Away,{'Home/Away': []} WR: (0%)
Strong Home,Strong Home,Weak Home,{'Home/Away' :  [2.54 - 4.67]} WR: (0%)
Strong Home,Strong Away,Strong Draw,{'Draw/Away' : [] | 'Home/Draw': [] }  WR: (0%)
Strong Home,Strong Away,Weak Away,{'Home/Away': []} WR: (0%)
Strong Home,Strong Away,Weak Home,{'Draw' : []} WR: (0%)
Strong Home,Weak Away,Strong Away,{'Home/Away' : []} WR: (0%)
Strong Home,Weak Home,Weak Away,{'Home/Away': [] | {'LO/Draw':  [0.9] } WR: (0%)
Strong Home,Weak Home,Weak Home,{'Home/Draw' : [] } WR: (0%)
Strong Away,Strong Home,Strong Home,{'Home/Away' : []} WR: (0%)
Strong Away,Strong Home,Strong Away,{'Home/Away' : []} WR: (0%)
Strong Away,Strong Away,Strong Home,{'Away/Draw' : [] } WR: (0%)
Strong Away,Strong Away,Strong Away,{'Home/Away' : [2.46]} WR: (0%)
Strong Away,Strong Away,Weak Away,{'Away/Draw' : [] | 'Home/Away':  [1.5 - 2.1]} WR: (0%)
Strong Away,Strong Draw,Strong Home,{'LO/Draw'  : [1.28] } WR: (0%)
Strong Away,Strong Draw,Strong Away,{'Draw/Away' : [] | 'LO/Draw' :  [4.8]} WR: (0%)
Strong Away,Strong Draw,Weak Away,{'Away/Draw' : []} WR: (0%)
Strong Away,Weak Away,Strong Away,{'Home/Away' :  [ 4.67]} WR: (0%)
Strong Away,Weak Away,Weak Away,{'Home/Away' : [0.7]} WR: (0%)
Strong Away,Weak Home,Strong Home,{'Home/Away' : []} WR: (0%)
Strong Away,Weak Home,Strong Away,{'Home/Away'  :  [0.9]} WR: (0%)
Strong Away,Weak Home,Weak Away,{'Home/Away' : [] | 'Away/Draw':  [ 0.5]} WR: (0%)
Strong Draw,Strong Home,Strong Home,{'Home/Draw' : [2.43 - 5.26] | 'LO/Draw' : [] | 'Home/Away' :  [0.25]} WR: (0%)
Strong Draw,Strong Home,Strong Away,{'Home/Away'  :  [2.89 - 4.39]  | 'LO/Draw' : [ 0.05 - 1.55]} WR: (100%)
Strong Draw,Strong Home,Strong Draw,{'Home/Draw'  : [1.5 - 3.2] | 'Home/Away' :  [0.15]} WR: (0%)
Strong Draw,Strong Home,Weak Away,{'Home/Draw' :  [1.1 - 1.87]} WR: (0%)
Strong Draw,Strong Home,Weak Home,{'Home/Draw' : [3.86] | 'Away/Draw' : [5.51] | 'Home/Away' : [0.3 - 1.3]} WR: (100%)
Strong Draw,Strong Away,Strong Home,{'Home/Away' : [1 - 6.3] | 'LO/Draw' :  [0.2]} WR: (0%)
Strong Draw,Strong Away,Strong Away,{'Draw/Away' : [] | 'Home/Away':  [6.6 - 9.26] } WR: (0%)
Strong Draw,Strong Away,Strong Draw,{'Draw/Away'  : [2.1 - 2.8]} WR: (0%)
Strong Draw,Strong Away,Weak Away,{'Draw/Away' :   [0.15 - 2.15]  |  'Home/Away' :  [4.17]} WR: (100%)
Strong Draw,Strong Away,Weak Home,{'Draw/Away'  :  [1 - 2.21] | 'Home/Away' :  [2.89]} WR: (0%)
Strong Draw,Strong Draw,Strong Home,{'Home/Draw' : [1.43 -  5.5] |'LO/Draw':  [0.5 - 0.65] |'Home/Away':  [0.1 -0.25]} WR: (67%)
Strong Draw,Strong Draw,Strong Away,{'Draw/Away' : [0.55 - 0.9] | 'LO/Draw':  [0.95 - 15.9 ] | 'Home/Away' : [0.35]} WR: (100%)
Strong Draw,Strong Draw,Strong Draw,{'Home/Draw' :  [ 0.9 - 5.45]} WR: (0%)
Strong Draw,Strong Draw,Weak Away,{'Draw/Away' : [0.15 - 1.51] | 'LO/Draw' : [] | 'Home/Away':   [2.16 -  4.7]} WR: (75%)
Strong Draw,Strong Draw,Weak Home,{'Home/Draw' :  [0.35  - 6.17 ] | 'LO/Draw' : [] | 'Home/Away' : [0.1] } WR: (50%)
Strong Draw,Weak Away,Strong Home,{'Home/Draw' :  [0.45]} WR: (0%)
Strong Draw,Weak Away,Strong Draw,{' Away/Draw' : [0.85]} WR: (0%)
Strong Draw,Weak Away,Weak Away,{'Draw/Away' : [5.1]} WR: (0%)
Strong Draw,Weak Away,Weak Home,{'Home/Draw' : [4.94]} WR: (0%)
Strong Draw,Weak Home,Weak Away,{'Home/Draw' : [0.4]} WR: (0%)
Weak Away,Strong Home,Strong Home,{'Home/Away' : []} WR: (0%)
Weak Away,Strong Home,Weak Away,{'Home/Away' : []} WR: (0%)
Weak Away,Strong Away,Strong Away,{'Home/Away' : []} WR: (0%)
Weak Away,Strong Away,Weak Home,{'Draw' : []} WR: (0%)
Weak Away,Weak Away,Strong Away,{'Home/Away' : []} WR: (0%)
Weak Away,Weak Home,Strong Away,{'Home/Away' : [] } WR: (0%)
Weak Away,Weak Home,Strong Draw,{'Home/Draw' : []  | 'Away/Draw' : ['away LO odd']} WR: (0%)
Weak Home,Strong Home,Strong Home,{'Home/Draw' : []} WR: (0%)
Weak Home,Strong Home,Weak Home,{'Home/Away' : [] | 'Home/Draw' :  [0.6 - 1.4] } WR: (0%)
Weak Home,Strong Away,Strong Away,{'Home/Away' : [] } WR: (0%)
Weak Home,Strong Away,Strong Draw,{'Home/Away' : [0.9]} WR: (0%)
Weak Home,Strong Away,Weak Away,{'Home/Away' : []} WR: (0%)
Weak Home,Strong Draw,Strong Away,{'Draw/Away' : [] | 'Home/Away' : ['LO for Home']} WR: (0%)
Weak Home,Weak Away,Weak Home,{'Home/Away' : []} WR: (0%)
Weak Home,Weak Home,Strong Draw,{'Home/Draw' : [] } WR: (0%)
    """
    combinedDataList = compbinedData.split("\n")


    # while True:
    for data in combinedDataList:
        time.sleep(0.2)
        if error is False:
            os.system('cls')
        # combinations = input("Add combinations [a,b,c,result]: ")
        combinations = data
        if combinations == "":
            break
        else:
            if combinations.count(",") != 3:
                print("Wrong Expected Input! Try again")
                error= True
            else:
                a, b, c, result = combinations.split(",")
                analyzer.add_combination(a, b, c, result)
                error = False

        print(f"Done for {data}")
    # input("Wait here...................")

elif action.lower() == 'e':
    # Extract data from sporty
    reset_file(teamData)
    reset_file("oddOnlyData.txt")
    reset_file("teamOnlyData.txt")

    period = 3
    ans = input("Period? default=3: ")
    if ans != "":
        period = int(ans)

    url = f"https://www.sportybet.com/ng/sport/football?time={period}"

    leagueInfo = extract_team_info(url)

    for league in leagueInfo:
        # print(f"League: {league['title']}")
        # print(f"Data: {league['data']}")
        # print("=============================================================")
        # print()
        result = f"League: {league['title']}"
        odd_only = ""
        team_only= ""

        for data_item in  league['data']:
            # excluding simulated reality games
            if data_item['home_team'].lower().__contains__('srl'):
                continue

            result2 = f"""{data_item['game_time']}
{data_item['home_team']}
{data_item['away_team']}
{data_item['home_odd']}
{data_item['away_odd']}
"""
            result_odd = f"""{data_item['home_odd']} | {data_item['away_odd']}

"""

            result_team = f"""{data_item['home_team']} | {data_item['away_team']}

"""

            result += f"\n{result2}"
            odd_only += f"{result_odd}"
            team_only += f"{result_team}"

        result += f"\n***************************************************************************\n"


        print(result)
        write_append_to_file(teamData, result)
        write_append_to_file("oddOnlyData.txt", odd_only)
        write_append_to_file("teamOnlyData.txt", team_only)

    # input('waiting...')
    print("Done! Done! Ok!")






