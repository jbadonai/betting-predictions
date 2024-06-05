'''
sofascore.py (entry) | data_extractor.py ==>
    * GET ALL GAMES ON SPECIFIED DATE FROM SPORTYBET.COM
    * EXTRACT PREVIOUS GAME DATA FOR EACH TEAM IN VIEW FROM SOFASCORE.COM
    * PREDICICT OUTCOME [HOME/DRAW | AWAY/DRAW | HOME/AWAY]

fb_result.txt
    * FOOTBALL RESULT AFTER PREDICTION

bb_result.txt
    * BASKETBALL RESULT AFTER PREDICTION

ml_fb.xlsx | ml_bb.xlsx
    * CONTAINS DATA USED BY MACHINE LEARNING ALGORITHM TO PREDICT OUTCOME
    * PREVIOUS GAME RESULT ARE UPDATED FOR BETTER ACCURACY

updateDataWithCurrentResult.py
    * CHECK THE ACTUAL RESULT FROM SPORTYBET.COM ON THE LAST PREDICTED GAME
    * UPDATE 'ml_fb.xlsx' AND 'ml_bb.xlsx'

filter.py
    * SORTS 'fb_result.txt' BASED ON THE CODE
    * SAVE RESULT IN 'filtered' DIRECTORY BASED ON DATE SPECIFIED
'''


"""
PROCEDURE
************
1. IF THERE IS AN EXISTING GAME PLAYED.
    > RUN 'updateDataWithCurrentResult.
    
2. > RUN 'sofascore.py'

3. > RUN 'filter.py'

4. > RUN 'book_game.py'

"""


