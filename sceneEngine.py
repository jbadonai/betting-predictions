from PyQt5 import QtCore
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
from PIL import Image
import winsound
import threading


class SceneEngine():

    def __init__(self, display_screen: object, skip_button: object, stat_url: str, screen_number, myParent=None):
        self.url = stat_url  # statistic url to extract data from
        self.screen_number = screen_number   # holds the scene window value 1,2,3, or 4
        self.task_initiated = False     # track if task has been given to this scene engine
        self.busy = False   # tracks that the engine is working
        self.skip = False   # track if user click skip button to initiate going to next available stat

        # self.threadController = {}  # controls thread
        if myParent is not None:
            self.threadController = myParent.threadController  # controls thread
        else:
            self.threadController = {}

        self.display_screen = display_screen    # holds labels to display result

        self.teamA_oldValue = 0
        self.teamB_oldValue = 0

        self.start_engine()

        self.skip_button = skip_button
        self.skip_button.clicked.connect(self.skip_to_next)

    def run_function(self, functionName, join: bool = False, *args):
        try:
            t = threading.Thread(target=functionName, args=args)
            t.daemon = True
            t.start()
            if join:
                t.join()
        except Exception as e:
            print(f"An Error Occurred in [generalFunctions.py] > run_function(): {e}")

    def skip_to_next(self):
        try:
            self.skip = True
        except Exception as e:
            print(f"an error occurred in scene engine > skip : {e}")

    def set_display(self, value):

        self.display_screen.setText(str(value))

    def calculate_service_win_probability(self, win_1st_serve, win_2nd_serve, break_point_save):
        p_win_1st_serve = win_1st_serve / 100
        p_win_2nd_serve = win_2nd_serve / 100
        p_break_point_save = break_point_save / 100

        p_win = p_win_1st_serve + (1 - p_win_1st_serve) * p_win_2nd_serve * p_break_point_save

        return p_win

    def calculate_service_win_probability2(self, win_1st_serve, win_2nd_serve, opp_break_point_save):
        a1 = win_1st_serve + win_2nd_serve
        a2 = a1 - opp_break_point_save
        # print(f"1:{a1} - 2; {a2}")

        return a1, a2

    def make_beeps(self, num_beeps=3, freq=1000, duration=100):
        for _ in range(num_beeps):
            # Beep with a frequency of 1000 Hz and duration of 100 milliseconds
            winsound.Beep(freq, duration)
            time.sleep(0.5)

    def start_engine(self):
        self.set_display(f"[Engine {self.screen_number}] Starting ...")

        def engine_connector(data):
            try:
                game_data = data['data']
                error = data['error']
                players = data['players']
                message = data['message']
                player_details = None
                result = None
                # print(f"Engine{self.screen_number}: {message}")
                # print(f"SceneEngine Data: {data}")

                player1 = "Team A"
                player2 = "Team B"

                # get team's Name
                # ----------------
                players_dict = {}
                if str(players).lower().__contains__('loading') is False:

                    # checking if player data obtained
                    if str(players).lower().__contains__("{"):
                        players_dict = eval(players)
                    else:
                        self.set_display(players)

                else:
                    self.set_display(message)

                    # new_line_count = str(players).count('\n')
                    # dash_count = str(players).count('-')
                    #
                    # if new_line_count > 0 and dash_count > 0:
                    #     print(f"inspecting players: {players}")
                    #
                    #     details = eval(players)
                    #     print()
                    #     print(f"details:\n {details}")
                    #     print()
                    #
                    #     # details = {"league": league,
                    #     #            'player1': players[0].text,
                    #     #            'player2': players[1].text,
                    #     #            'player1_score': player1_score,
                    #     #            'player2_score': player2_score,
                    #     #            "current_set": current_set}
                    #
                    #     # if new_line_count == 2:
                    #     #     player1 = str(players).split("\n")[-1].split("vs")[0].strip()
                    #     #     player2 = str(players).split("\n")[-1].split("vs")[1].strip()
                    #     #
                    #     #     # set players name on the main window
                    #     #     header, body = str(players).split("\n")
                    #     #     p1, p2 = str(body).split("vs")
                    #     #     player_details = f"{header}\n{p1}\n{p2}"
                    #     #     # self.mainWindow.label_players.setText(player_details)
                    #     #
                    #     # if new_line_count == 4:
                    #     #     # print(str(players).split("\n"))
                    #     #     split = str(players).split("\n")
                    #     #     player1 = f'{split[1].strip()} {str()} {split[2].split("vs")[0].strip()} '
                    #     #     player2 = f'{split[2].split("vs")[1].strip()} {split[3].strip()} {str()} '
                    #     #
                    #     #     # set players name on the main window
                    #     #     player_details = f"{split[0].strip()}\n{player1}\n{player2}"
                    #     #     # self.mainWindow.label_players.setText(player_details)
                # get prediction based on data
                if len(game_data) > 1:
                    # Extract the required data
                    # ---------------------------------
                    if len(game_data) > 1:
                        # print(f"Tennis Data: {tennis_data}")

                        a1 = int(game_data['1st serve points won'][0].replace("%", ""))
                        a2 = int(game_data['2nd serve points won'][0].replace("%", ""))
                        ab = int(game_data['Break points saved'][0].replace("%", ""))

                        b1 = int(game_data['1st serve points won'][1].replace("%", ""))
                        b2 = int(game_data['2nd serve points won'][1].replace("%", ""))
                        bb = int(game_data['Break points saved'][1].replace("%", ""))

                        team_a_statistics = {'win_1st_serve': a1, 'win_2nd_serve': a2, 'break_point_save': ab}
                        team_b_statistics = {'win_1st_serve': b1, 'win_2nd_serve': b2, 'break_point_save': bb}

                        method = 2

                        if method == 1:
                            # Calculate probabilities for each team
                            p_win_team_a = self.calculate_service_win_probability(**team_a_statistics)
                            p_win_team_b = self.calculate_service_win_probability(**team_b_statistics)

                            teamA = p_win_team_a * 100
                            teamB = p_win_team_b * 100
                        elif method == 2:
                            # Calculate probabilities for each team
                            p_win_team_a = self.calculate_service_win_probability2(team_a_statistics['win_1st_serve'],
                                                                                   team_a_statistics['win_2nd_serve'],
                                                                                   team_b_statistics[
                                                                                       'break_point_save'])
                            p_win_team_b = self.calculate_service_win_probability2(team_b_statistics['win_1st_serve'],
                                                                                   team_b_statistics['win_2nd_serve'],
                                                                                   team_a_statistics[
                                                                                       'break_point_save'])

                            ta = p_win_team_a[0] + p_win_team_a[1]
                            tb = p_win_team_b[0] + p_win_team_b[1]
                            total = tb + tb

                            teamA = (ta / max(total, 1)) * 100
                            teamB = (tb / max(total, 1)) * 100
                            # print(f"ta={ta}, tb={tb}, total={total}, Pa={teamA}, Pb={teamB}")
                            if teamA + teamB > 100 or teamA + teamB < 100:
                                ateamA = (teamA / max((teamA + teamB), 1)) * 100
                                ateamB = (teamB / max((teamA + teamB), 1)) * 100
                                # print(f"Adjusted percentage: ta={ateamA}, tb={ateamB}, total={ateamA + ateamB}")

                                teamA = ateamA
                                teamB = ateamB

                        # print(f"teamA: {teamA} --{self.teamA_oldValue}")
                        # print(f"teamB: {teamB} -- {self.teamB_oldValue}")
                            # input("waiting....")

                        # Trying to perform these action only if the value from the thread changed
                        if self.teamA_oldValue != teamA or self.teamB_oldValue != teamB:
                            # if value has changed, update the old value with the new one
                            self.teamA_oldValue = teamA
                            self.teamB_oldValue = teamB

                            # if (teamA >= 80 or teamB >= 80) and abs(teamA - teamB) > 20:
                            # check if the game can be played
                            if (teamA > 0 and teamB > 0) :
                                # self.make_beeps(4)
                                self.run_function(self.make_beeps,False, 4)
                                # disable auto navigate to prevent navigation automatically
                            else:
                                print(f"[Engine {self.screen_number}] No Statistics! Re checking..")
                                time.sleep(1)
                                # self.make_beeps(1, 3000)
                                self.run_function(self.make_beeps, False, 1, 3000)


                            # Print the results
                #             result = f"""{player1}: {round(teamA, 2)}"
                # {player2}: {round(teamB, 2)}"""
                #             print(f"Printing result: {result}")

                            league = players_dict['league']
                            player1 = players_dict['player1']
                            player2 = players_dict['player2']
                            player1_score = players_dict['player1_score']
                            player2_score = players_dict['player2_score']
                            current_set = players_dict['current_set']
                            player1_prediction = round(teamA, 2)
                            player2_prediction = round(teamB, 2)

                            result = f"""
League  : {league}
Current Set  : {current_set}
{player1} : [ {player1_score} ]  [ {player1_prediction}% ]
{player2} : [ {player2_score} ]  [ {player2_prediction}% ]
                            """

                            self.set_display(result)

                        else:
                            # print("No new value detected!!!!!!!!!!")
                            # if the value has not changed do nothing
                            # self.make_beeps(1)
                            pass
                else:
                    self.set_display(message)

                # if player_details is not None:
                #     print('--------------------------------------------------------')
                #     print(f"player details: \n {player_details}")
                #     print('--------------------------------------------------------')
                # if result is not None:
                #     print('................................................................')
                #     print(f"result: \n {result}")
                #     print('................................................................')



            except Exception as e:
                print(f"An error occurred in Scene Engine > start Engine > engine_connector: {e}")

        try:
            self.threadController['scene_engine'] = SceneEngineThread(stat_url=self.url, threadParent=self)
            self.threadController['scene_engine'].start()
            self.threadController['scene_engine'].any_signal.connect(engine_connector)
            self.busy = True

            # input('wait2')
        except Exception as e:
            print(f"An error occurred in scene engine > start engine : {e}")

    def stop(self):
        try:
            self.threadController['scene_engine'].stop()
            pass
        except Exception as e:
            print(f"An Error occurred in Scene Engine > stop engine: {e}")

    def reset_to_default(self):
        try:
            self.stop()

            self.url = None
            self.task_initiated = False
            self.busy = False
            self.skip = False
            self.threadController = {}
            self.display_screen.setText(f"Screen {self.screen_number}")

        except Exception as e:
            print(f"An Error occured in scene Engine > reset to default: {e}")


