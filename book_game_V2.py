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


class BookGame:
    def __init__(self):
        # self.url = 'https://www.sportybet.com/ng/sport/football?time=24'
        self.url = 'https://www.sportybet.com/ng/sport/football'
        # self.url = 'https://www.sportybet.com/ng/sport/football?time=24'
        self.driver = None

        # self.initialize_browser()
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(30)
        self.current_page = 1
        self.dataListToBook = None

        pass

    def login_to_sportybet(self, driver, username, password):
        # driver = self.driver

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

            return driver

        finally:
            # Close the browser session
            pass

    def check_pagination_exists(self, current_driver):
        try:
            pagination = WebDriverWait(current_driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
            )
            return True
        except:
            return False

    def click_next_button(self, current_driver):
        try:
            # Wait for the span element to be clickable
            span_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".pageNum.icon-next"))
            )

            try:
                # check if disabled next icon is on page.
                span_element = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".pageNum.icon-next.icon-disabled"))
                )

                return False
            except:
                pass

            # print("span element found! Tring to click it")
            # Click the span element
            # print('Moving on to Next page...')
            span_element.click()
            return True
        except:
            print(">>> Next button not found or clickable")
            return False

    def goto_page_one(self, current_driver):
        try:
            # get all the leagues
            # print("Waiting to be ready....")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "match-league"))
            )

            # get all page numbers
            # check if disabled next icon is on page.
            page_numbers = self.driver.find_elements(By.CLASS_NAME, 'pageNum')
            # print(f"TOTAL PAGE NUMBERS: {len(page_numbers)}")

            page1_handle = None

            # get handle for page1
            for pageNumber in page_numbers:
                value = pageNumber.text
                # print(f"TEXT value: {value}")
                if str(value).strip() == "1":
                    page1_handle = pageNumber
                    break

            cname = None
            if page1_handle is not None:
                cname = page1_handle.get_attribute('class')

            if cname is not None:
                if str(cname).__contains__("selected"):
                    print("Already on page 1")
                else:
                    print("Navigating back to page 1...")
                    try:
                        page1_handle.click()
                    except:
                        print(f"Error clicking on page 1")
        except Exception as e:
            print(f">>> Next button not found or clickable!\n {e}")
            return False

    def get_current_page_number(self, current_driver):
        try:
            # get all the leagues
            # print("Waiting to be ready....")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "match-league"))
            )

            # get all page numbers
            # check if disabled next icon is on page.
            page_numbers = self.driver.find_elements(By.CLASS_NAME, 'pageNum')

            # get handle for page1
            for pageNumber in page_numbers:
                value = pageNumber.text
                cname = pageNumber.get_attribute('class')
                if str(cname).__contains__("selected"):
                    return value

            return "?"


        except Exception as e:
            print(f">>> Next button not found or clickable!\n {e}")
            return "?"

    def navigate_to_next_page(self):
        # for x range(1,5,1):
        # checking of multiple pages exists
        ans = self.check_pagination_exists(driver)
        if ans is False:
            print(f"No paginaton")
            return False
        else:
            # if there is pagination, click next
            ans2 = self.click_next_button(self.driver)
            if ans2 is False:
                return False

    def extract_required_info(self, dataList):
        begin = False
        dataGroup = []
        group = []
        home = None
        away = None
        game_code = None
        accuracy = 0
        game_time = None
        sporter_counter = 0
        extraData = []
        new_insight = ""

        for d in dataList:
            if d.__contains__("Game Time"):
                game_time = d.strip().split(" ")[8]
                begin = True

            if d.__contains__("*"):
                begin = False
                continue

            if d.__contains__("Filtered data for"):
                begin = False
                continue

            if begin is True:
                if d != "":
                    group.append(d)

                # extract home and away team
                if d.__contains__('Teams'):
                    home = d.split(":")[1].strip()
                    away = d.split(":")[2].strip()

                if d.__contains__("{"):
                    sporter_counter += 1
                    if sporter_counter == 1:
                        accuracy = d.split(" ")[-1].strip()
                    elif sporter_counter == 2:
                        game_code = d.split(" ")[-1].strip()
                        game_code = game_code.replace("[","").replace("]","")
                        sporter_counter = 0

                if d.__contains__("|"):
                    new_insight = "None"
                    # Prediction:     ['H', 'D', 'D', 'H', 'D'] | H, D, H, H, D
                    raw = d.split(":")[-1].strip()
                    homeCount = raw.count("H")
                    awayCount = raw.count("A")
                    drawCount = raw.count("D")

                    if homeCount > 0 and awayCount > 0 and drawCount > 0:
                        # i.e all of them has value pick(guess) the maximum and draw: subject to review
                        def max_variable_name(h, a, d):
                            # Create a dictionary to map values to their corresponding variable names
                            values = {'Home': h, 'Away': a, 'Draw': d}

                            # Find the maximum value
                            max_value = max(values.values())

                            # Find the corresponding key (variable name) for the maximum value
                            for key, value in values.items():
                                if value == max_value:
                                    return key

                        biggest = max_variable_name(homeCount, awayCount, drawCount)
                        if biggest != "Draw":
                            new_insight = f"{biggest} or Draw"
                        else:
                            new_insight = "[G]Home or Away"    # Guess
                    else:
                        def non_zero_keys(h, a, d):
                            # Create a dictionary to map values to their corresponding variable names
                            values = {'Home': h, 'Away': a, 'Draw': d}

                            # Filter out the keys with non-zero values
                            non_zero_keys = [key for key, value in values.items() if value > 0]

                            # Check the number of non-zero values and return the appropriate result
                            if len(non_zero_keys) == 1:
                                return non_zero_keys[0]
                            elif len(non_zero_keys) == 2:
                                return f"{non_zero_keys[0]} or {non_zero_keys[1]}"
                            else:
                                return None  # All three have non-zero values or all are zero

                        combination = non_zero_keys(homeCount, awayCount, drawCount)
                        if combination is not None:
                            if combination.__contains__("or"):
                                if combination.strip() == 'Away or Draw':
                                    new_insight = "Draw or Away"
                                else:
                                    new_insight = combination
                            else:
                                if str(combination).lower() == "home":
                                    new_insight = f"{combination} or Draw"
                                else:
                                    new_insight = f"Draw or {combination}"
                        else:
                            new_insight = "[G]Home or Away"    # Guess



            if begin is False:
                # if len(group) > 0:
                #     # apply filter
                #
                #     if str(group).__contains__(f"[{code}]"):
                #         x = "\n".join(group)
                #
                #         x += "\n\n\t\t\t\t***************************************************\n"
                #         dataGroup.append(x)

                if home is not None:
                    extraData.append((game_time, home, away, game_code, accuracy, new_insight))

                group.clear()
                home = None
                away = None
                accuracy = None
                game_code = None
                sporter_counter = 0

        return extraData
        pass

    def load_data_to_book(self, filename):
        path = f"{filename}"
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()

        # pre process data
        data = data.replace("<>","")
        dataList = data.split("\n")

        finalData = self.extract_required_info(dataList)

        return finalData

    def switch_to_double_chance(self, component):
        dc_class = 'market-item'
        allDC = component.find_elements(By.CLASS_NAME, dc_class)
        time.sleep(2)
        for dc in allDC:
            text = dc.text
            if text.strip() == 'Double Chance':
                dc.click()
                # print(f"Switching done")

                return True, component

        return False, component

    def is_in_booking_list(self, timeHandle, homeHandle, awayHandle):
        for data in self.dataListToBook:
            # print(data)
            # input('ms')
            t = data[0] # extract time
            h = data[1] # extrach home team
            a = data[2] # extract away team
            accuracy = str(data[4]).replace("[", "").replace("]", "")
            code = data[3]
            newInsight = data[5]

            # print("[][] ",data , "<><>", f"{timeHandle}--{homeHandle}--{awayHandle}")

            if t==timeHandle.strip() and h == homeHandle.strip() and a == awayHandle.strip():
                return True, code, accuracy, newInsight

        return False, None, None, None
        pass

    def start(self, booking_limit=50):
        print(f"Booking Limit: {booking_limit}")
        try:
            # LOAD DATA TO BOOK
            # load data list with serail date
            dataListToBook = self.load_data_to_book(f"fb_result.txt")
            self.dataListToBook = dataListToBook

            self.driver = self.login_to_sportybet(self.driver, '08022224284', "Afolayemi1")
            time.sleep(3)

            # 1. Goto webpage and load url
            self.driver.get(self.url)

            eachRowClass = 'm-table-row'
            match_league = "match-league"

            booking_list = []

            # Book all the game serially
            # -------------------------
            game_booked = 0     # used to control number of games in a booking

            # looping through all the game in the booking list
            for current_game in self.dataListToBook:
                self.goto_page_one(self.driver)

                print(f"\n[{game_booked + 1}/{booking_limit}]    Booking Game '{current_game}'")
                gameBookedSuccessfully = False

                currentTime = current_game[0]
                currentHome = current_game[1]
                currentAway = current_game[2]
                currentPrediction = current_game[5]

                # Search for game and book it, even if it involve searching through multiple pages
                # print()
                def manual_search(team):
                    text = self.driver.page_source

                    if text.__contains__(team):
                        return True
                    else:
                        return False
                    pass

                def custom_manual_search(team, parent_element):

                    # Get the HTML content of the league element
                    parent_html = parent_element.get_attribute('innerHTML')

                    # Check if the word "argentina" is present within the HTML content
                    if str(team).lower() in parent_html.lower():
                        return True
                    else:
                        return False
                    pass


                while True:
                    currentPage = self.get_current_page_number(self.driver)

                    if gameBookedSuccessfully is True:
                        # go back to page 1 to start searching for next game
                        break

                    print(f"\rScanning page {currentPage} for {currentHome} vs {currentAway}! Please wait...", end="")

                    try:
                        # get all the leagues
                        # print("Waiting to be ready....")
                        WebDriverWait(self.driver, 30).until(
                            EC.presence_of_element_located((By.CLASS_NAME, match_league))
                        )

                        print("\n\t[QUICK SEARCH]: Initiated")
                        a = manual_search(currentHome)
                        b = manual_search(currentAway)

                        if a is False and b is False:
                            print(f"\t[QUICK SEARCH]: Team not found on page {currentPage}! Checking next page__")
                            # closing.........
                            pagination_exists = self.check_pagination_exists(self.driver)
                            if pagination_exists is False:
                                # self.goto_page_one(self.driver)
                                break
                            else:
                                ans = self.click_next_button(self.driver)
                                if ans is False:
                                    break
                            continue
                        else:
                            print(f"\t[QUICK SEARCH]: Team on page! Scanning game handle...")

                        leagues = self.driver.find_elements(By.CLASS_NAME, match_league)


                        # looping through all the leagues in the current page
                        for league in leagues:

                            h = custom_manual_search(currentHome, league)
                            a = custom_manual_search(currentAway, league)

                            if h is False and a is False:
                                # print('Fast skip')
                                continue
                            # else:
                            #     print("Found here!")

                            try:
                                if gameBookedSuccessfully is True:
                                    # go back to page 1 to start searching for next game
                                    break

                                # a. switch to double chance
                                # --------------------------
                                switch_result, league = self.switch_to_double_chance(league)

                                if switch_result is False:
                                    raise Exception

                                # b. find all the rows in the league
                                # ----------------------------------
                                rows = league.find_elements(By.CLASS_NAME, eachRowClass)

                                # search through all the rows to get necessary handles
                                for row in rows:

                                    try:
                                        time_handle = row.find_element(By.CLASS_NAME, 'clock-time').text
                                        home_team_handle = row.find_element(By.CLASS_NAME, 'home-team').text
                                        away_team_handle = row.find_element(By.CLASS_NAME, 'away-team').text
                                        outcome_handle = row.find_elements(By.CLASS_NAME, 'm-outcome')
                                        hd_handle = outcome_handle[0]
                                        ha_handle = outcome_handle[1]
                                        ad_handle = outcome_handle[2]

                                        # Check if this row is the current game to book:
                                        if currentTime == time_handle.strip() and currentHome == home_team_handle.strip() and currentAway == away_team_handle.strip():
                                            if str(currentPrediction).lower().__contains__("home or draw"):
                                                cname = hd_handle.get_attribute('class')
                                                # print()
                                                # print(f"Class Name: {cname}")
                                                if str(cname).__contains__("disabled"):
                                                    print()
                                                    print(f"[X] Game is no longer available...")
                                                    gameBookedSuccessfully = True
                                                    pass
                                                else:
                                                    try:
                                                        hd_handle.click()
                                                        time.sleep(1)
                                                        game_booked += 1
                                                        gameBookedSuccessfully = True
                                                        print()
                                                        print(f"[] Game Booked Successfully...")
                                                    except Exception as e:
                                                        print(f"[Error] Game Booking Failed! {e}")
                                                        pass
                                            elif str(currentPrediction).lower().__contains__('draw or away') or str(currentPrediction).lower().__contains__('away or draw'):
                                                cname = ad_handle.get_attribute('class')
                                                # print()
                                                # print(f"Class Name: {cname}")
                                                if str(cname).__contains__("disabled"):
                                                    print()
                                                    print(f"[X] Game is no longer available...")
                                                    gameBookedSuccessfully = True
                                                    pass
                                                else:
                                                    try:
                                                        ad_handle.click()
                                                        time.sleep(1)
                                                        game_booked += 1
                                                        gameBookedSuccessfully = True
                                                        print()
                                                        print(f"[] Game Booked Successfully...")
                                                    except Exception as e:
                                                        print(f"[Error] Game Booking Failed! {e}")
                                                        pass

                                            elif str(currentPrediction).lower().__contains__("home or away") :
                                                cname = ha_handle.get_attribute('class')

                                                # print()
                                                # print(f"Class Name: {cname}")
                                                if str(cname).__contains__("disabled"):
                                                    print()
                                                    print(f"[X] Game is no longer available...")
                                                    gameBookedSuccessfully = True
                                                    pass
                                                else:
                                                    try:
                                                        ha_handle.click()
                                                        time.sleep(1)
                                                        game_booked += 1
                                                        gameBookedSuccessfully = True
                                                        print()
                                                        print(f"[] Game Booked Successfully...")
                                                    except Exception as e:
                                                        print(f"[Error] Game Booking Failed! {e}")
                                                        pass
                                            else:

                                                print()
                                                print(f"{currentHome} VS {currentAway}")
                                                print(f"Unknown prediction [{currentPrediction} |for| {currentHome} VS {currentAway}] but refused to take a guess. Skipping...")
                                                continue
                                            pass
                                        else:
                                            continue

                                        if game_booked >= booking_limit:
                                            game_booked = 0
                                            print()
                                            input("[*][*][*] BOOKING LIMIT REACHED! REACT AND PRESS ENTER TO CONTINUE! WAITING FOR YOU...")
                                        if gameBookedSuccessfully is True:
                                            break
                                    except:
                                        continue
                            except:
                                continue

                        # closing.........
                        pagination_exists = self.check_pagination_exists(self.driver)
                        if pagination_exists is False:
                            # self.goto_page_one(self.driver)
                            break
                        else:
                            ans = self.click_next_button(self.driver)
                            if ans is False:
                                break
                    except:
                        continue



            # input('wait')
            # looping through the pages if more than one to get all booking list

            print("Completed! Waiting for user input...")

            ans = input("press any key after completeing the booking process to exit browser")

            pass
        except Exception as e:
            # if switch_result is False:
            #     print("Fail to Switch to DOUBLE CHANCE")
            print(e)
            pass


bookingLimit = 5

test = BookGame()
test.start(booking_limit=bookingLimit)
