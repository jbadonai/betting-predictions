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
            print('Moving on to Next page...')
            span_element.click()
            return True
        except:
            print(">>> Next button not found or clickable")
            return False

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

                if d.__contains__("NEW:"):
                    new_insight = d.split("-")[-1].strip()


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
        path = f"filtered/{filename}"
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

    def start(self, date_to_book, specific=False, specific_value="500", booking_limit=40):
        print(f"date: {date_to_book}")
        print(f"date: {specific}")
        print(f"date: {specific_value}")
        print(f"date: {booking_limit}")
        try:
            # LOAD DATA TO BOOK
            '''
                ('18:00', 'Denmark', 'Sweden', '302')
                ('23:00', 'EC Juventude RS', 'AC Goianiense GO', '302')
                '''
            dataListToBook = self.load_data_to_book(f"filtered_{date_to_book}.txt")
            # dataListToBook = self.load_data_to_book(f"fb_result.txt")
            self.dataListToBook = dataListToBook

            self.driver = self.login_to_sportybet(self.driver, '08022224284', "Afolayemi1")
            time.sleep(3)
            # 1. Goto webpage and load url
            self.driver.get(self.url)

            # 2. swithc to double chance
            # switch_result = self.switch_to_double_chance()

            # if switch_result is False:
            #     raise Exception

            # 2. scan through the pages and capture all rows
            # a. check if there is pagination
            eachRowClass = 'm-table-row'
            match_league = "match-league"



            booking_list = []
            # looping through the pages if more than one to get all booking list
            game_booked = 0
            while True:
                try:
                    # get all the leagues
                    print("Waiting to be ready....")
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.CLASS_NAME, match_league))
                    )

                    leagues = self.driver.find_elements(By.CLASS_NAME, match_league)

                    # looping through all the leagues in the current page
                    for league in leagues:
                        try:
                            # a. switch to double chance
                            # --------------------------
                            switch_result, league = self.switch_to_double_chance(league)

                            if switch_result is False:
                                raise Exception

                            # b. find all the rows in the league
                            # ----------------------------------
                            rows = league.find_elements(By.CLASS_NAME, eachRowClass)
                            # print(f"Total Rows in league: {len(rows)}")

                            def submit():

                                # m-input fs-exclude
                                bat = "m-input.fs-exclude"
                                pbb = "af-button.af-button--primary"  # place bet button class
                                pbc = "af-button.af-button--primary"  # place bet confirm
                                ssb = "af-button.af-button--primary"

                                bet_amount_textbox = self.driver.find_element(By.CLASS_NAME, bat)

                                place_bet_button = self.driver.find_element(By.CLASS_NAME, pbb)


                                if bet_amount_textbox:
                                    time.sleep(1)
                                    # Click on the text box to focus it
                                    print("trying to clear amount textbox...")
                                    # Get the current value of the text box
                                    current_value = bet_amount_textbox.get_attribute("value")

                                    # Send backspace keys to delete the current value
                                    bet_amount_textbox.send_keys(Keys.BACKSPACE * len(current_value))
                                    print("Inseting N10 bet...")
                                    time.sleep(1)
                                    bet_amount_textbox.send_keys(10)
                                    time.sleep(1)
                                    print("clicking ok to place bet")
                                    place_bet_button.click()
                                    time.sleep(1)
                                    print("confirming bet...")
                                    try:
                                        place_bet_confirm_button = self.driver.find_element(By.CLASS_NAME, pbc)
                                        time.sleep(1)
                                        place_bet_confirm_button.click()
                                    except Exception as e:
                                        print(e)

                                    time.sleep(1)
                                    print("Confirming submission....")
                                    place_bet_confirm_button.click()
                                else:
                                    print("bet amount textbox not found!")

                            for row in rows:
                                try:
                                    time_handle = row.find_element(By.CLASS_NAME, 'clock-time').text
                                    home_team_handle = row.find_element(By.CLASS_NAME, 'home-team').text
                                    away_team_handle = row.find_element(By.CLASS_NAME, 'away-team').text
                                    outcome_handle = row.find_elements(By.CLASS_NAME, 'm-outcome')
                                    hd_handle = outcome_handle[0]
                                    ha_handle = outcome_handle[1]
                                    ad_handle = outcome_handle[2]

                                    hdList = ["104", "500", "302", '401', '212', '203']  # code for home or draw
                                    adList = ['041']  # code for away or draw
                                    haList = ["140", "311", "050", "320", '221', '410']

                                    hone_al = ['37', '34', '25', '20', '14']    # home accuracy list
                                    away_al = ['14', '13']    # away accuracy list
                                    draw_al = ['20', '18']    # draw accuracy list

                                    acc = {"500": {'hd': ['47','45','44'], 'ha': ['46', '43']},
                                           "050": ['46', '45', '44', '43']}

                                    excludeList = ["500", "050", "302","104", "320", "140", "311"]

                                    # SURE: 500, 302 AND 050

                                    # check if this data is in booking list:
                                    try:
                                        ans, code, accuracy, new_insight = self.is_in_booking_list(time_handle.strip(), home_team_handle.strip(), away_team_handle.strip())
                                    except Exception as e:
                                        print(f"ERROR: {e}")

                                    #   USING NEW INSIGHT AS PRIORITY
                                    # ---------------------------------------

                                    if str(new_insight).lower().__contains__("home or draw"):
                                        print(f"[] Taking decision based on new insight...")
                                        hd_handle.click()
                                        game_booked += 1
                                    elif str(new_insight).lower().__contains__('draw or away'):
                                        print(f"[] Taking decision based on new insight...")
                                        ad_handle.click()
                                        game_booked += 1
                                    elif str(new_insight).lower().__contains__("home or away"):
                                        print(f"[] Taking decision based on new insight...")
                                        ha_handle.click()
                                        game_booked += 1
                                    else:
                                        # print(f"{ans} -- {code} -- {accuracy}")
                                        if ans is True:
                                            # print(f"Ans: {ans} - {code}<>{specific_value}")
                                            if specific is False:
                                                # print(f"CODE: {code}")
                                                # booking all games except those in excluded list
                                                if str(code) in hdList and str(code) not in excludeList:   # 1x
                                                    print()
                                                    print(f"[OK] [{code}] [{home_team_handle} vs {away_team_handle}]")
                                                    hd_handle.click()
                                                    game_booked += 1
                                                elif str(code) in adList and str(code) not in excludeList:
                                                    print()
                                                    print(f"[OK] [{code}] [{home_team_handle} vs {away_team_handle}]")
                                                    ad_handle.click()
                                                    game_booked += 1
                                                elif str(code) in haList and str(code) not in excludeList:
                                                    print()
                                                    print(f"[OK] [{code}] [{home_team_handle} vs {away_team_handle}]")
                                                    ha_handle.click()
                                                    game_booked += 1
                                                else:
                                                    print("\r.", end="")
                                                    pass

                                            else:
                                                # booking only spcified code
                                                if str(code) in hdList and str(code) == specific_value:   # 1x
                                                    print()
                                                    print(f"[OK] [{code}] [{home_team_handle} vs {away_team_handle}]")
                                                    hd_handle.click()
                                                    game_booked += 1
                                                elif str(code) in adList and str(code) == specific_value:
                                                    print()
                                                    print(f"[OK] [{code}] [{home_team_handle} vs {away_team_handle}]")
                                                    ad_handle.click()
                                                    game_booked += 1
                                                elif str(code) in haList and str(code) == specific_value:
                                                    print()
                                                    print(f"[OK] [{code}] [{home_team_handle} vs {away_team_handle}]")
                                                    ha_handle.click()
                                                    game_booked += 1
                                                else:
                                                    print("\r.", end="")
                                                    pass

                                                # if game_booked >= booking_limit:
                                                #     game_booked = 0
                                                #     print()
                                                #     # submit()
                                                #
                                                #     input("[*][*][*] BOOKING LIMIT REACHED! REACT AND PRESS ENTER TO CONTINUE! WAITING FOR YOU...")
                                                #
                                        else:
                                            # print(f"\rNot Found! {home_team_handle} vs {away_team_handle}", end="")
                                            pass

                                    if game_booked >= booking_limit:
                                        game_booked = 0
                                        print()
                                        # submit()

                                        input(
                                            "[*][*][*] BOOKING LIMIT REACHED! REACT AND PRESS ENTER TO CONTINUE! WAITING FOR YOU...")

                                    # I can actually check if each of this is in the booking list and just book right here

                                except:
                                    continue
                        except:
                            continue

                    # closing.........
                    pagination_exists = self.check_pagination_exists(self.driver)
                    if pagination_exists is False:
                        break
                    else:
                        ans = self.click_next_button(self.driver)
                        if ans is False:
                            break
                except:
                    continue

            print("Completed! Waiting for user input...")

            ans = input("press any key after completeing the booking process to exit browser")

            pass
        except Exception as e:
            # if switch_result is False:
            #     print("Fail to Switch to DOUBLE CHANCE")
            print(e)
            pass

# excludeList = ["500", "050", "302","104", "320", "140", "311"]
excludeList = ["302","104", "320", "140", "311"]

mdate = 22
specific = False
bookingLimit = 5

if specific is True:
    for e in excludeList:
        print(f"Working on {e}")
        test = BookGame()
        test.start(date_to_book=mdate,
                   specific=True,
                   specific_value=e,
                   booking_limit=bookingLimit)
else:
    test = BookGame()
    test.start(date_to_book=mdate,
               specific=False,
               specific_value="500",
               booking_limit=bookingLimit)
