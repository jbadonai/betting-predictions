from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os
import pandas as pd
import ast  # To evaluate the string representation of the dictionary
import re
from difflib import SequenceMatcher
from selenium.common.exceptions import TimeoutException


class PreviousRecordExtractor():
    def __init__(self):
        self.driver = None
        self.url = "https://www.sofascore.com/"
        self.search_textbox_class = 'sc-30244387-0.hiFyBG'
        # self.data_table_class = "div.sc-fqkvVR.fZdvTU"
        self.data_table_class = "div.js-list-cell-target"
        self.data_table_class_list = ["div.sc-fqkvVR.fZdvTU", "div.js-list-cell-target" ]
        self.dataFile = 'datafile.xlsx'
        self.new_team_name = []
        self.timeout = 15

        self.initialize()

    def initialize(self):
        self.initialize_browser()

    def initialize_browser(self):
        # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
        self.driver = webdriver.Chrome()

    def load_url(self, url):
        try:
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.get(url)
            return True
        except TimeoutException:
            return True
        except Exception as e:
            return False

    def search_team(self, team_name):
        try:
            # Wait for the input element to be visible
            input_element = WebDriverWait(self.driver, 120).until(
                EC.visibility_of_element_located((By.CLASS_NAME, self.search_textbox_class))
            )

            # Clear any existing text in the input field
            input_element.clear()

            # Insert the desired text into the input field
            input_element.send_keys(team_name)

            # Perform the search (press Enter)
            input_element.send_keys(Keys.RETURN)

            return True

        except Exception as e:
            print(f"[DEBUG] Error in search team function: {e}")
            return False

    def wait_for_element(self, element_class, time_out=10, selector='class'):
        try:
            if selector == 'class':
                input_element = WebDriverWait(self.driver,time_out).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, element_class))
                )
            if selector == 'css':
                input_element = WebDriverWait(self.driver, time_out).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, element_class))
                )
        except Exception as e:
            pass

    def get_team_href(self):
        # all_search_list_class = 'sc-fqkvVR.sc-fUnMCh.esJGSi.hkwHv.ps.ps--active-y'
        all_search_list_class = 'Box.dAFRQr'
        each_team_link_class = 'sc-bbd8cee0-0.jeQTnS'  # has href and other data
        # game_confirmation_class = 'sc-gFqAkR.hzPof'  # under each team lnk class
        game_confirmation_class = 'Text.eJlzjH'  # under each team lnk class
        team_only_filter_button = "Chip"
        team_error_class = "Text"
        errorMessage = None

        try:
            # wait for all list to be visible
            print('waiting for search list to be visible')
            self.wait_for_element(all_search_list_class, 4, 'css')
            print('done!')

            # find and click on team only filter
            filterFound = False
            gameFilterButton = self.driver.find_elements(By.CLASS_NAME, team_only_filter_button)
            for filter in gameFilterButton:
                if filter.text == "Team":
                    filter.click()
                    print(f"{filter.text} has been clicked!")
                    filterFound = True
                    break

            time.sleep(3)
            if filterFound is False:
                errorMessage = "Team Filter Not Found"
                raise Exception

            # after selecting team filter check if there is result:
            print("Checkin for team error...")
            errorFound = False
            teamErrors = self.driver.find_elements(By.CLASS_NAME, team_error_class)
            print(f"Total team errors to check = {len(teamErrors)}")
            for index,teamError in enumerate(teamErrors):
                if teamError.text == "No results found":
                    errorFound = True
                    print(f"[{index}]Team not found!")
                    break

                if index > 10:
                    print('Break by assumption!')
                    break

            # input("Testing waiting...........")
            if errorFound is True:
                errorMessage = "Team Not Found"
                raise Exception

            # get all the links in the list
            all_links = self.driver.find_elements(By.CLASS_NAME, each_team_link_class)

            # scan the links to select link for football only for the team
            print('Scanning links...')
            for link in all_links:
                # get the game: football, clrcket...
                game = link.find_element(By.CLASS_NAME, game_confirmation_class).text

                # filter out only football link
                if str(game).lower() == 'football':
                    # extract the href which is requried
                    team_url = link.get_attribute('href')
                    # print(f"Team URL: {team_url}")
                    # print("FOUND!!!!!!")
                    return team_url, errorMessage

        except Exception as e:
            print(f"[DEBUG][ERROR] An error occurred in get team href function: {e}")
            return None, errorMessage

    def find_suitable_class_name(self, class_name_list: list, byClassName=True):
        for className in class_name_list:
            if byClassName is True:
                ans = self.is_element_on_page(className)
            else:
                ans = self.is_element_on_page(className, 'css')

            if ans is True:
                return className

        return None

    def extract_football_data(self, team):
        gameData = []   # stores final game data

        # declare classes required for extraction
        data_table_class = "div.js-list-cell-target"    # represent a block of row of data in a table.
        # data_table_class = "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.iGqHmj a.sc-631ef08b-0"
        data_table_class_list = ["div.js-list-cell-target", "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.iGqHmj a.sc-631ef08b-0"]

        # ha_class = "sc-gFqAkR"
        ha_class = "Text"
        ha_class_list = ["sc-gFqAkR", "Text"]

        # print(f"finding suitable class name for DATA TABLE CLASS...")
        suitable_data_table_class = self.find_suitable_class_name(data_table_class_list, False)     # using CSS
        if suitable_data_table_class is None:
            print(f"[DEBUG][ERROR!] NO SUITABLE CLASS NAME FOUND FOR [DATA TABLE CLASS] - REPRESENTING EACH ROW IN THE TABLE\n"
                  f"UPDATE THE DATA_TABLE_CLASS_LIST WITH NEW CLASS NAME")
            raise Exception
        else:
            print(f"[DEBUG] suitable data class name found @ {suitable_data_table_class}")

        # get the whole table containing all the data
        # table = self.driver.find_elements(By.CSS_SELECTOR, data_table_class)
        table = self.driver.find_elements(By.CSS_SELECTOR, suitable_data_table_class)
        # print(f"Total data in table : {len(table)}")
        # input("wait 1...........")

        singleGameData = {}     # stores a single row of data in the table

        print(f"[DEBUG] Finding suitable class name for 'ha': .....")
        suitable_ha_class = self.find_suitable_class_name(ha_class_list)
        if suitable_ha_class is None:
            print(f"[DEBUG][ERROR!] NO SUITABLE CLASS NAME FOUND FOR  HA [actual data] - REPRESENTING EACH TO BE EXTRACTED\n"
                  f"UPDATE THE 'HA_CLASS WITH NEW CLASS NAME")
            raise Exception
        else:
            print(f"[DEBUG] suitable HA CLASS found @ {suitable_data_table_class}")

        # loop through all the rows in the table to extract each data in the row
        for table_data in table:
            try:
                # get all data holder in each rows
                # ha = table_data.find_elements(By.CLASS_NAME, ha_class)
                ha = table_data.find_elements(By.CLASS_NAME, suitable_ha_class)
                # print(f"HA:::: {ha}")

                # extract the required data from the holder
                home = ha[4].text
                away = ha[5].text
                home_score = ha[6].text
                away_score = ha[8].text
                wld = ha[10].text

                # create a dictionary of the extracted data
                singleGameData['league'] = "my league"
                singleGameData['team'] = team
                singleGameData['home'] = home
                singleGameData['away'] = away
                singleGameData['home_score'] = home_score
                singleGameData['away_score'] = away_score
                singleGameData['status'] = wld

                # append it to the final game data
                gameData.append(str(singleGameData))

            except Exception as e:
                # print(f"error:-----------")
                continue

        # returned compiled final game data
        return gameData
        pass

    def save_to_excel(self, data_list ):
        file_path = self.dataFile
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

    def retrieve_data(self, ):
        file_path = self.dataFile
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

    def is_element_on_page(self, selector_name, selector='class'):
        if selector == 'class':
            try:
                input_element = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, selector_name))
                )
                return True
            except:
                return False
        elif selector == 'css':
            try:
                input_element = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector_name))
                )
                return True
            except:
                return False

    def start_data_extraction(self, team_names: list):
        failure_count = 0
        try:
            self.new_team_name.clear()
            # 1. LOAD THE MAIN URL
            # --------------------------------
            while True:
                print("[DEBUG]  Loading main url...")
                ans = self.load_url(self.url)
                # check for positive response from load url function
                if ans is True:
                    # check if page is properly loaded by checking if search box is on page
                    on_page = self.is_element_on_page(self.search_textbox_class)
                    if on_page is True:
                        break
                    else:
                        print("[DEBUG][ERROR] Page not properly loaded! Refreshing to retry....")
                        self.driver.refresh()
                        time.sleep(5)
                else:
                    print(f"[DEBUG][ERROR] Error Loading main url! Retrying")
                    time.sleep(2)

            # 2. LOOP THROUGH ALL THE TEAMS
            for team_name in team_names:
                # a. SEARCH FOR TEAM'S NAME
                # ---------------------------
                print(f"[DEBUG] Searching for team's Name: {team_name}")
                while True:
                    search_result = self.search_team(team_name)
                    if search_result is True:
                        break
                    else:
                        print(f"[DEBUG][ERROR] Unable to search for {team_name}. Retrying...")
                        time.sleep(2)

                # b. GET THE HREF: TEAM'S URL
                # ---------------------------
                failure_count = 0
                while True:
                    print("[DEBUG] Getting temas' href ")
                    team_url, errorMessage = self.get_team_href()
                    if team_url is not None:
                        break

                    else:
                        failure_count += 1
                        if failure_count > 1 or errorMessage is not None:
                            raise Exception
                        print(f"[DEBUG][ERROR][{failure_count}] Error Extracting team's url! Retrying...")
                        time.sleep(2)

                # c. LOAD TEAM URL
                # --------------------------------
                failure_count = 0
                while True:
                    print("[DEBUG]  Loading team url...")
                    ans = self.load_url(team_url)
                    # check for positive response from load url function
                    if ans is True:
                        # check if page is properly loaded by checking if search box is on page
                        # on_page = self.is_element_on_page(self.data_table_class, 'css')
                        found = False
                        for data in self.data_table_class_list:
                            on_page = self.is_element_on_page(data, 'css')
                            if on_page is True:
                                print(f"[DEBUG] data table found using class: {data}")
                                found = True
                                break
                            print(f"[DEBUG] data table not found in: {data}! Trying next one........")
                            time.sleep(1)

                        if found is True:
                            break
                        else:
                            print(f"[DEBUG][ERROR] Team url Page [{team_url}] not properly loaded! DATA TABLE NOT FOUND ON PAGE! Refreshing to retry....")
                            self.driver.refresh()
                            time.sleep(5)
                    else:
                        print(f"[DEBUG][ERROR] Error Loading team's url [{team_url}]! Retrying")
                        time.sleep(2)

                # d. EXTRACT DATA FROM THE PAGE
                # ------------------------------
                print(f"[DEBUG] Extracting Data...")
                tester = "sc-gFqAkR"
                # tester = "div.Text"
                testerList = ["sc-gFqAkR", "Text"]

                trial = 0
                while True:
                    print('[DEBUG] Waiting for data to be availalbe...')
                    # ans = self.is_element_on_page(tester)
                    ans = self.is_element_on_page(testerList[trial])
                    if ans is True:
                        print(f"[DEBUG] Passed @ {trial}")
                        break

                    time.sleep(2)
                    trial += 1
                    if trial == len(testerList):
                        trial = 0

                game_data = self.extract_football_data(team_name)
                # print(f"Game data:: {game_data}")
                # input("::::")

                # e. SAVE GAME DATA TO EXCEL
                # print(f"Game data: {game_data}")
                print("[DEBUG] Saving Data")

                self.save_to_excel(game_data)

                self.new_team_name.append(eval(game_data[0])['team'] )
            # print(f"Data Saved! returning new teamname : {self.new_team_name}")
            return self.new_team_name
            pass
        except Exception as e:
            if failure_count > 0:
                return None
            print(f"[DEBUG] An Error occurred in start data extraction: {e}")








