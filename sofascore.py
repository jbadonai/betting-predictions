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

timeout = 15

def initialize_browser():
    # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
    return webdriver.Chrome()


def load_url(driver, url):
    global timeout
    # Navigate to the webpage
    # driver.get(url)
    driver.set_page_load_timeout(timeout)

    try:
        # Attempt to navigate to the URL within the specified timeout period
        driver.get(url)
        return  True
    except TimeoutException:
        # Handle the timeout exception here (e.g., print an error message)
        print("Page load timed out")
        return True
        pass
    except Exception as e:
        print(f"Error! Retrying[timeout ={timeout}] [url: {url}]...")
        timeout += 5
        return FileNotFoundError
        # time.sleep(5)
        # load_url(driver, url)


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
    # Example usage:
    url = "https://www.sofascore.com/"
    text_to_search = team_member

    # 1. Initialize the browser
    print("initializing driver...")
    driver = initialize_browser()

    # 2. Load the URL
    print("loading url...")
    while True:
        ans = load_url(driver, url)
        if ans is True:
            break
        else:
            time.sleep(2)



    # 3. Search for text
    print(f"Searching for {text_to_search}")
    search_text(driver, text_to_search)
    time.sleep(1)

    # 4. load the first url
    print(f"getting page url for {text_to_search}")
    href = get_first_href(driver)

    print(f"loading page for {text_to_search}...")
    while True:
        try:
            # driver.get(href)
            load_url(driver, href)
            break
        except:
            print("Error loading page! Retrying...")
            driver.refresh()
            time.sleep(2)
    time.sleep(1)

    # 5. select a display option
    # print("selecting option...")
    # select_option(driver, "full")

    teamList = get_all_team(driver)

    return driver, teamList


# =============================================================================


def get_data_for_prediction(home, no_team = False):
    all_data = []
    team_list = []
    # set one of the team name in a league required to get the league and all teams in the league
    league_member = home
    driver, team_list_temp = get_team_list_for(league_member)
    if no_team is False:
        team_list.extend(team_list_temp)
        team_list.append(league_member)
    else:
        team_list.append(league_member)

    for index, team in enumerate(team_list):
        # 3. Search for text
        while True:
            try:
                print(f"\r[{index + 1}/{len(team_list)}] Extracting Data for {team}", end="")
                # ---------> REMOVED FOR TESTING PURPOSE TO AVOID DUPLICATE LOADING <---------------
                # search_text(driver, team)
                # time.sleep(1)

                # 4. load the first url
                # print(f"getting page url for {team}")

                # href = get_first_href(driver)

                # print(f"loading page for {team}...")
                # driver.get(href)
                # time.sleep(1)
                # <----------------- UP TO HERE ---------------------------------------->

                time.sleep(3)
                # print("Extracting Football data:")
                game_data = extract_football_data(driver, team)
                # print(game_data)
                all_data.extend(game_data)
                print(f'\t |\t saving data for {team}...')
                # print(" | ", eval(game_data[0])['team'], " | ")
                # print('--------------------------------------')

                save_to_excel(game_data)
                return eval(game_data[0])['team']
                # if ans is True:
                #     print("Saved successfully")
                #     break
                # else:
                #     print("Not saved! Data exists")
                #     break
                # time.sleep(1)
                # break
            except Exception as e:
                print(e)
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

    h, ch = check_team_existence(home)  # h-home, ch-count home
    a, ca = check_team_existence(away)  # a-away, ca-count away
    # print(f"home: {home}::{h}")
    # print(f"away: {away}::{a}")

    time.sleep(1)

    # if bool(h) is False or bool(a) is False:
    #     print(f"No data for teams! Getting data online")
    #     if bool(h) is False:
    #         get_data_for_prediction(home, True)
    #     else:
    #         get_data_for_prediction(away, True)
    new_home = home
    new_away = away

    if bool(h) is False:
        new_home = get_data_for_prediction(home, True)

    if bool(a) is False:
        new_away = get_data_for_prediction(away, True)

    # print(f"{home} ==> {new_home}")
    # print(f"{away} ==> {new_away}")

    newdata = retrieve_data()
    predict_engine = FootballPrediction()

    # prediction = predict_engine.analyze_matches(newdata, home, away)
    # prediction = predict_engine.analyze_matches(newdata, new_home, new_away)
    # print(prediction)
    time.sleep(1)

    a = predict_engine.analyze_matches(newdata, new_home, new_away)
    b = predict_engine.analyze_by_average_goal_scored(newdata, new_home, new_away)
    c = predict_engine.analyze_by_poisson_analysis(newdata, new_home, new_away)

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

    print(a, "-", evaluate(a))
    print(b, "-", evaluate(b))
    print(c, "-", evaluate(c))
    print()
    print(f"H:A:D: {h_count}:{a_count}:{d_count}")
    print(f"PLAY: {suggestion}")

    result = f"""
{a} - {evaluate(a)}
{b} - {evaluate(b)}
{c} - {evaluate(c)}
H:A:D: {h_count}:{a_count}:{d_count}
{evaluate(a)},{evaluate(b)},{evaluate(c)}

PLAY: {suggestion}
===========================================================================================================
===========================================================================================================
    """

    with open("result.txt", 'a', encoding='utf-8') as f:
        f.write(result)


action = input("[A] Add pattern | [P] Predict: ")

if action.lower() == 'p' or action == '':

    raw = '''Melbourne Knights
Hume City

St Albans Saints
Manningham United Blues

Green Gully Cavaliers
Dandenong Thunder

Oakleigh Cannons
South Melbourne FC
        '''

    teamList = []
    rawsplit = raw.split("\n\n")
    # print(rawsplit)
    for split in rawsplit:
        h = split.split("\n")[0]
        a = split.split("\n")[1]
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

else:
    analyzer = CombinationAnalyzer()
    error = False
    while True:
        if error is False:
            os.system('cls')
        combinations = input("Add combinations [a,b,c,result]: ")
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