try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    import time
    from bs4 import BeautifulSoup
    from predict import *
    import os
    import pandas as pd
    import ast  # To evaluate the string representation of the dictionary
    import re
    from difflib import SequenceMatcher
    from selenium.common.exceptions import TimeoutException
    from datetime import datetime

    from pattern import CombinationAnalyzer
    from data_extractor import PreviousRecordExtractor
    from data_analysis_prediction import *

    import predictionBot as bot
    import threading

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.naive_bayes import GaussianNB
    from sklearn.metrics import accuracy_score
    import joblib


    # timeout = 15
    teamData = 'teamList.txt'
    algorighm_list = ['LOGISTIC REGRESSION', 'DECISION TREE', 'RANDOM FOREST', 'SVM', 'NAIVE BAYES']
    use_old_model = False

    def run_function(functionName, join: bool = False, *args):
        try:
            t = threading.Thread(target=functionName, args=args)
            t.daemon = True
            t.start()
            if join:
                t.join()
        except Exception as e:
            print(f"An Error Occurred in [generalFunctions.py] > run_function(): {e}")

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
        # print(f"h: {h} --  a: {a}")

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

    def retrieve_data_bb(file_path='datafile_bb.xlsx'):
        try:
            # Load data from Excel file
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                print("Error loading data:", str(e))
                return []

             # Drop rows with any NaN values
            df = df.dropna()

            # Remove rows with blank or "?" values in any column
            df = df[~df.isin(["", "?"])]

            # Convert specified columns to integers
            int_columns = ['home_Q1_score', 'home_Q2_score', 'home_Q3_score', 'home_Q4_score',
                           'home_Q5_score', 'away_Q1_score', 'away_Q2_score', 'away_Q3_score',
                           'away_Q4_score', 'away_Q5_score', 'home_score', 'away_score']
            for col in int_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

            # # Return the cleaned DataFrame
            # return df


            # Return the cleaned DataFrame as a list of dictionaries
            cleaned_data = df.to_dict(orient='records')
            return cleaned_data

        except FileNotFoundError:
            # Return an empty list if the file doesn't exist
            return []

    def check_team_existence(team_name, sport='football'):
        try:
            if sport == 'football':
                file_path='datafile.xlsx'
            elif sport == 'basketball':
                file_path = 'datafile_bb.xlsx'

            # Try loading existing file
            df = pd.read_excel(file_path)
            try:
                team_count = df['team'].eq(team_name).sum()
            except:
                return False, 0

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

    def predict(game_time, home, away, driver, sport="football"):
        try:
            print("PREDICTING...")

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

            def evaluate(text):
                ans = None
                awaycount = str(text).count("Away")
                homecount = str(text).count("Home")
                drawcount = str(text).count("Draw")

                if awaycount == 2:
                    return "Strong Away"
                elif homecount == 2:
                    return "Strong Home"
                elif homecount == 1 and drawcount == 1:
                    return "Weak Home"
                elif awaycount == 1 and drawcount == 1:
                    return "Weak Away"
                elif drawcount == 2:
                    return "Strong Draw"

            def evaluate_scores(text):
                homescore = str(text).split(":")[0].strip().split(" ")[-1]
                awayscore = str(text).split(":")[-1].strip().split(" ")[0]
                return homescore, awayscore
                pass

            def complete_evaluation(a, b, c):
                new_a = a.lower().replace(" ", '_')
                new_b = b.lower().replace(" ", '_')
                new_c = c.lower().replace(" ", '_')

                # strong_home	strong_away	strong_draw	weak_home	weak_away
                eval_data = {'strong_home': 0,
                             'strong_away': 0,
                             'strong_draw': 0,
                             'weak_home': 0,
                             'weak_away': 0
                             }

                eval_data[new_a] = 1
                eval_data[new_b] = 1
                eval_data[new_c] = 1

                return eval_data

                pass

            def check_evaluation(test, all_evaluation):
                if str(all_evaluation).strip().lower().__contains__(str(test).lower().strip()):
                    return 1
                else:
                    return 0

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

            def combine_lists(list1, list2):
                # Convert lists to sets to remove duplicates
                set1 = set(list1)
                set2 = set(list2)

                # Combine the sets
                combined_set = set1.union(set2)

                # Convert the combined set back to a list
                combined_list = list(combined_set)

                return combined_list

            def process_final(fin: list):
                ans = "/".join(fin)
                if ans.lower().__contains__("a") and ans.lower().__contains__("h"):
                    return "Home or Away [ 12 ] "
                elif ans.lower().__contains__("d") and ans.lower().__contains__("h"):
                    return "Home or Draw [ 1X ] "
                elif ans.lower().__contains__("d") and ans.lower().__contains__("a"):
                    return "Draw or Away [ X2 ] "
                elif ans.lower() == 'a':
                    return "Away"
                elif ans.lower() == 'h':
                    return "Home"
                elif ans.lower() == 'd':
                    return "Draw"

            def combine_lists(list1, list2):
                # Convert lists to sets to remove duplicates
                set1 = set(list1)
                set2 = set(list2)

                # Combine the sets
                combined_set = set1.union(set2)

                # Convert the combined set back to a list
                combined_list = list(combined_set)

                return combined_list

            def process_final(fin: list):
                ans = "/".join(fin)
                if ans.lower().__contains__("a") and ans.lower().__contains__("h"):
                    return "Home or Away [ 12 ] "
                elif ans.lower().__contains__("d") and ans.lower().__contains__("h"):
                    return "Home or Draw [ 1X ] "
                elif ans.lower().__contains__("d") and ans.lower().__contains__("a"):
                    return "Draw or Away [ X2 ] "
                elif ans.lower() == 'a':
                    return "Away"
                elif ans.lower() == 'h':
                    return "Home"
                elif ans.lower() == 'd':
                    return "Draw"

            #  CHECKING IF HOME AND AWAY TEAM ALREADY EXIST IN THE EXCEL SSHEET
            # -----------------------------------------------------------------------------
            print(f'[DEBUG] Checking teams: "{home}" and "{away}" recent matches locally...')
            h, ch = check_team_existence(home, sport)  # h-home, ch-count home
            a, ca = check_team_existence(away, sport)  # a-away, ca-count away

            time.sleep(1)

            # INITIALIZE NEW HOME AND NEW AWAY WITH THE PASSED IN VALUES
            # -----------------------------------------------------------------------------
            new_home = home
            new_away = away
            # print(f"name before: {new_home}<>{new_away}")

            teamsWithMissingData = []


            # IF HOME OR AWAY IS NOT IN THE DATA BASE, EXTRACT THEIR DATA AND SAVE IN DATABASE
            # -----------------------------------------------------------------------------
            if bool(h) is False:
                # new_home = get_data_for_prediction(home, True)
                print(f'[DEBUG] "{home}" not in local database! adding it to checklist...')
                teamsWithMissingData.append(home)

            if bool(a) is False:
                # new_away = get_data_for_prediction(away, True)
                print(f'[DEBUG] "{away}" not in local database! adding it to checklist...')
                teamsWithMissingData.append(away)

            # print(f"h: {bool(h)} : a: {bool(a)}")

            #  GET DATA FROM SOFASCORE FOR TEAM WITH NO DATA IN THE EXCEL FILE
            # ---------------------------------------------------------------
            if bool(h) is False or bool(a) is False:
                print(f'[DEBUG] Intializing recent game data extraction...')
                dataExtractor = PreviousRecordExtractor(driver=driver, sport=sport)
                newTeamName = dataExtractor.start_data_extraction(teamsWithMissingData)

                if newTeamName is None:
                    return None

                if len(newTeamName) == 2:
                    new_home = newTeamName[0]
                    new_away = newTeamName[1]
                elif len(newTeamName) == 1:
                    if bool(h) is False:
                        new_home = newTeamName[0]
                    elif bool(a) is False:
                        new_away = newTeamName[0]

            # print(f"names after: {new_home}<>{new_away}")
            # =================================================
            # PREDICTION ACTUALLY STARTS HERE
            # =================================================



            # LOAD DATA FROM THE DATABASE (I.E THE EXCEL SHEET)
            # -----------------------------------------------------------------------------
            print(f'[DEBUG] Recent game data confirmed! Prediction begins...')
            if sport == 'football':
                print(f'[DEBUG] Retrieving recent football data from file for processing...')
                newdata = retrieve_data()
            elif sport == 'basketball':
                print(f'[DEBUG] Retrieving recent basketball data from file for processing...')
                newdata = retrieve_data_bb()

            # print(newdata)
            # for data in newdata:
            #     print(data)
            #
            # input('ms')


            # CREATE AN INSTANCE OF THE PREDICTING ENGINE
            # -----------------------------------------------------------------------------
            # predict_engine = FootballPrediction()
            def football_prediction_old():
                try:
                    predict_engine = FootballPrediction()

                    print(f'[DEBUG] [PREDICTING] Using WINS ratio and H2H data...')
                    a = predict_engine.analyze_matches(newdata, new_home, new_away)

                    print(f'[DEBUG] [PREDICTING] Using AVERAGE GOALS and EXPECTED GOAL analysis...')
                    b = predict_engine.analyze_by_average_goal_scored(newdata, new_home, new_away)

                    print(f'[DEBUG] [PREDICTING] Using POISSON analysis...')
                    c = predict_engine.analyze_by_poisson_analysis(newdata, new_home, new_away)

                    print(f'[DEBUG] [PREDICTING] Evaluating results from the 3 alorighms...')

                    analyzer = CombinationAnalyzer()

                    homeScore = round(
                        (float(evaluate_scores(a)[0]) + float(evaluate_scores(b)[0]) + float(
                            evaluate_scores(c)[0])) / 3)
                    awayScore = round(
                        (float(evaluate_scores(a)[1]) + float(evaluate_scores(b)[1]) + float(
                            evaluate_scores(c)[1])) / 3)

                    comp_eval = complete_evaluation(evaluate(a), evaluate(b), evaluate(c))
                    print(f'complete evaluation: {comp_eval}')

                    print(
                        f'[DEBUG] [PREDICTING] Evaluation completed! Concluding/Predicting based on the evaluation...')
                    # get suggestion based on previous result given by the prediction stored
                    suggestion = analyzer.analyze(evaluate(a), evaluate(b), evaluate(c))
                    print(f'suggestion: {suggestion}')

                    # get the home and away odds
                    odds = get_home_away_odds(home, away)
                    print(f"odds: {odds}")

                    if odds is None:
                        return

                    # using the odds and suggestion to make a deeper infomed decision or predition
                    deepCheck = deep_check(odds, suggestion)

                    # declaring machine learning container that holds data to be passed to machine learning
                    print(f'[DEBUG] [PREDICTING LEVEL 2] Preparing data for MACHINE LEARNING algorighms...')
                    ml = {}

                    allEvaluation = f"{evaluate(a)},{evaluate(b)},{evaluate(c)}"

                    # THE SCRIPT USES 2 DIFFERENT MACHINE LEARNING ALGORIGHMS THEIR DATA WILL BE PREPARED BELOW
                    # populate data for the machine learning V1
                    # ------------------------------------
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

                    #  populate data for machine learning version 2
                    # -------------------------------------------------
                    data4Ml2 = {'home_odd': ml['home_odd'],
                                'away_odd': ml['away_odd'],
                                'odd_difference': ml['odd_difference'],
                                'strong_home': ml['strong_home'],
                                'strong_away': ml['strong_away'],
                                'strong_draw': ml['strong_draw'],
                                'weak_home': ml['weak_home'],
                                'weak_away': ml['weak_away']}

                    # predict using machine learning based on supplied data ml
                    print("[Debug][ML] ML prediction V1 starting...")

                    print(
                        f'[DEBUG] [PREDICTING LEVEL 2] spliting input data into 2 for V1 and V2 Machine learning algorithms...')
                    # create a copy of ml data so it can be modified for ml
                    mlData = ml.copy()
                    mlData.pop('home')
                    mlData.pop('away')

                    print(f'[DEBUG] [PREDICTING LEVEL 2] parsing data to V1 MACHINE LEARNING algorith...')
                    mlPrediction = ml_prediction(mlData)
                    required = mlPrediction.split("(")[-1].replace(")", "").replace("%", "")
                    required_split = required.split("/")
                    required_dict = {}
                    for r in required_split:
                        d = r.split(":")
                        required_dict[d[0].strip()] = d[1].strip()

                    print(f'[DEBUG] [PREDICTING LEVEL 2] V1 MACHINE LEARNING prediction Completed!')

                    print(f'[DEBUG] [PREDICTING LEVEL 2] parsing data to V2 MACHINE LEARNING algorighms...')
                    mlPredictionV2 = V2_prediction(data4Ml2)
                    print(f"ml prediction v2: {mlPredictionV2[0]}")
                    required2_dict = mlPredictionV2[0]

                    required_final = {}
                    tp = ['H', 'A', 'D']  # total possibilities

                    for t in tp:
                        d1 = required_dict.get(t, 0)
                        d2 = required2_dict.get(t, 0)

                        add = float(d1) + float(d2)
                        if add > 0:
                            required_final[t] = add

                    print(f"required final: {required_final}")

                    print(f'[DEBUG] [PREDICTING LEVEL 2] V2 MACHINE LEARNING prediction Completed!')

                    print()
                    print(
                        f'[DEBUG] [PREDICTING LEVEL 2] Evaluating result from both V1 and V2 MACHINE LEARNING algorighms...')
                    v2List = []
                    v1List = str(mlPrediction).split(" ")[0].split("/")

                    for x in mlPredictionV2[0]:
                        v2List.append(x)

                    final = combine_lists(v1List, v2List)
                    print("[Debug][ML] ML prediction V2 done!")

                    '''
                        DEEP CHECK: {deepCheck}
                        ML: {mlPrediction}
                        ML V2: {mlPredictionV2}
                    '''

                    homeDetail = a.split("|")[0].split(":")[0].strip()
                    awayDetails = a.split("|")[0].split(":")[1]

                    homeDetail = homeDetail.strip().split(" ")[:-2]
                    awayDetails = awayDetails.strip().split(" ")[1:]

                    print(
                        f'[DEBUG] [PREDICTING LEVEL 2] Making final prediction based on evaluation of V1 and V2 MACHINE LEARNING algorighm results ')

                    # if len(final) <= 2:
                    def analyze_sure(result):
                        try:
                            resultList = str(result).split("\n")
                            filteredResultList = [item for item in resultList if item != ""]
                            # for f in filteredResultList:
                            #     print(f)
                            #
                            # input('ms')

                            focus = None
                            focusCount = 0
                            drawCount = 0
                            focusAbbr = None

                            if 'away' in filteredResultList[2].lower():
                                focus = "Away"
                                focusAbbr = "A"
                            elif 'home' in filteredResultList[2].lower():
                                focus = "Home"
                                focusAbbr = "H"

                            # 1/5 analysis
                            if filteredResultList[1].__contains__(f"Strong {focus}"):
                                focusCount += 1

                            # 2/5 analysis
                            if filteredResultList[2].__contains__(focus):
                                focusCount += 1

                            # 3/5 analysis
                            if filteredResultList[3].split(":")[1].__contains__(focusAbbr):
                                focusCount += 1

                            # 4/5 analysis
                            scores = filteredResultList[4].split(":")
                            hs = int(scores[1].strip())
                            a_s = int(scores[2].strip())

                            if hs == a_s:
                                drawCount += 1
                            else:
                                if hs > a_s:  # if home score is greater than away score
                                    if focus == "Home":
                                        focusCount += 1
                                else:
                                    if focus == "Away":
                                        focusCount += 1

                            # 5/5 analysis
                            scores = filteredResultList[1].split(":")
                            hs = int(scores[0].strip().split(" ")[-1].strip())
                            a_s = int(scores[1].strip().split(" ")[0].strip())

                            if hs == a_s:
                                drawCount += 1
                            else:
                                if hs > a_s:  # if home score is greater than away score
                                    if focus == "Home":
                                        focusCount += 1
                                else:
                                    if focus == "Away":
                                        focusCount += 1

                            return f"{focusCount}/{drawCount}"
                        except Exception as e:
                            print()
                            # print(f"[ERROR!] {e}" )
                            # print(result)
                            print()
                            return f"-/-"
                            pass

                        pass

                    if len(final) == 1:
                        result = f"""
                                        [{game_time}]
                                        {' '.join(homeDetail)} {homeScore} : {awayScore} {' '.join(
                            awayDetails)} | [ {evaluate(a)},{evaluate(
                            b)},{evaluate(c)} ]
                                        PLAY:       [ {process_final(final)} ] 
                                        RQD FINAL:  {required_final}
                                        Scores:     {mlPredictionV2[1]} :  {mlPredictionV2[2]} """

                        result_sure = f"""
                                        {result}
                                        RATINGS:       {analyze_sure(result)}
                                        ===========================================================================================================
                                        """

                        save_ml_to_excel(ml)

                        with open("result.txt", 'a', encoding='utf-8') as f:
                            f.write(result_sure)
                    else:
                        resultx = f"""
                                        [{game_time}]
                                        {' '.join(homeDetail)} {homeScore} : {awayScore} {' '.join(awayDetails)}
                                        PLAY:       {v1List}  | {mlPrediction}
                                                    {v2List}  | {mlPredictionV2}
                                                    [ {process_final(final)} ] 
                                        RQD FINAL:  {required_final}
                                        ===========================================================================================================
                                    """

                        save_ml_to_excel(ml)

                        with open("result.txt", 'a', encoding='utf-8') as f:
                            f.write("[X]")
                            # f.write(result)

                        if len(final) == 2:
                            with open("result_excluded.txt", 'a', encoding='utf-8') as f:
                                f.write(resultx)
                        else:
                            with open("result_excluded.txt", 'a', encoding='utf-8') as f:
                                f.write("[X]")
                    pass
                except Exception as e:
                    print(f"[ERROR][football_prediciton_old()] {e}")

            def football_prediction_new():
                try:
                    print(f"[FB][DEBUG] Initalizing predicting enging...")
                    predict_engine = FootballPrediction2()

                    print(f'[FB][DEBUG] [PREDICTING] Using WINS ratio and H2H data...')
                    # get test result of machine lerarning on the data
                    a = predict_engine.analyze_fb_matches(newdata, new_home, new_away)

                    if type(a) is tuple:
                        print(f"No data for {a[2]} and {a[3]}")
                        print()

                        return

                    bb_pred_features = {}

                    def get_and_save_fb_ml_data(a):
                        odds = get_home_away_odds(home, away)

                        print()
                        ml = {}

                        ml['home'] = new_home
                        ml['away'] = new_away
                        ml['home_odd'] = round(float(odds[0]), 2)
                        ml['away_odd'] = round(float(odds[1]), 2)
                        ml['odd_difference'] = abs(ml['home_odd'] - ml['away_odd'])
                        ml['home_score'] = a['Average_Total_Score_Prediction_Home']
                        ml['away_score'] = a['Average_Total_Score_Prediction_Away']
                        ml['status'] = "pending"

                        features = ml.copy()

                        features.pop('home')
                        features.pop('away')
                        features.pop('status')

                        save_ml_to_excel(ml, 'ml_fb.xlsx')

                        return features

                    print(f"[FB][DEBUG] Saving past matches analysis to ML file")
                    # save match alnalysis to file and retreive features for ML prediction
                    fb_pred_features = get_and_save_fb_ml_data(a)

                    print('Starting machine learning algorithms...')
                    prediction, accuracy = football_ml_predictions(fb_pred_features)

                    def calculate_summary(prediction, accuracy):
                        print("Calculating surmary...")
                        # Make sure the lengths of both lists are equal
                        if len(prediction) != len(accuracy):
                            raise ValueError("Lengths of lists must be equal")

                        # Initialize dictionaries to store total accuracy and count for each prediction
                        total_accuracy = {'A': 0, 'H': 0, 'D': 0}
                        count = {'A': 0, 'H': 0, 'D': 0}

                        # Iterate through the prediction and accuracy lists simultaneously
                        for pred, acc in zip(prediction, accuracy):
                            # Update total accuracy and count for each prediction class
                            total_accuracy[pred] += acc
                            count[pred] += 1

                        # Calculate the average accuracy for each prediction class
                        average_accuracy = {pred: total_accuracy[pred] / count[pred] if count[pred] != 0 else 0 for pred
                                            in
                                            total_accuracy}

                        # Remove keys with value 0
                        average_accuracy = {key: value for key, value in average_accuracy.items() if value != 0}

                        # Round up the values to the nearest whole number
                        average_accuracy = {key: round(value) for key, value in average_accuracy.items()}

                        return average_accuracy

                    def count_occurrences(lst):
                        # Initialize an empty dictionary to store the counts
                        counts = {}

                        # Iterate through the list
                        for element in lst:
                            # If the element is already in the dictionary, increment its count
                            if element in counts:
                                counts[element] += 1
                            # If the element is not in the dictionary, add it with a count of 1
                            else:
                                counts[element] = 1

                        return counts

                    occurrence_count = count_occurrences(prediction)

                    def format_dict_values(input_data):
                        # If the input is a string, convert it to a dictionary
                        if isinstance(input_data, str):
                            input_data = ast.literal_eval(input_data)

                        # Define the order of keys and initialize the result list
                        key_order = ['H', 'A', 'D']
                        result = []

                        # Construct the result list based on the key order
                        for key in key_order:
                            if key in input_data:
                                result.append(str(input_data[key]))
                            else:
                                result.append('0')

                        # Join the result list with '--' and return the result string
                        return ''.join(result)

                    def update_dict_with_list(main_dict, keys_to_add):
                        for key in keys_to_add:
                            if key not in main_dict:
                                main_dict[key] = ''
                        return main_dict

                    def get_code_dict():
                        try:
                            with open("code_dict.txt", 'r', encoding='utf-8') as f:
                                d = f.read()
                                if d == "":
                                    return {}
                                else:
                                    if isinstance(d,str):
                                        d = eval(d)
                                        return d
                            pass
                        except:
                            return {}
                        pass

                    def save_code_dict(codeDict):
                        try:
                            with open("code_dict.txt", 'w', encoding='utf-8') as f:
                                f.write(str(codeDict))
                            pass
                        except:
                            pass

                    def save_code(code):
                        newCode = []
                        try:
                            with open("code.txt", 'r', encoding='utf-8') as f:
                                loaded_code = f.read()
                                if loaded_code == "":
                                    loaded_code = []
                        except:
                            loaded_code = []

                        if isinstance(loaded_code, str):
                            loaded_code = eval(loaded_code)

                        loaded_code.append(code)
                        # print(f"1. {loaded_code}")

                        loaded_code = list(set(loaded_code))
                        # print(f"2. {loaded_code}")

                        # print(f"writing: {loaded_code}")
                        with open("code.txt", 'w', encoding='utf-8') as f:
                            f.write(str(loaded_code))

                        return loaded_code

                    code = format_dict_values(occurrence_count)
                    last_loaded_code_list = save_code(code)
                    main_code_dict = get_code_dict()

                    updated_code_dict = update_dict_with_list(main_code_dict, last_loaded_code_list)

                    save_code_dict(updated_code_dict)

                    def get_experienced_result(code):
                        mainDict = get_code_dict()
                        result = mainDict.get(code, "No Record")

                        if result == "":
                            return "Unknown"

                        return result

                    def simplify_experience(experience):
                        if experience == "H/D":
                            return "Home or Draw [1X]"
                        elif experience == "H/A":
                            return "Home or Away [12]"
                        elif experience == "D/A":
                            return "Away or Draw [X2]"
                        elif  experience == "D" :
                            return f"Lowest odd (H/A) / D"
                        else:
                            return "N/A"

                    def sum_dictionary_values(input_data):
                        # If the input is a string, convert it to a dictionary
                        if isinstance(input_data, str):
                            input_data = ast.literal_eval(input_data)

                        # Calculate the sum of values in the dictionary
                        total_sum = sum(input_data.values())

                        return total_sum
                    summary = calculate_summary(prediction, accuracy)
                    experience = get_experienced_result(code)

                    result = f"""
                                   Game Time:      [ {game_time} ]
                                   Teams:          {new_home} : {new_away}
                                   Prediction:     {prediction}
                                   Accuracy:       {accuracy}
                                   Summary:        {summary}  [{sum_dictionary_values(summary)}]
                                                   {occurrence_count} [{code}]
                                                   {experience}  [{simplify_experience(experience)}]
                                   ********************************************************************************
                                   """
                    print()
                    print(result)
                    print()

                    with open("fb_result.txt", 'a', encoding='utf-8') as f:
                        f.write(result)


                    pass
                except Exception as e:
                    print(f"[ERROR][FOOTBALL_PREDICTION_NEW] {e}")


            print(f'[DEBUG] Recent game data extracted from file. Intializing Predicting Engine...')
            if sport == 'football':
                # football_prediction_old()
                football_prediction_new()

            elif sport == 'basketball':
                print(f"[BB][DEBUG] Initalizing predicting enging...")
                predict_engine = BasketballPrediction()

                print(f'[BB][DEBUG] [PREDICTING] Using WINS ratio and H2H data...')
                # get test result of machine lerarning on the data
                a = predict_engine.analyze_bb_matches(newdata, new_home, new_away)


                if type(a) is tuple:
                    print(f"No data for {a[2]} and {a[3]}")
                    print()

                    return

                bb_pred_features = {}

                def get_and_save_bb_ml_data(a):
                    odds = get_home_away_odds(home, away)

                    print()
                    ml={}

                    ml['home'] = new_home
                    ml['away'] = new_away
                    ml['home_odd'] = round(float(odds[0]), 2)
                    ml['away_odd'] = round(float(odds[1]), 2)
                    ml['odd_difference'] = abs(ml['home_odd'] - ml['away_odd'])
                    ml['home_Q1'] = a['Average_Quarterly_Score_Home'][0]
                    ml['home_Q2'] = a['Average_Quarterly_Score_Home'][1]
                    ml['home_Q3'] = a['Average_Quarterly_Score_Home'][2]
                    ml['home_Q4'] = a['Average_Quarterly_Score_Home'][3]
                    ml['away_Q1'] = a['Average_Quarterly_Score_Away'][0]
                    ml['away_Q2'] = a['Average_Quarterly_Score_Away'][1]
                    ml['away_Q3'] = a['Average_Quarterly_Score_Away'][2]
                    ml['away_Q4'] = a['Average_Quarterly_Score_Away'][3]
                    ml['home_score'] = a['Average_Total_Score_Prediction_Home']
                    ml['away_score'] = a['Average_Total_Score_Prediction_Away']
                    ml['status'] = "pending"

                    features = ml.copy()

                    features.pop('home')
                    features.pop('away')
                    features.pop('status')

                    save_ml_to_excel(ml, 'ml_bb.xlsx')

                    return features

                print(f"[BB][DEBUG] Saving past matches analysis to ML file")
                bb_pred_features = get_and_save_bb_ml_data(a)

                print('Starting machine learning algorithms...')
                prediction, accuracy = basketball_ml_predictions(bb_pred_features)

                def calculate_summary(prediction, accuracy):
                    print("Calculating surmary...")
                    # Make sure the lengths of both lists are equal
                    if len(prediction) != len(accuracy):
                        raise ValueError("Lengths of lists must be equal")

                    # Initialize dictionaries to store total accuracy and count for each prediction
                    total_accuracy = {'A': 0, 'H': 0}
                    count = {'A': 0, 'H': 0}

                    # Iterate through the prediction and accuracy lists simultaneously
                    for pred, acc in zip(prediction, accuracy):
                        # Update total accuracy and count for each prediction class
                        total_accuracy[pred] += acc
                        count[pred] += 1

                    # Calculate the average accuracy for each prediction class
                    average_accuracy = {pred: total_accuracy[pred] / count[pred] if count[pred] != 0 else 0 for pred in
                                        total_accuracy}

                    # Remove keys with value 0
                    average_accuracy = {key: value for key, value in average_accuracy.items() if value != 0}

                    # Round up the values to the nearest whole number
                    average_accuracy = {key: round(value) for key, value in average_accuracy.items()}

                    return average_accuracy

                def count_occurrences(lst):
                    # Initialize an empty dictionary to store the counts
                    counts = {}

                    # Iterate through the list
                    for element in lst:
                        # If the element is already in the dictionary, increment its count
                        if element in counts:
                            counts[element] += 1
                        # If the element is not in the dictionary, add it with a count of 1
                        else:
                            counts[element] = 1

                    return counts

                result = f"""
                Game Time:      [ {game_time} ]
                Teams:          {new_home} : {new_away}
                Prediction:     {prediction}
                Accuracy:       {accuracy}
                Summary:        {calculate_summary(prediction,accuracy)}
                                {count_occurrences(prediction)}
                ********************************************************************************
                """
                print()
                print(result)
                print()

                with open("bb_result.txt", 'a', encoding='utf-8') as f:
                    f.write(result)

            elif sport == 'football_new':
                football_prediction_new()


        except Exception as e:
            print(f"An Error occurred in Predict(): {e}")
            print('SKIPPING.....')

    def basketball_ml_predictions(featured_data=None):

        def load_and_prepare_data(file_path):
            data = pd.read_excel(file_path)
            # Remove rows with 'pending' status and missing values
            data = data[(data['status'] != 'pending') & (data['status'].notna())]
            features = data.drop(columns=["home", "away", "status"])
            target = data["status"]
            le = LabelEncoder()
            target_encoded = le.fit_transform(target)
            return features, target_encoded, le

        # Function to train models and calculate accuracy
        def train_and_evaluate_models(X_train, X_test, y_train, y_test):
            models = {
                "Logistic Regression": LogisticRegression(max_iter=1000),
                "Decision Tree": DecisionTreeClassifier(),
                "Random Forest": RandomForestClassifier(),
                "SVM": SVC(),
                "Naive Bayes": GaussianNB()
            }
            accuracies = {}
            for model_name, model in models.items():
                model.fit(X_train, y_train)
                joblib.dump(model, f"{model_name}.pkl")
                predictions = model.predict(X_test)
                accuracy = accuracy_score(y_test, predictions)
                accuracies[model_name] = accuracy * 100  # Convert to percentage
            return accuracies

        def predict_old(features_list):
            # Define the feature names based on the training data
            feature_names = ['home_odd', 'away_odd', 'odd_difference', 'home_Q1', 'home_Q2', 'home_Q3', 'home_Q4',
                             'away_Q1', 'away_Q2', 'away_Q3', 'away_Q4', 'home_score', 'away_score']

            # Convert the list of features into a DataFrame with feature names
            features_df = pd.DataFrame([features_list], columns=feature_names)

            predictions = []
            for model_name in ["Logistic Regression", "Decision Tree", "Random Forest", "SVM", "Naive Bayes"]:
                loaded_model = joblib.load(f"{model_name}.pkl")
                pred = loaded_model.predict(features_df)
                predictions.append(label_encoder.inverse_transform(pred)[0])
            return predictions

        def predict(features):
            # Define the feature names based on the training data
            feature_names = ['home_odd', 'away_odd', 'odd_difference', 'home_Q1', 'home_Q2', 'home_Q3', 'home_Q4',
                             'away_Q1', 'away_Q2', 'away_Q3', 'away_Q4', 'home_score', 'away_score']

            # Check if features is a list, convert to DataFrame
            if isinstance(features, list):
                features_df = pd.DataFrame([features], columns=feature_names)
            # Check if features is a dictionary, convert to DataFrame
            elif isinstance(features, dict):
                features_df = pd.DataFrame([features])
            else:
                raise ValueError("Features must be either a list or a dictionary.")

            predictions = []
            for model_name in ["Logistic Regression", "Decision Tree", "Random Forest", "SVM", "Naive Bayes"]:
                loaded_model = joblib.load(f"{model_name}.pkl")
                pred = loaded_model.predict(features_df)
                predictions.append(label_encoder.inverse_transform(pred)[0])
            return predictions

        # Main script
        # Load and prepare data
        print(f"[BB][ML][DEBUG] Loading and cleaning data...")
        features, target_encoded, label_encoder = load_and_prepare_data("ml_bb.xlsx")

        print(f"[BB][ML][DEBUG] Training data...")
        X_train, X_test, y_train, y_test = train_test_split(features, target_encoded, test_size=0.2,
                                                            random_state=42)

        # Train models and get accuracy
        model_accuracies = train_and_evaluate_models(X_train, X_test, y_train, y_test)
        # print("Model Accuracies:")
        accuracy_list = []
        for model_name, accuracy in model_accuracies.items():
            # print(f"{model_name}: {accuracy:.2f}%")
            accuracy_list.append(float(f"{accuracy:.2f}"))

        # sample_features = [1.8, 1.87, 0.07, 18.75, 14.25, 16, 19.25, 18.5, 20, 21, 17.75, 96.055, 95.265]
        sample_features_dict = {
            'home_odd': 1.8, 'away_odd': 1.87, 'odd_difference': 0.07, 'home_Q1': 18.75, 'home_Q2': 14.25,
            'home_Q3': 16, 'home_Q4': 19.25, 'away_Q1': 18.5, 'away_Q2': 20, 'away_Q3': 21, 'away_Q4': 17.75,
            'home_score': 96.055, 'away_score': 95.265
        }

        result = predict(featured_data)

        def remove_below_threshold(labels, values, threshold):
            # Make sure the lengths of both lists are equal
            if len(labels) != len(values):
                raise ValueError("Lengths of lists must be equal")

            # Create a new list to store filtered values and labels
            filtered_labels = []
            filtered_values = []

            # Iterate through both lists simultaneously
            for label, value in zip(labels, values):
                # Check if the value is greater than or equal to the threshold
                if value >= threshold:
                    # If so, add the label and value to the filtered lists
                    filtered_labels.append(label)
                    filtered_values.append(value)

            return filtered_labels, filtered_values

        pred, acc = remove_below_threshold(result, accuracy_list, 0)

        return pred, acc

    def football_ml_predictions(featured_data=None):

        def load_and_prepare_data(file_path):
            data = pd.read_excel(file_path)
            # Remove rows with 'pending' status and missing values
            data = data[(data['status'] != 'pending') & (data['status'].notna())]
            features = data.drop(columns=["home", "away", "status"])
            target = data["status"]
            le = LabelEncoder()
            target_encoded = le.fit_transform(target)
            return features, target_encoded, le

        # Function to train models and calculate accuracy
        def train_and_evaluate_models(X_train, X_test, y_train, y_test):
            models = {
                "Logistic Regression": LogisticRegression(max_iter=1000),
                "Decision Tree": DecisionTreeClassifier(),
                "Random Forest": RandomForestClassifier(),
                "SVM": SVC(),
                "Naive Bayes": GaussianNB()
            }
            accuracies = {}
            for model_name, model in models.items():
                model.fit(X_train, y_train)
                joblib.dump(model, f"{model_name}.pkl")
                predictions = model.predict(X_test)
                accuracy = accuracy_score(y_test, predictions)
                accuracies[model_name] = accuracy * 100  # Convert to percentage
            return accuracies

        def predict(features):
            # Define the feature names based on the training data
            # Features: {'home_odd': 3.33, 'away_odd': 1.99, 'odd_difference': 1.34, 'home_score': 1.8938461538461537, 'away_score': 1.616923076923077}

            feature_names = ['home_odd', 'away_odd', 'odd_difference', 'home_score', 'away_score']

            # Check if features is a list, convert to DataFrame
            if isinstance(features, list):
                features_df = pd.DataFrame([features], columns=feature_names)
            # Check if features is a dictionary, convert to DataFrame
            elif isinstance(features, dict):
                features_df = pd.DataFrame([features])
            else:
                raise ValueError("Features must be either a list or a dictionary.")

            predictions = []
            for model_name in ["Logistic Regression", "Decision Tree", "Random Forest", "SVM", "Naive Bayes"]:
                loaded_model = joblib.load(f"{model_name}.pkl")
                pred = loaded_model.predict(features_df)
                predictions.append(label_encoder.inverse_transform(pred)[0])
            return predictions

        # Main script
        # Load and prepare data
        print(f"[FB][ML][DEBUG] Loading and cleaning data...")
        features, target_encoded, label_encoder = load_and_prepare_data("ml_fb.xlsx")

        print(f"[FB][ML][DEBUG] Training data...")
        X_train, X_test, y_train, y_test = train_test_split(features, target_encoded, test_size=0.2,
                                                            random_state=42)

        # Train models and get accuracy
        model_accuracies = train_and_evaluate_models(X_train, X_test, y_train, y_test)
        # print("Model Accuracies:")
        accuracy_list = []
        for model_name, accuracy in model_accuracies.items():
            # print(f"{model_name}: {accuracy:.2f}%")
            accuracy_list.append(float(f"{accuracy:.2f}"))

        # sample_features = [1.8, 1.87, 0.07, 18.75, 14.25, 16, 19.25, 18.5, 20, 21, 17.75, 96.055, 95.265]
        sample_features_dict = {
            'home_odd': 1.8, 'away_odd': 1.87, 'odd_difference': 0.07, 'home_Q1': 18.75, 'home_Q2': 14.25,
            'home_Q3': 16, 'home_Q4': 19.25, 'away_Q1': 18.5, 'away_Q2': 20, 'away_Q3': 21, 'away_Q4': 17.75,
            'home_score': 96.055, 'away_score': 95.265
        }

        result = predict(featured_data)

        def remove_below_threshold(labels, values, threshold):
            # Make sure the lengths of both lists are equal
            if len(labels) != len(values):
                raise ValueError("Lengths of lists must be equal")

            # Create a new list to store filtered values and labels
            filtered_labels = []
            filtered_values = []

            # Iterate through both lists simultaneously
            for label, value in zip(labels, values):
                # Check if the value is greater than or equal to the threshold
                if value >= threshold:
                    # If so, add the label and value to the filtered lists
                    filtered_labels.append(label)
                    filtered_values.append(value)

            return filtered_labels, filtered_values

        pred, acc = remove_below_threshold(result, accuracy_list, 0)

        return pred, acc

    def ml_prediction(data):
        try:
            predictionData = []

            logisticRegression = LogisticRegressionModel()
            decisionTree = DecisionTreeModel()
            randomForest = RandomForestModel()
            svm = SVMModel()
            naiveBayes = NaiveBayesModel()

            # logistic regression
            print('[Debug][ML] checking logistic regression...')
            if os.path.exists(logisticRegression.model_file) is False:
                print('\t\t[Debug][ML]Training model using updated data...')
                logisticRegression.train_model('ml.xlsx')
            else:
                print('\t\t[Debug][ML]Skipping model Traininga...')
            predictions = logisticRegression.predict(data)
            predictionData.append(predictions)


            # decision tree
            print('[Debug][ML] checking decision tree...')
            if os.path.exists(decisionTree.model_file) is False:
                print('\t\t[Debug][ML]Training model using updated data...')
                decisionTree.train_model('ml.xlsx')
            else:
                print('\t\t[Debug][ML]Skipping model Traininga...')

            predictions = decisionTree.predict(data)
            predictionData.append(predictions)

            # random forest
            print('[Debug][ML] checking random forest...')
            if os.path.exists(randomForest.model_file) is False:
                print('\t\t[Debug][ML]Training model using updated data...')
                randomForest.train_model('ml.xlsx')
            else:
                print('\t\t[Debug][ML]Skipping model Traininga...')

            predictions = randomForest.predict(data)
            predictionData.append(predictions,)

            # SVM
            print('[Debug][ML] checking SVM')
            if os.path.exists(svm.model_file) is False:
                print('\t\t[Debug][ML]Training model using updated data...')
                svm.train_model('ml.xlsx')
            else:
                print('\t\t[Debug][ML]Skipping model Traininga...')

            predictions = svm.predict(data)
            predictionData.append(predictions)

            # Naive bayes
            print('Checking Naive bayes...')
            if os.path.exists(naiveBayes.model_file) is False:
                print('\t\t[Debug][ML]Training model using updated data...')
                naiveBayes.train_model('ml.xlsx')
            else:
                print('\t\t[Debug][ML]Skipping model Traininga...')

            predictions = naiveBayes.predict(data)
            predictionData.append(predictions)

            print(f"[Debug][ML] PREDICTIONS FROM ML_PREDICTION: {predictionData}")

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

    def extract_team_info(url, focussed_days: list, sport='football', no_of_pages=1, tomorrow=False):
        if tomorrow is True:
            no_of_pages = 100


        # variable declarations
        no_bet_class = "m-sport-bet-no-data"
        match_league = "match-league"
        league_title = "league-title"
        match_table_class = "m-table.match-table"
        match_content_row_class = "m-table-row.m-content-row.match-row"
        all_rows_class = "m-table-row"
        match_date_row_class = "m-table-row.date-row"
        game_time_class = "clock-time"
        home_team_class = "home-team"
        away_team_class = "away-team"
        odd_market_class = "m-market.market" # 2 available pick the first one
        outcome_odds_class = "m-outcome-odds"
        no_bet = None
        league_games_date_class = "m-table-cell.date"

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

        def check_pagination_exists(current_driver):
            try:
                pagination = WebDriverWait(current_driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
                )
                return True
            except:
                return False

        def click_next_button(current_driver):
            try:
                # # next_button = current_driver.find_element_by_css_selector(".pagination .icon-next")
                # next_button = current_driver.find_elements(By.CSS_SELECTOR, "span.icon-next")
                # print(f"Button Found! Trying to click it")
                # time.sleep(1)
                # next_button.click()


                # Wait for the span element to be clickable
                span_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".pageNum.icon-next"))
                )

                try:
                    # check if disabled next icon is on page.
                    span_element = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".pageNum.icon-next.icon-disabled"))
                    )

                    return False
                except:
                    pass

                print("span element found! Tring to click it")
                # Click the span element
                span_element.click()
                print('click successfull')
                return True
            except:
                print(">>> Next button not found or clickable")
                return False

        try:
            # initialize driver
            print("[DEBUG] Initializing browser...")
            driver = initialize_browser()
            # load url
            print("[DEBUG] Loading url...")
            load_url(driver, url)
            # check if team data is available on page
            print("[DEBUG] Checking for data availability on the page...")
            no_bet = element_exists(driver, no_bet_class)
            if no_bet is True:
                raise Exception

            for x in range(no_of_pages):
                print(f"[DEBUG] Starting Data Extraction on page {x+1}...")
                # get list of all leagues available
                print("[DEBUG] Waiting for league table to be loaded....")
                pagination = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, match_league))
                )
                print("[DEBUG] League table detected! Getting all leagues on page...")

                leagues = driver.find_elements(By.CLASS_NAME, match_league)

                print(f'total leagues: {len(leagues)}')

                if len(leagues) == 0:
                    raise Exception

                # Loop through the leagues
                # -----------------------------
                print("[DEBUG] Looping through all leagues to extract game data...")
                for index, league in enumerate(leagues):

                    league_details = {}
                    # GET THE LEAGUE TITLE
                    # ---------------------
                    title = get_league_title(league, league_title)
                    league_details['title'] = clean_text(title).strip()
                    print(f"\r[DEBUG][{league_details['title']}] Extracting game data...", end="")

                    # GET MATCH TABLE
                    # -----------------
                    # contains all the
                    matchTableData = get_match_table(league, match_table_class)

                    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    # DESIGNED TO SKIP GAMES IN UNWANTED DATE (to be reviewed)
                    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    # if tomorrow is True:
                    #     # GET THE DAY(DATE) THE GAMES IN THE ROWS WILL BE PLAYED.
                    #     games_date = get_game_date(matchTableData, league_games_date_class).text
                    #
                    #     todayDate = int(datetime.today().day)
                    #     gameDate = int(games_date.split('/')[0])
                    #
                    #     # if gameDate != todayDate + 1:
                    #     if str(gameDate) not in focussed_days:
                    #         print()
                    #         # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    #         print(f"\t[][][][][]date {gameDate}! Not in range....")
                    #         # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    #         time.sleep(2)
                    #         # skip the extraction and check the next one. as we are looking only for tomorrow's date
                    #         continue
                    #     else:
                    #         print()
                    #         print(f"\tYEAH!  - {gameDate} - Working on tomorrows's game......")
                    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

                    # GET THE NUMBER OF ROWS IN THE MATCH TABLE
                    #------------------------------------------
                    # tableRows = get_table_rows(matchTableData, match_content_row_class) # to be replace by below

                    tableRows =[]
                    # trying to separate date row from content row
                    all_rows = get_table_rows(matchTableData, all_rows_class)
                    print(f"TOTAL ROWS BEFORE: {len(all_rows)}")

                    # looping through the rows to filter out games in unwanted dates.
                    skip = False
                    for row in all_rows:
                        className = row.get_attribute('class')

                        # if current item is a date row
                        if className == "m-table-row date-row":
                            # check date
                            # GET THE DAY(DATE) THE GAMES IN THE ROWS WILL BE PLAYED.
                            games_date = get_game_date(row, league_games_date_class).text

                            todayDate = int(datetime.today().day)
                            gameDate = int(games_date.split('/')[0])

                            if str(gameDate) not in focussed_days:
                                print(f"[][][] REJected Date - {gameDate} not in {focussed_days}")
                                skip = True
                            else:
                                print(f"<><><> Accepted date - {gameDate}")
                                skip = False
                            pass

                        # if current itme is a content row
                        print(f"CLASS NAME: {className} --- skip {skip}")
                        if className == "m-table-row m-content-row match-row":
                            print('class name found for content row')
                            if skip is False:
                                tableRows.append(row)

                    print(f"TOTAL ROWS AFTER: {len(tableRows)}")

                    if len(tableRows) <= 0:
                        print(f"No suitable game in {title}! Going next...")
                        continue

                    # LOOP THROUGH THE ROWS IN THE TABLE TO EXTRACT DATA
                    # ---------------------------------------------------
                    # print(f"{index}/{len(leagues)} looping through roes to get data for {title}")
                    gameDetails =[]
                    for row in tableRows:
                        try:
                            single_game_detail = {}

                            gameTime = row.find_element(By.CLASS_NAME, game_time_class).text
                            single_game_detail['game_time'] = gameTime

                            single_game_detail['league'] = league_details['title']
                            # print(f"game time: {gameTime}")

                            homeTeam = row.find_element(By.CLASS_NAME, home_team_class).text
                            single_game_detail['home_team'] = homeTeam

                            awayTeam = row.find_element(By.CLASS_NAME, away_team_class).text
                            single_game_detail['away_team'] = awayTeam

                            oddMarkets = row.find_element(By.CLASS_NAME, odd_market_class) # trying to select the first one only
                            outcomeOdds = oddMarkets.find_elements(By.CLASS_NAME, outcome_odds_class)

                            # print(f'total: {len(outcomeOdds)} | {single_game_detail["home_team"]}')
                            homeWinOdd = outcomeOdds[0].text
                            single_game_detail['home_odd'] = homeWinOdd

                            if sport == 'football':
                                # print("[]Football")
                                drawOdd = outcomeOdds[1].text
                                single_game_detail['draw_odd'] = drawOdd

                                awayWinOdd = outcomeOdds[2].text
                                single_game_detail['away_odd'] = awayWinOdd
                            elif sport == 'basketball':
                                # print("[]Basketball")
                                awayWinOdd = outcomeOdds[1].text
                                single_game_detail['away_odd'] = awayWinOdd

                            gameDetails.append(single_game_detail)
                        except Exception as e:
                            print(f"Error in row loop: {e}")
                            continue

                    league_details['data'] = gameDetails

                    all_leagues_data.append(league_details)
                    # print(f"{index}/{len(leagues)} >. data added for {title}")

                print()
                if x+1 < no_of_pages:
                    # checking of multiple pages exists
                    ans = check_pagination_exists(driver)
                    if ans is False:
                        print(f"[{x+1}] Pagination not found on page!")
                        break
                    else:
                        print(f"[{x+1}] pagination section seen on page.")
                        pass

                    print(f"NAVIGATING TO NEXT PAGE | page {x+2}")
                    ans2 = click_next_button(driver)
                    if ans2 is False:
                        break

                    time.sleep(5)
                else:
                    print("NO MORE PAGES TO EXTRACT! PROCEEDING...")

            # print(f"total all league data = {len(all_leagues_data)}")
            print()
            print("[DEBUG] Data Extraction from webpage completed!...")
            return all_leagues_data

        except Exception as e:
            if no_bet is True:
                print("[DEBUG] Bet is not available for current period. change the period or try again latter!")

            if len(leagues) == 0:
                print("[DEBUG] No league found")
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

    def get_game_date(driver, class_name):
        dt = driver.find_element(By.CLASS_NAME, class_name)
        return dt

    def reset_file(filename):
        with open(filename, 'w') as f:
            f.write("")

    def write_append_to_file(filename, data):
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(data)

    def get_all_odds_data():
        oddData = []
        with open('teamOnlyData.txt', 'r', encoding='utf-8') as f:
            data = f.read()

        with open('oddOnlyData.txt', 'r', encoding='utf-8') as f:
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
        if odd_info is None:
            return "UNKNOW | odd info not available!"
        homeOdd = round(float(odd_info[0]),2)
        awayOdd = round(float(odd_info[1]), 2)

        oddDiff = round(abs(homeOdd - awayOdd), 2)
        lowestOdd = odd_info[2]

        # {'Home/Draw' : [1.43 -  5.5] |'LO/Draw':  [0.5 - 0.65] |'Home/Away':  [0.1 -0.25]} WR: (67%)
        # print(f"SUGGESTION HERE: {suggestion}")
        if suggestion.lower() == 'unknown':
            return None

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
    # clean model files
    def clean_model_files():
        try:
            logisticRegression = LogisticRegressionModel()
            decisionTree = DecisionTreeModel()
            randomForest = RandomForestModel()
            svm = SVMModel()
            naiveBayes = NaiveBayesModel()

            logisticRegression.delete_model_file()
            decisionTree.delete_model_file()
            randomForest.delete_model_file()
            svm.delete_model_file()
            naiveBayes.delete_model_file()
            print(f"EXISTING MODEL FILE CLEANED SUCCESSFULLY")
        except Exception as e:
            print(f"An Error occurred while cleaning model files: {e}")
            print(f"CLEANING OF EXISTING MODEL FILE FAILED!")
            pass

    def clean_data_file():
        try:
            if os.path.exists(f"datafile.xlsx") is True:
                path = os.getcwd()
                os.remove(os.path.join(path, "datafile.xlsx"))

            # test = 0
            # while True:
            #     if os.path.exists(f"datafile{test}.xlsx") is True:
            #         test += 1
            #         pass
            #     else:
            #         print(f'[{test}]Now renaming...')
            #         path = os.getcwd()
            #         if os.path.exists(f"datafile.xlsx") is True:
            #             os.rename(os.path.join(path, "datafile.xlsx"), os.path.join(path, f"datafile{test}.xlsx"))
            #         break
            #     time.sleep(1)
        except Exception as e:
            print(f"[ERROR][clean_data_file()] {e}")
            pass


    def start_add_pattern():
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
                    error = True
                else:
                    a, b, c, result = combinations.split(",")
                    analyzer.add_combination(a, b, c, result)
                    error = False

            print(f"Done for {data}")
        # input("Wait here...................")
        pass

    def start_predict(sport='football'):
        # delete existing model
        clean_model_files()

        # open file that contains all the teams to be predicted
        with open('teamOnlyData.txt', 'r', encoding='utf-8') as f:
            raw = f.read()

        # open file that contains all the time
        with open('timeOnlyData.txt', 'r', encoding='utf-8') as f:
            rawtime = f.read()

        teamList = []
        timeList = []
        # split team by new line
        rawsplit = raw.strip().split("\n\n")
        rawtimesplit = rawtime.strip().split("\n\n")

        # from the split teams extrac home and away team
        for split in rawsplit:
            h = split.split("|")[0]
            a = split.split("|")[1]

            value = (h, a)
            teamList.append(value)

        def initialize_browser1():
            # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
            driver = webdriver.Chrome()
            return driver

        def load_url(driver, url):
            try:
                driver.set_page_load_timeout(30)
                driver.get(url)
                return True
            except TimeoutException:
                return True
            except Exception as e:
                return False

        # [experimental] - Trying to use the same driver for all extract
        def load_browser():
            print("Initializing Browser for  data extraction! Please wait...")
            url = "https://www.sofascore.com/"
            driver = initialize_browser1()
            while True:
                try:
                    driver.set_page_load_timeout(30)
                    driver.get(url)
                    break
                except TimeoutException:
                    break
                    pass
                except Exception:
                    print("[DEBUG] - Error loading page! Refreshing and retrying...")
                    time.sleep(5)
                    driver.refresh()
                    pass
            print('done loading initial page!')
            return driver

        driver = None
        driver = load_browser()

        # loop through each home and way team to predict
        for index, team in  enumerate(teamList):
            home = team[0]
            away = team[1]
            gameTime = rawtimesplit[index]
            predict(gameTime, home, away, driver, sport)

            print("------>>>>>>> NEXT")
            # input("Wait.....................................")
            print()
            time.sleep(2)

        print("DONE!DONE!DONE!DONE!")



        pass

    def V2_prediction(data):
        global use_old_model
        try:

            football_model = FootballPredictionModel('ml2.xlsx')
            final_result = []

            # expected sample data
            # data = {'home_odd': 5.4, 'away_odd': 1.56, 'odd_difference': 3.84, 'strong_home': 1, 'strong_away': 0, 'strong_draw': 1, 'weak_home': 0, 'weak_away': 0}

            for algorithm in algorighm_list:
                algorithm = str(algorithm).lower()

                print(f"Training and predicting with {algorithm}...")
                # TRAINING MODEL
                if use_old_model is False:
                    football_model.train_and_save_model(algorithm)
                else:
                    print(f"[DEBUB] Now using existing trained model!")

                # PREDICTING WITH THE MODEL
                status = football_model.predict(data, 'status', algorithm)
                home_score = football_model.predict(data, 'home_score', algorithm)
                away_score = football_model.predict(data, 'away_score', algorithm)

                final_result.append((status[0], home_score[0], away_score[0]))
                print(f"Training and predicting Done! -  {algorithm}...")

            def analyze_results(results):
                total_count = len(results)
                status_counts = {'H': 0, 'D': 0, 'A': 0}
                total_home_score = 0
                total_away_score = 0

                for result in results:
                    status, home_score, away_score = result
                    status_counts[status] += 1
                    total_home_score += home_score
                    total_away_score += away_score

                status_percentages = {status: count / total_count * 100 for status, count in status_counts.items() if count != 0}
                home_score_average = total_home_score / total_count
                away_score_average = total_away_score / total_count

                return (status_percentages, round(home_score_average), round(away_score_average))

            # Example usage:
            print(f"Analyzing and sumarizing V2 results")
            print(f"V2 Final result: {final_result}")
            analysis = analyze_results(final_result)

            use_old_model = True
            return analysis
        except Exception as e:
            print(f"An Error occurred in V2 Prediction: {e}")
            pass

    def start_extract(sport = "football", no_of_pages=1):
        tomorrow = None
        # reset datafile.xlsx to contain only new extracted data.
        clean_data_file()

        # Extract data from sporty
        reset_file(teamData)
        reset_file("oddOnlyData.txt")
        reset_file("teamOnlyData.txt")
        reset_file("timeOnlyData.txt")

        def get_today():
            # Get today's date
            today = datetime.today()

            # Extract the day component
            day = today.day

            return str(day)

        period = 3
        focussedDays = None

        dt = input("Specify dates(day) to extract [25] or [25,26] or [Enter for today]: ")
        if dt == "":
            tomorrow = False
            focussedDays = [get_today()]

        elif dt.strip() == str(get_today()):
            # in case today's date was typed manually instead of pressing Enter
            tomorrow = False
            focussedDays = [get_today()]
        else:
            tomorrow = True
            if "," not in dt:
                focussedDays = [dt]
            else:
                focussedDays = dt.split(",")

        if tomorrow is False:
            ans = input (f"( {sport.upper()} )( EXTRACT DATA ) Set Start Time >  [ Default = 3 ]: ")
            if ans != "":
                if ans.lower() == "all" or ans.lower() == 'a':
                    period = None
                else:
                    period = int(ans)

        print()
        print("[DEBUG] Starting Data extraction...")
        url = f"https://www.sportybet.com/ng/sport/{sport}"

        if tomorrow is False:
            if period is None:
                url = f"https://www.sportybet.com/ng/sport/{sport}"
                no_of_pages = 100
            else:
                url = f"https://www.sportybet.com/ng/sport/{sport}?time={period}"
                no_of_pages = 1

        # print("[DEBUG] Extracting team info...")
        leagueInfo = extract_team_info(url=url, focussed_days=focussedDays,sport=sport, no_of_pages=no_of_pages, tomorrow=tomorrow)

        allData = []
        print("[DEBUG] Compiling Extracted Data...")
        for league in leagueInfo:
            print(f"\r[DEBUG] Compiling Extracted Data {league}...", end="")
            # print(f"League: {league['title']}")
            # print(f"Data: {league['data']}")
            # input('waiting......')
            # print("=============================================================")
            # print()
            if league['title'].lower().__contains__('srl'):
                continue

            result = f"League: {league['title']}"
            odd_only = ""
            team_only = ""
            time_only = ""

            for data_item in league['data']:
                # excluding simulated reality games
                if data_item['home_team'].lower().__contains__('srl'):
                    continue

                result2 = f"""{data_item['game_time']}
                    {data_item['home_team']}
                    {data_item['away_team']}
                    {data_item['home_odd']}
                    {data_item['away_odd']}
                """
                result_odd = f"""{data_item['home_odd']} | {data_item['away_odd']}"""
                result_team = f"""{data_item['home_team']} | {data_item['away_team']}"""
                result_time = f"""{data_item['game_time'].strip()}"""
                result_team_with_league = f"""{data_item['home_team']} | {data_item['away_team']} | {data_item['league']}"""

                allData.append((result_odd, result_team, result_time, result_team_with_league))

                # result += f"\n{result2}"
                # odd_only += f"{result_odd}"
                # team_only += f"{result_team}"
                # time_only += f"{result_time}"

            # result += f"\n***************************************************************************\n"
            #
            # print(result)
            # write_append_to_file(teamData, result)
            # write_append_to_file("oddOnlyData.txt", odd_only)
            # write_append_to_file("teamOnlyData.txt", team_only)

        # Custom key function to extract time from tuple
        def get_time(tup):
            return datetime.strptime(tup[2], "%H:%M")

        # Sorting the list based on time
        print("[DEBUG] Sorting Extracted Data by time...")
        sorted_data = sorted(allData, key=get_time)

        print("[DEBUG] Spliting Sorted Data into 'OddsData' | 'TeamsData | TimeData...")
        # Extracting items at index 0 and 1 from sorted data
        oddsData = [item[0] for item in sorted_data]
        teamsData = [item[1] for item in sorted_data]
        timeData = [item[2] for item in sorted_data]
        teamsDataWithLeague = [item[3] for item in sorted_data]

        print("[DEBUG] Writing sorted data to files...")
        # Writing items at odds data to a text file
        with open("oddOnlyData.txt", "w", encoding='utf-8') as file:
            file.write("\n\n".join(oddsData))

         # Writing items at team only data to a text file
        with open("teamOnlyData.txt", "w", encoding='utf-8') as file:
            file.write("\n\n".join(teamsData))

        # Writing items at time only data to a text file
        with open("timeOnlyData.txt", "w", encoding='utf-8') as file:
            file.write("\n\n".join(timeData))

        # Writing items at time only data to a text file
        with open("teamWithLeaguestxt", "w", encoding='utf-8') as file:
            file.write("\n\n".join(teamsDataWithLeague))

        # input('waiting...')
        print("[DEBUG] COMPLETED!")
        print()
        pass

    # ---------------------------------
    # ---------------------------------
    # ENTRY POINT
    # ---------------------------------
    # ---------------------------------

    sport = 'football'
    # sport = 'basketball'


    while True:
        # ensuring correct SPORT  is obtained before proceeeding..
        while True:
            s = input("Select Sport > [ {F}ootball | {B}asketball ] :  ")
            if s.lower() == 'f' or s.lower() == "football" or s == "":
                sport = "football"
                break
            elif s.lower() == 'b' or s.lower() == 'basketball':
                sport = 'basketball'
                break
            else:
                os.system('cls')
                print('[ERROR] Unrecognized sport provided! Please try again!')
                print()

        # ensuring correct ACTION is obtained before proceeding
        while True:
            command = f"Select Action ( {sport.upper()} ) > " + " [ {all} | {P}redict | {E}xtract ]: "
            action = input(command)

            if action.lower() == 'all' or action == '':
                print("[DEBUG] Starting data extraction...")
                start_extract(sport)
                print("[DEBUG] Extraction Completed! Starting prediction...")
                start_predict(sport)
                break

            elif action.lower() == 'p':
                start_predict(sport)
                break

            elif action.lower() == 'a':
                start_add_pattern()
                break

            elif action.lower() == 'e':

                start_extract(sport)
                break

            else:
                os.system('cls')
                print("[ERROR!] Unrecognized action provided! Please try again!")
                print()

        print()
        print()
        ans = input("Press any key to continue or 'e' to exit: ")
        if ans == 'e' or ans == "E":
            break

        print()

        os.system('cls')

except Exception as e:
    print(f"[APP ERROR] : {e}")

    input("press any key to exit!")




