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
import configparser

class PreviousRecordExtractor():
    def __init__(self, driver, sport):
        self.driver = driver
        self.url = "https://www.sofascore.com/"
        # self.search_textbox_class = 'sc-30244387-0.hiFyBG'
        self.search_textbox_class = 'sc-fMMURN.jZA-DVh'
        self.search_textbox_class_list = ['sc-dSIIpw.dtpAIu','sc-YysOf.ijRSqw','sc-fMMURN.jZA-DVh', 'sc-30244387-0.hiFyBG','sc-ePDLzJ.ExPNf']
        # self.data_table_class = "div.sc-fqkvVR.fZdvTU"
        self.data_table_class = "div.js-list-cell-target"
        self.data_table_class_list = ["div.sc-fqkvVR.fZdvTU", "div.js-list-cell-target" ]
        if sport == 'football':
            self.dataFile = 'datafile.xlsx'
        elif sport == 'basketball':
            self.dataFile = 'datafile_bb.xlsx'

        self.new_team_name = []
        self.timeout = 15
        self.sport = sport
        
        # ---------------------------------------------------------
        # defining a constant handle for element that changes on the page
        self.config_file_path = 'config.ini'
        self.section = "app_settings"

        self.search_textbox_handle = self.get_from_config(self.section, 'searchTextboxHandle')
        # self.initialize()

    # Function to save data to the config file
    def save_to_config(self, section, key, value):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, key, value)
        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)

    # Function to retrieve data from the config file
    def get_from_config(self, section, key):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        if config.has_section(section) and config.has_option(section, key):
            return config.get(section, key)
        else:
            return None

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
            # input_element = WebDriverWait(self.driver, 120).until(
            #     EC.visibility_of_element_located((By.CLASS_NAME, self.search_textbox_class))
            # )
            # input_element = self.search_textbox_handle
            # for element in self.search_textbox_class_list:
            #     print(f">[]>[] Checking {element}")
            #     try:
            input_element = WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, self.search_textbox_handle))
            )
                #     break
                # except:
                #     continue

            if input_element is None:
                return False

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

        each_team_link_class = 'sc-bbd8cee0-0.jeQTnS'  # has href and other data[no longer working]
        each_team_link_class = 'sc-ktPPKK.fLZUf'  # has href and other data
        each_team_link_class_list = ['sc-ktPPKK.fLZUf','sc-cVzyXs.iWIRcx', 'sc-bbd8cee0-0.jeQTnS','sc-bVVIoq.gItNGx']

        # game_confirmation_class = 'sc-gFqAkR.hzPof'  # under each team lnk class
        game_confirmation_class = 'Text.eJlzjH'  #  under each team lnk class
        game_confirmation_xpath = '//*[@id="__next"]/header/div[1]/div/div/div[2]/div/div/div[2]/div[1]/div/div[1]/a/div/div/div[2]/span[2]'  #  under each team lnk class
        game_confirmation_xpath1 = '//*[@id="__next"]/header/div[1]/div/div/div[2]/div/div/div[2]/div[1]/div/div[1]/a/div/div/div[2]/span'  #  under each team lnk class

        team_only_filter_button = "Chip"
        team_error_class = "Text"
        team_error_class_list = ["Text","Text.gNHtbq"]
        errorMessage = None

        try:
            # wait for all list to be visible
            self.wait_for_element(all_search_list_class, 4, 'css')

            # find and click on team only filter
            filterFound = False
            gameFilterButton = self.driver.find_elements(By.CLASS_NAME, team_only_filter_button)
            for filter in gameFilterButton:
                if filter.text == "Team":
                    filter.click()
                    filterFound = True
                    # print("Team Filter clicked!")
                    break

            time.sleep(3)
            if filterFound is False:
                errorMessage = "Team Filter Not Found"
                print("Team Filter not found!")
                raise Exception

            # after selecting team filter check if there is result:
            print('checking if no team is available...')
            errorFound = False
            teamErrors = self.driver.find_elements(By.CLASS_NAME, team_error_class)
            # print(f"total error class: {len(teamErrors)}")
            for index,teamError in enumerate(teamErrors):
                if teamError.text == "No results found":
                    errorFound = True
                    break
                if index > 10:
                    break

            # input("Testing waiting...........")
            if errorFound is True:
                errorMessage = "Team Not Found"
                raise Exception

            # get all the links in the list
            # all_links = self.driver.find_elements(By.CLASS_NAME, each_team_link_class)
            # for each_link in each_team_link_class_list:
            #     print(f"Checking link list: {each_link}...")
            #     all_links = self.driver.find_elements(By.CLASS_NAME, each_link)
            #     if len(all_links) > 0:
            #         break
            # print(f"Milestone:: > all links : {len(all_links)}")

            # # scan the links to select link for football only for the team
            # for link in all_links:
            #     # get the game: football, clrcket...
            #     game = link.find_element(By.CLASS_NAME, game_confirmation_class).text
            #     print(f"gametextfound: {game} -- sport: {self.sport}")
            #     # filter out only football link
            #     if str(game).lower() == self.sport.lower():
            #         print("[]milestone! requried game found!")
            #         # extract the href which is requried
            #         team_url = link.get_attribute('href')
            #         print(f"Team URL: {team_url}")
            #         return team_url, errorMessage

            # scan the links to select link for football only for the team
            # This scan for only 5 intems in the search list after team has been clicke
            # the first link in the list is usually the required link
            print(f"[DEBUT] Trying to get team link...")
            for x in range(1, 5, 1):
                # declare known xpath
                element = f'//*[@id="__next"]/header/div[1]/div/div/div[2]/div/div/div[2]/div[1]/div/div[{x}]/a'
                try:
                    link = self.driver.find_element(By.XPATH, element)
                    # print(f"ACTUAL LINK FOUND @ {element}")
                    # break
                except:
                    print(f">>> checking next one...")
                    continue

                # game = link.find_element(By.CSS_SELECTOR, game_confirmation_class).text
                try:
                    game = link.find_element(By.XPATH, game_confirmation_xpath).text
                except:
                    game = link.find_element(By.XPATH, game_confirmation_xpath1).text

                # print(f"gametextfound: {game} -- sport: {self.sport}")
                # filter out only football link
                if str(game).lower() == self.sport.lower():
                    # print("[]milestone! requried game found!")
                    # extract the href which is requried
                    team_url = link.get_attribute('href')
                    print(f"Team URL: {team_url}")
                    return team_url, errorMessage

            return None, "Possibly the Xpath provided is no longer valid"
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

        # suggested_data_table_class = ""
        # suggested_ha_class = ""
        rating_xpath = '//*[@id="__next"]/main/div[2]/div/div[2]/div[2]/div[3]/div[3]/div[1]/div[2]/span/div'
        ranking_xpath = '//*[@id="__next"]/main/div[2]/div/div[2]/div[2]/div[3]/div[3]/div[1]/div[1]/div[2]'

        def get_rating():
            try:
                rate = self.driver.find_element(By.XPATH, rating_xpath)
                return rate.text
            except Exception as e:
                # print(f"[x] Rating error {e}")
                return 0

        def get_ranking():
            try:
                rank = self.driver.find_element(By.XPATH, ranking_xpath)
                rank = rank.text
                rankList = str(rank).split("/")
                actual_rank = rankList[0].split(" ")[-1].strip()
                total_ranked = rankList[1].split(" ")[0].strip()

                return f"{actual_rank}/{total_ranked}"
            except Exception as e:
                # print(f"[x] Ranking Error: {e}")
                return 0

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

                # extract the required data from the holder
                home = ha[4].text
                away = ha[5].text
                home_score = ha[6].text
                away_score = ha[8].text
                wld = ha[10].text
                rating = get_rating()
                ranking = get_ranking()
                print(f"[][][] >>> {team}> Rating : {rating} - Ranking: {ranking}")

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
                continue

        # returned compiled final game data
        return gameData
        pass

    def extract_basketball_data(self, team):
        gameData = []   # stores final game data

        # declare classes required for extraction
        data_table_class_list = ["div.js-list-cell-target", "div.sc-fqkvVR.fZdvTU div.sc-fqkvVR.iGqHmj a.sc-631ef08b-0"]

        ha_class_list = ["sc-gFqAkR", "Text"]

        suitable_data_table_class = self.find_suitable_class_name(data_table_class_list, False)     # using CSS
        if suitable_data_table_class is None:
            print(f"[DEBUG][ERROR!] NO SUITABLE CLASS NAME FOUND FOR [DATA TABLE CLASS] - REPRESENTING EACH ROW IN THE TABLE\n"
                  f"UPDATE THE DATA_TABLE_CLASS_LIST WITH NEW CLASS NAME")
            raise Exception
        else:
            print(f"[DEBUG] suitable data class name found @ {suitable_data_table_class}")

        # get the whole table containing all the data
        table = self.driver.find_elements(By.CSS_SELECTOR, suitable_data_table_class)
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

                # extract the required data from the holder
                home = ha[4].text
                away = ha[5].text
                home_Q1_score= ha[6].text
                home_Q2_score= ha[8].text
                home_Q3_score= ha[10].text
                home_Q4_score= ha[12].text
                home_Q5_score= ha[14].text
                away_Q1_score= ha[16].text
                away_Q2_score= ha[18].text
                away_Q3_score= ha[20].text
                away_Q4_score= ha[22].text
                away_Q5_score= ha[24].text
                home_score = ha[26].text
                away_score = ha[28].text
                wld = ha[30].text

                # create a dictionary of the extracted data
                singleGameData['league'] = "my league"
                singleGameData['team'] = team
                singleGameData['home'] = home
                singleGameData['away'] = away
                singleGameData['home_Q1_score'] = 0 if home_Q1_score=="" else home_Q1_score
                singleGameData['home_Q2_score'] = 0 if home_Q2_score=="" else home_Q2_score
                singleGameData['home_Q3_score'] = 0 if home_Q3_score=="" else home_Q3_score
                singleGameData['home_Q4_score'] = 0 if home_Q4_score=="" else home_Q4_score
                singleGameData['home_Q5_score'] = 0 if home_Q5_score=="" else home_Q5_score
                singleGameData['away_Q1_score'] = 0 if away_Q1_score=="" else away_Q1_score
                singleGameData['away_Q2_score'] = 0 if away_Q2_score=="" else away_Q2_score
                singleGameData['away_Q3_score'] = 0 if away_Q3_score=="" else away_Q3_score
                singleGameData['away_Q4_score'] = 0 if away_Q4_score=="" else away_Q4_score
                singleGameData['away_Q5_score'] = 0 if away_Q5_score=="" else away_Q5_score
                singleGameData['home_score'] = 0 if home_score=="" else home_score
                singleGameData['away_score'] = 0 if away_score=="" else away_score
                singleGameData['status'] = wld

                # append it to the final game data
                gameData.append(str(singleGameData))

            except Exception as e:
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
        elif selector == 'xpath':
            try:
                input_element = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.XPATH, selector_name))
                )
                return True
            except:
                return False

    def start_data_extraction_old(self, team_names: list):
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
                    print("[DEBUG] Getting team's href ")
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

                print("[DEBUG] Saving Data")

                self.save_to_excel(game_data)

                self.new_team_name.append(eval(game_data[0])['team'] )
            return self.new_team_name
            pass
        except Exception as e:
            if failure_count > 0:
                return None
            print(f"[DEBUG] An Error occurred in start data extraction: {e}")

    def get_search_handle_by_xpath(self):
        print("[DEBUG] scanning for search handle...")
        for x in range(10):
            for y in range(10):
                try:
                    element = f'//*[@id="__next"]/header/div[{x}]/div/div/div[{y}]/div/form/input'
                    print(f"\r[{x},{y}]checking {element}", end="")
                    input_element = WebDriverWait(self.driver, 0.2).until(
                        EC.visibility_of_element_located((By.XPATH, element))
                    )
                    print()
                    print(f'FOUND!@ |{x},{y}')
                    self.save_to_config(self.section, 'searchTextboxHandle', element)
                    return element
                except:
                    continue
        return None




    def start_data_extraction(self, team_names: list):
        failure_count = 0
        try:
            self.new_team_name.clear()

            # check if page is properly loaded by checking if search box is on page
            # --------------------------------------------------------------------

            print('looking for search handle')
            if self.search_textbox_handle is None:
                self.search_textbox_handle = self.get_search_handle_by_xpath()
                # if self.search_textbox_handle is not None:
                #     self.save_to_config(self.section, 'searchTextboxHandle', self.search_textbox_handle)



            # input("milestone")
            # while True:
            #     op = None
            #     # checking all known class for search box
            #     for element in self.search_textbox_class_list:
            #         print(f"[][][][]Finding Search class [{element}].....")
            #         # on_page = self.is_element_on_page(self.search_textbox_class)
            #         on_page = self.is_element_on_page(element)
            #         if on_page is True:
            #             self.search_textbox_class = element
            #             print(f"[][][] Found! @ {self.search_textbox_class}")
            #
            #             op = True
            #             break
            #
            #     if op is True:
            #         break
            #     else:
            #         print("[DEBUG][ERROR] [using search box]Page not properly loaded! Refreshing to retry....")
            #         self.driver.refresh()
            #         time.sleep(5)
            #

            # 2. LOOP THROUGH ALL THE TEAMS
            # ----------------------------
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
                        self.search_textbox_handle = self.get_search_handle_by_xpath()
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
                            if failure_count >= 5:
                                return None
                            failure_count += 1
                            print(f"[DEBUG][ERROR] Team url Page [{team_url}] not properly loaded! DATA TABLE NOT FOUND ON PAGE! Refreshing to retry....")
                            self.driver.refresh()
                            time.sleep(5)
                    else:
                        if failure_count >= 5:
                            return None
                        failure_count += 1
                        print(f"[DEBUG][ERROR] Error Loading team's url [{team_url}]! Retrying")
                        time.sleep(2)

                failure_count = 0
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


                if self.sport == 'football':
                    game_data = self.extract_football_data(team_name)
                elif self.sport == 'basketball':
                    self.driver.maximize_window()
                    game_data = self.extract_basketball_data(team_name)


                print("[DEBUG] Saving Data")

                self.save_to_excel(game_data)

                self.new_team_name.append(eval(game_data[0])['team'] )
            return self.new_team_name
            pass
        except Exception as e:
            if failure_count > 0:
                return None
            print(f"[DEBUG] An Error occurred in start data extraction: {e}")








