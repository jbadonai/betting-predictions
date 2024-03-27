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
        self.timeout = 30
        self.search_textbox_class = 'sc-30244387-0.hiFyBG'
        self.data_table_class = "div.sc-fqkvVR.fZdvTU"
        self.dataFile = 'datafile.xlsx'
        self.new_team_name = []

        self.initialize()

    def initialize(self):
        self.initialize_browser()

    def initialize_browser(self):
        # Initialize the webdriver (Make sure you have the appropriate webdriver installed)
        self.driver = webdriver.Chrome()

    def load_url(self, url):
        try:
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
        all_search_list_class = 'sc-fqkvVR.sc-fUnMCh.esJGSi.hkwHv.ps ps--active-y'
        each_team_link_class = 'sc-bbd8cee0-0.jeQTnS'  # has href and other data
        game_confirmation_class = 'sc-gFqAkR.hzPof'  # under each team lnk class

        try:
            # wait for all list to be visible
            self.wait_for_element(all_search_list_class)

            # get all the links in the list
            all_links = self.driver.find_elements(By.CLASS_NAME, each_team_link_class)

            # scan the links to select link for football only for the team
            for link in all_links:
                # get the game: football, clrcket...
                game = link.find_element(By.CLASS_NAME, game_confirmation_class).text

                # filter out only football link
                if str(game).lower() == 'football':
                    # extract the href which is requried
                    team_url = link.get_attribute('href')
                    print(f"Team URL: {team_url}")
                    print("FOUND!!!!!!")
                    return team_url

        except Exception as e:
            print(f"[DEBUG][ERROR] An error occurred in get team href function: {e}")
            return None

    def extract_football_data(self, team):
        gameData = []   # stores final game data

        # declare classes required for extraction
        data_table_class = "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.iGqHmj a.sc-631ef08b-0"
        # data_table_class = "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.buMHXe"
        ha_class = "sc-gFqAkR"

        # get the whole table containing all the data
        table = self.driver.find_elements(By.CSS_SELECTOR, data_table_class)

        singleGameData = {}     # stores a single row of data in the table

        # loop through all the rows in the table to extract each data in the row
        for table_data in table:
            try:
                # get all data holder in each rows
                ha = table_data.find_elements(By.CLASS_NAME, ha_class)

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
                print(f"error:-----------")
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
                input_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, selector_name))
                )
                return True
            except:
                return False
        elif selector == 'css':
            try:
                input_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector_name))
                )
                return True
            except:
                return False

    def start_data_extraction(self, team_names: list):
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
                print(f"[DEBUG] Searchin for team's Name")
                while True:
                    search_result = self.search_team(team_name)
                    if search_result is True:
                        break
                    else:
                        print(f"[DEBUG][ERROR] Unable to search for {team_name}. Retrying...")
                        time.sleep(2)

                # b. GET THE HREF: TEAM'S URL
                # ---------------------------
                while True:
                    print("[DEBUG] Getting temas' href ")
                    team_url = self.get_team_href()
                    if team_url is not None:
                        break
                    else:
                        print("[DEBUG][ERROR] Error Extracting team's url! Retrying...")
                        time.sleep(2)

                # c. LOAD TEAM URL
                # --------------------------------
                while True:
                    print("[DEBUG]  Loading team url...")
                    ans = self.load_url(team_url)
                    # check for positive response from load url function
                    if ans is True:
                        # check if page is properly loaded by checking if search box is on page
                        on_page = self.is_element_on_page(self.data_table_class, 'css')
                        if on_page is True:
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
                print(f"Extracting Data...")
                game_data = self.extract_football_data(team_name)

                # e. SAVE GAME DATA TO EXCEL
                print("Saving Data")
                self.save_to_excel(game_data)

                self.new_team_name.append(eval(game_data[0])['team'] )

            return self.new_team_name
            pass
        except Exception as e:
            print(f"An Error occurred in start data extraction: {e}")