class SceneEngineThread(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(dict)

    def __init__(self, stat_url, threadParent = None):
        super(SceneEngineThread, self).__init__()
        self.data_to_emit = {}
        self.data_to_emit['error'] = ""
        self.data_to_emit['players'] = "Scanning Games. Please wait..."
        self.data_to_emit['status'] = ''
        self.data_to_emit['message'] = ''
        self.data_to_emit['total_statistics'] = 0
        self.data_to_emit['data'] = {}
        self.url = stat_url
        self.driver = None
        self.thread_parent = threadParent

        self.message = ""
        self.debug = False



    def initialize_web(self):
        try:
            self.message = "Initializing Browser..."
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)

            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run Chrome in headless mode

            self.driver = webdriver.Chrome(options=chrome_options)

        except Exception as e:
            if self.debug is True:
                print(f"[Debug][ERROR] An Error occurred in SceneEngineThread > Initialize web: {e}")
            print(f"An error occurred in SceneEngineThread: initiailze_web: {e}")
            self.message = f"An Error Occurred!\n{e}"
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)

    def stop(self):
        self.requestInterruption()
        try:
            self.driver.quit()
            print(f"driver for Engine {self.thread_parent.screen_number} successfully closed!")
        except:
            pass

    def goto_stat_url(self):
        try:
            self.message = "Loading statistics page..."

            self.data_to_emit['status'] = self.message
            self.data_to_emit['message'] = self.message
            self.any_signal.emit(self.data_to_emit)
            self.driver.get(self.url)
            time.sleep(5)
            return True
        except:
            return False
            pass

    def wait_for_statistics_button(self, driver):
        # Wait for the Statistics button to be visible
        WebDriverWait(driver, 500).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.dashboard-game-action-bar__group button[aria-label="Statistics"]')))
        # print('Done Waiting for statistics button on main page')

    def get_total_spans(self, driver):
        # Get the total number of spans and store it in a variable
        spans = driver.find_elements(By.CSS_SELECTOR, '.dashboard-game-action-bar__group')
        total_spans = len(spans)
        return total_spans

    def select_and_click_statistics_button(self, driver, position):
        # Get all the spans
        try:
            spans = driver.find_elements(By.CSS_SELECTOR, '.dashboard-game-action-bar__group')

            # Select the span at the specified position
            if position < len(spans):
                target_span = spans[position]

                # Check if the span has a Statistics button
                statistics_button = target_span.find_element(By.CSS_SELECTOR, 'button[aria-label="Statistics"]')
                if statistics_button:
                    # Click the Statistics button
                    statistics_button.click()
                    return True
                else:
                    print("Button not found")
                    return False
            else:
                print("Invalid position")
                return False
        except Exception as e:
            if str(e).__contains__('Unable to locate element'):
                print("Cannot Locate statistics button! Possibly Statistics is not available for current game")
                # self.take_screenshot(spans[position], f"spanERRor_{position}")
            return False
            pass

    def click_statistics_button(self, driver, at_position=1):
        try:
            # Wait for the statistics button to be present
            self.message = 'waiting for statistics button....'
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)

            # WAIT FOR STATISTICS BUTTON TO APPEAR
            # --------------------------------------
            self.wait_for_statistics_button(driver)

            # get the total spans. Each span has several buttons including the statistics button.
            # ----------------------------------------------------------------------------------
            total_spans_group = self.get_total_spans(driver)

            # get the total statistics (i.e. no of games) available  and push to main window
            # print(f"total spans: {total_spans_group} <> current position: {at_position}")
            self.data_to_emit['total_statistics'] = total_spans_group
            self.any_signal.emit(self.data_to_emit)

            # CLICKING THE STATISTICS BUTTON
            ans = self.select_and_click_statistics_button(driver, at_position)
            if ans is True:
                return True
            else:
                return False
        except Exception as e:
            print(f"An Error occurred in click statistics button function: {e}")
            return False
            pass

    def take_screenshot(self, element_to_capture, savename):
        # Find the element you want to capture (replace this with the appropriate locator)
        # element_to_capture = driver.find_element(By.XPATH, xpath)

        # Get the location and size of the element
        # location = element_to_capture.location
        # size = element_to_capture.size

        # Take a screenshot of the entire page
        element_to_capture.screenshot(f"{savename}.png")

    def scroll_to_element(self, driver, element):
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def extract_data(self, driver):
        """
        * Get data
        * Get players' name and current set
        * once data is obtained, close the pop up
        * switch back to the main window.

        """
        try:
            self.push_message("Waiting for statistics page to fully load...")
            if self.debug is True:
                print("[Debug] Waiting for statistics page to  fully load...")

            # waiting for statistics page to load
            self.message = "Waiting for statistics page to fully load..."
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)

            # This loop is just to wait for pop up page to be fully loaded
            # ------------------------------------------------------
            counter = 0
            while True:
                if self.isInterruptionRequested() is True:
                    if self.debug is True:
                        print("[Debug][Exit Thread]Exiting by Interrupting Thread @ Waiting for popup page to be fully loaded...")
                    raise Exception

                if self.thread_parent.skip is True:
                    return True

                time.sleep(1)
                counter += 1
                title = self.driver.title
                if 'bookmaker' not in str(title).lower() and 'site' not in str(title).lower():
                    counting = str(title).count("-")
                    if counting > 0:
                        break
                else:
                    self.push_message(f"[{counter}] Waiting for statistics page to be fully loaded...")
                    if self.debug is True:
                        print(f"\r[Debug][{counter}] Waiting for statistics page to be fully loaded...", end="")
                    self.message = f"\r[{counter}]Waiting for page to fully load ..."
                    self.data_to_emit['status'] = self.message
                    self.any_signal.emit(self.data_to_emit)
                    if counter > 15:
                        counter = 1
                        self.driver.refresh()
                    time.sleep(1)


            self.push_message("Page fully loaded...")
            if self.debug is True:
                print("[Debug] Page fully loaded!")
            self.message = "Page fully loaded!"
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)

            time.sleep(2)
            self.push_message("Looking for data in frames...")
            if self.debug is True:
                print("[Debug] Looking for data in frames...")

            # Check each frames, and search for required Data continuously
            # # ---------------------------------------------.
            dataCounter = 0
            in_right_frame = False
            while True:
                if self.isInterruptionRequested() is True:
                    if self.debug is True:
                        print("[Debug][EXIT Thread] Exiting by interrupting thread @ scanning frames for data.")
                    raise Exception
                if self.thread_parent.skip is True:
                    return True

                time.sleep(1)
                # Get all the frames on the page
                # ------------------------------
                frames = self.driver.find_elements(By.TAG_NAME, 'iframe')
                num_frames = len(frames)  # count all the frames
                # print(f"No of frames found: {num_frames}")
                if num_frames == 0:
                    self.push_message("No Frame found! Refreshing page...")
                    if self.debug is True:
                        print("[Debug] No Frame found! Refreshing page...")
                    self.driver.refresh()
                    time.sleep(2)
                    continue

                time.sleep(1)

                # Scan through all frames to see the one that has the element required
                # -------------------------------------------------------------------
                self.push_message("Searching for Data...")
                if self.debug is True:
                    print("[Debug]Looking for required element in all available Frames...")

                for i in range(num_frames):
                    # Switch to the i-th frame
                    if self.thread_parent.skip is True:
                        return True

                    if num_frames == 1:
                        self.driver.switch_to.frame(0)
                    else:
                        if in_right_frame is False:
                            self.driver.switch_to.frame(i)
                    try:
                        # Search for the element within the frame
                        # element_to_search = self.driver.find_element(By.CLASS_NAME, "match-stat-table")
                        if self.debug is True:
                            print("[Debug] Waiting for statistics table to be visible...")
                        try:
                            element_to_search = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located(
                                    (By.CLASS_NAME, "match-stat-table"))
                            )
                        except:
                            if self.debug is True:
                                print("[Debug] Statistics table not found on the page. Exiting extract_data()...")

                            raise NoSuchElementException

                        # after ensuring the element exists, access it
                        element_to_search = self.driver.find_element(By.CLASS_NAME, "match-stat-table")

                        if self.debug is True:
                            print("[Debug] Statistics table detected. Proceeding...")

                        def get_and_select_current_quarter(driver):
                            try:
                                # Wait for the buttons to be present in the DOM
                                buttons = WebDriverWait(driver, 500).until(
                                    EC.presence_of_all_elements_located(
                                        (By.CSS_SELECTOR, '.switch-line__group .switch-line__button'))
                                )

                                # Find the index of the button with text 'Match'
                                match_index = next(
                                    (i for i, button in enumerate(buttons) if button.text.strip().lower() == 'match'), None)

                                # If 'Match' button is found and there is a button before it, click the one before it
                                if match_index is not None and match_index > 0:
                                    # Find the button just before the 'Match' button
                                    # if self.mainWindow.use_match_data is True:
                                    #     button_to_click = buttons[match_index]
                                    # else:
                                    #     button_to_click = buttons[match_index - 1]

                                    button_to_click = buttons[match_index - 1]

                                    # Get the text of the button to click and save it in a variable
                                    clicked_button_text = button_to_click.text.strip()

                                    # Click the button
                                    button_to_click.click()

                                    # Now, you can use the 'clicked_button_text' variable as needed
                                    # print("Clicked button text:", clicked_button_text)
                                    return clicked_button_text
                            except Exception as e:
                                print(f"An error occurred in get and select current quarter(): {e}")
                                return None

                        clicked_item_text = get_and_select_current_quarter(self.driver)

                        if clicked_item_text is None:
                            if self.debug is True:
                                print("[Debug] Could not find 'set'/'Quarter' link on the page. Exiting extract_data()...")
                            raise NoSuchElementException

                        # Get Scores
                        # ---------------------------
                        if self.thread_parent.skip is True:
                            return True
                        set, player1_score, player2_score = self.get_scores(self.driver)

                        # Get the players name
                        # --------------------
                        # print("Getting current players...")
                        league = self.get_league(self.driver)
                        players = self.driver.find_elements(By.CLASS_NAME, "old-member-info__names")
                        current_set = clicked_item_text

                        details ={"league": league,
                                  'player1': players[0].text,
                                  'player2': players[1].text,
                                  'player1_score': player1_score,
                                  'player2_score': player2_score,
                                  "current_set": current_set}

                        # players = f"[ {clicked_item_text} ] - {league}\n{players[0].text}:\t\t[ {player1_score} ] vs {players[1].text}:\t\t[ {player2_score} ]"
                        players = str(details)

                        # ------------------------------------------------
                        time.sleep(2)

                        # Get the content of statistics table as text/string
                        # -------------------------------------------------
                        rawData = element_to_search.text

                        # Process the string into dictionary and store in statistics
                        # --------------------------------------------------------
                        statistics = self.process_raw_data(rawData)
                        # print("statistics: ", statistics)

                        # Push the statistics in dictionary format to the main window
                        self.data_to_emit['players'] = players
                        self.data_to_emit['status'] = self.message
                        self.data_to_emit['data'] = statistics
                        self.any_signal.emit(self.data_to_emit)
                        in_right_frame = True

                    except Exception as e:
                        if self.isInterruptionRequested() is True:
                            return True
                        else:
                            if self.debug is True:
                                print(f"[Debug] [ERROR] Error in extract_data(): Exiting... {e}")
                            return False

                    except NoSuchElementException:
                        print(">>>>>>>>>>>     Match Statistics Table not found")
                        if self.debug is True:
                            print("[Debug] Match Statistics Table not found! in extract_data(). Exiting...")

                        return False

                # Push message that data has been received
                # ----------------------------------------
                self.push_message("Data Received...")
                self.message = f"Data Retrieved!"
                self.data_to_emit['status'] = self.message
                self.any_signal.emit(self.data_to_emit)
                time.sleep(2)
                print(f"[engine _ {self.thread_parent.screen_number}]Data received! cooling........")
                self.cooling(10)

        except Exception as e:
            print(f"An error occurred in extract_data(): {e}")
            return False

    def cooling(self, t: int = 5):
        try:
            for x in range(t, 0, -1):
                self.push_message(f"\r[Debug] Cooling {x}...")
                if self.debug is True:
                    print(f"\r[Debug] Cooling {x}...", end="")
                time.sleep(1)
        except Exception as e:
            print(f"An Error occurred in cooling: {e}")

    def get_scores(self, driver):
        # Extract the HTML source after the page is fully loaded
        html_source = driver.page_source

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(html_source, 'html.parser')

        # Find all rows in the table body
        table_body_rows = soup.select('table.table--score tbody tr')

        # Dictionary to store the extracted data
        data_dict = {}

        # Find the header of the last column
        last_column_header = soup.find('tr', class_='thead').find_all('td')[-1].text.strip()

        # Loop through rows and extract the last column
        for row in table_body_rows:
            # Extract the content of the last column for each row
            content = row.find_all('td')[-1].text.strip()

            # Check if header is already in the dictionary
            if last_column_header in data_dict:
                # Append the content to the existing tuple
                data_dict[last_column_header] += (content,)
            else:
                # Create a new tuple if header is not in the dictionary
                data_dict[last_column_header] = (content,)


        # Print the resulting dictionary
        # print(data_dict[last_column_header])
        return data_dict[last_column_header]

    def get_league(self, driver):
        # getting league name from breadcrumbs
        # Find all list items within the specified class
        list_items = driver.find_elements(By.CLASS_NAME, 'new-breadcrumbs-item')

        # Extract and save the content of each list item
        contents = [item.text for item in list_items]

        # Print or use the variable 'contents' as needed
        # print("printing bread crump content:::")
        league = contents[1]
        # for content in contents:
        #     print(content)
        return league

    def process_raw_data(self, raw_data):
        processed_data = {}
        try:
            splitter = 3
            newData = str(raw_data).split("\n")
            # print(newData)
            # Loop through the list with a step of 3
            for i in range(0, len(newData), 3):
                # Get the current group of 3 elements
                data_group = newData[i:i + 3]
                stat = data_group[1]
                home = data_group[0]
                away = data_group[2]

                processed_data[stat] = (home, away)
            return processed_data

            pass
        except Exception as e:
            print(f"An Error Occurred in Process_raw_data: {e}")

    def get_data_from_web(self):
        try:
            self.push_message("Loading Statistics url")
            if self.debug is True:
                print("[Debug] Loading statistics url...")

            # LOAD THE STATISTICS PAGE
            # ------------------------------
            ans = self.goto_stat_url()

            # check if page is successfully loaded and no internet issue
            # ---------------------------------------------------
            if ans is True:
                # page sucessfully loaded
                # -------------------------
                self.push_message("Statistics found successfully")
                if self.debug is True:
                    print("[Debug] Statistics found successfully...")

                # this is a continuous loop until error occurred(False) and user breaks out of the loop(True)
                extract_result = self.extract_data(self.driver)

                if extract_result is True:
                    if self.thread_parent.skip is True:
                        return True
                    else:
                        print(f"IT IS FINISHED!")
                        self.data_to_emit['status'] = "Finished"
                        self.any_signal.emit(self.data_to_emit)
                        return True
                else:
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print(f"EXITED: no data to retrieve!")
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    return False

            else:
                # Page not successfully loaded
                # ---------------------------
                self.push_message("Error Loading statistics page. Retrying...")
                if self.debug is True:
                    print("[Debug][ERROR] Error loading statistics page. Retrying...")
                time.sleep(2)
                self.get_data_from_web()

        except Exception as e:
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            print(f"EXITED: due to error -> {e}")
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            if self.debug is True:
                print(f"[Debug][ERROR] Error occurred in SceneEngineThread > get_data_from_web(): {e}")
            return False

    def push_message(self, message):
        self.data_to_emit['message'] = message
        self.any_signal.emit(self.data_to_emit)
        pass

    def run(self):
        try:
            if self.isInterruptionRequested() is True:
                raise Exception

            while True:
                if self.isInterruptionRequested() is True:
                    break

                # wait for url to be available
                while True:
                    if self.isInterruptionRequested() is True:
                        break

                    if self.thread_parent.skip is True:
                        break

                    if self.thread_parent.url != "":
                        self.url = self.thread_parent.url
                        print(f"Engine {self.thread_parent.screen_number} now has url: {self.thread_parent.url}")

                        break
                    # else:
                    #     print("No Url")
                    time.sleep(5)

                # initialize web page
                self.push_message("Initializing web page...")
                if self.debug is True:
                    print("[Debug] Initializing web page...")
                self.initialize_web()

                # Get data from web
                self.push_message("Getting data from the web...")
                if self.debug is True:
                    print("[Debug] Getting data from the web...")

                ans = self.get_data_from_web()
                if ans is False or self.thread_parent.skip is True:
                    if self.thread_parent.skip is True:
                        print(f"[Engine {self.thread_parent.screen_number}]USER SKIPPING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    self.push_message("Process failed somewhere, Trying to skip..")
                    print("process failed somewhere, Tryin to skip to next")
                    self.driver.close()
                    self.thread_parent.url = ""
                    self.thread_parent.busy = False
                    self.thread_parent.skip = False
                    time.sleep(1)



        except Exception as e:
            pass
