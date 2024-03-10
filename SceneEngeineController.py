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

from sceneEngine import SceneEngine


class SceneEngineController():
    def __init__(self, sport, mainWindow):
        self.sport = sport
        self.mainWindow = mainWindow

        self.url = f"https://paripesa.ng/en/live/{sport}"
        self.threadController = self.mainWindow.threadController
        self.stat_position = 0

    def initialize(self):
        try:
            # initializing the engines
            # self.threadController['engine1'] = SceneEngine(self.mainWindow.label_screen1, self.url, 1)
            # self.threadController['engine2'] = SceneEngine(self.mainWindow.label_screen2, self.url, 2)
            # self.threadController['engine3'] = SceneEngine(self.mainWindow.label_screen3, self.url, 3)
            # self.threadController['engine4'] = SceneEngine(self.mainWindow.label_screen4, self.url, 4)

            pass
        except Exception as e:
            print(f"An error occurred in ScenEngneController > initialize: {e}")

    def start_controller(self):

        def controller_connector(data):
            # print(f"Controller data: {data}")
            message = data['message']
            self.mainWindow.label_info.setText(message)
            pass

        try:
            self.threadController['controller_engine'] = SceneEngineControllerThread(self.url, self.threadController)
            self.threadController['controller_engine'].start()
            self.threadController['controller_engine'].any_signal.connect(controller_connector)

        except Exception as e:
            print(f"An error occurred in scene engine controller> start : {e}")
        pass

    def stop(self):
        pass


class SceneEngineControllerThread(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(dict)

    def __init__(self, main_url, threadController):
        super(SceneEngineControllerThread, self).__init__()
        self.data_to_emit = {}
        self.driver = None
        self.debug = False
        self.message = ""
        self.url = main_url
        self.stat_current_position = 0
        self.threadController = threadController
        pass

    def push_message(self, message):
        self.data_to_emit['message'] = message
        self.any_signal.emit(self.data_to_emit)
        pass


    def stop(self):
        self.requestInterruption()
        try:
            self.driver.quit()
        except:
            pass

    def initialize_web(self):
        try:
            self.message = "Initializing Browser..."
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)

            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run Chrome in headless mode

            self.driver = webdriver.Chrome(options=chrome_options)
            return True

        except Exception as e:
            if self.debug is True:
                print(f"[Debug][ERROR] An Error occurred in SceneEngineController > Initialize web: {e}")
            self.message = f"An Error Occurred!\n{e}"
            self.data_to_emit['status'] = self.message
            self.any_signal.emit(self.data_to_emit)
            return False

    def goto_sport_url(self):
        try:
            self.message = "Loading statistics page..."

            self.data_to_emit['status'] = self.message
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

    def get_stat_list(self):
        try:
            # initialize web browser
            # ------------------------
            self.push_message("Initializing web browser...")
            if self.debug is True:
                print("[DEBUG] Initializing web browser...")

            web_result = self.initialize_web()
            if web_result is False:
                raise Exception

            # goto sport url
            # -----------------------------
            self.push_message("Loading url...")
            if self.debug is True:
                print(f"[DEBUG] Loading url....")
            sport_result = self.goto_sport_url()
            if sport_result is False:
                raise Exception

            # Waiting for statistics button to be visible
            # -------------------------------------------
            self.push_message("Waiting for statistics button to be visible...")
            if self.debug is True:
                print("[DEBUG] Waiting for statistics button to be visible on page....")
            self.wait_for_statistics_button(self.driver)

            WebDriverWait(self.driver, 500).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.dashboard-game-action-bar__group')))

            # search for all the statistics button
            # -----------------------------------
            self.push_message("Getting all spans with statistics buton...")
            if self.debug is True:
                print("[DEBUG] Getting all spans with statistics button....")
            spans = self.driver.find_elements(By.CSS_SELECTOR, '.dashboard-game-action-bar__group')

            statList =[]

            counter = 0
            self.push_message("Looping through the spans to get viable stat...")
            if self.debug is True:
                print("[DEBUG] :Looping through the span list to get viable stat buttons....")

            for span in spans:
                try:
                    statistics_button = span.find_element(By.CSS_SELECTOR, 'button[aria-label="Statistics"]')
                except:
                    continue

                statistics_button.click()

                # def switch():
                # Switching...............
                main_window_handle = self.driver.current_window_handle

                new_window_handle = None

                # Wait for the popup window to open
                wait = WebDriverWait(self.driver, 5)
                wait.until(lambda driver: len(self.driver.window_handles) > 1)

                # Find the the popup window handle
                for window_handle in self.driver.window_handles:
                    if window_handle != main_window_handle:
                        new_window_handle = window_handle
                        break

                # switch to pop up window
                self.driver.switch_to.window(new_window_handle)
                time.sleep(1)

                # Retrieve the URL of the new window
                new_window_url = self.driver.current_url
                # print("URL of the new window:", new_window_url)
                statList.append(new_window_url)
                counter += 1
                # print(f"\r Total valid urls found = {counter}", end= "")
                self.push_message(f"\r Scanning for valid urls... |  Found = {counter}")
                if self.debug is True:
                    print(f"\r Scanning for valid urls... |  Found = {counter}", end="")

                self.driver.close()

                self.driver.switch_to.window(main_window_handle)
                # End switching

            print()
            self.push_message(f"Link Extraction completed! {len(statList)} links found!")
            if self.debug is True:
                print(f"[DEBUG] : Link Extraction completed! {len(statList)} links found!")

            self.driver.quit()
            return statList
        except Exception as e:
            print(f"An Error Occurred in SceneEngineControllerThread > get_stat_list : {e}")
        pass

    def run(self):
        try:
            if self.isInterruptionRequested() is True:
                raise Exception

            self.push_message("Getting the list of stat urls...")

            if self.debug is True:
                print("[DEBUG] Getting the list of stat urls....")

            stat_list_urls = self.get_stat_list()
            print(stat_list_urls)

            print("updating engines.......................")
            self.push_message("Updating Engines...")
            while True:
                if self.isInterruptionRequested() is True:
                    break

                if self.stat_current_position >= len(stat_list_urls):
                    # no more link to work with
                    break

                # looping through the engine for the screens
                for x in range(4):
                    if self.isInterruptionRequested() is True:
                        break

                    if self.stat_current_position >= len(stat_list_urls):
                        # no more link to work with
                        break

                    engine = f"engine{x+1}"
                    busy = self.threadController[engine].busy
                    screen_number = self.threadController[engine].screen_number
                    present_url = self.threadController[engine].url
                    # print(f"busy_{screen_number}: {busy}")

                    if busy is True and present_url == "":
                        # print(f"setting url for engine {screen_number}")
                        url = stat_list_urls[self.stat_current_position]
                        self.threadController[engine].url = url
                        self.stat_current_position += 1

                    if busy is False:
                        print(f"ACTIVATING ENGINE {screen_number} | url:{self.stat_current_position}  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        # print(f"Display screen: {self.threadController[engine].display_screen.objectName()}")
                        url = stat_list_urls[self.stat_current_position]

                        self.threadController[engine].url = url
                        self.threadController[engine].busy = True
                        self.stat_current_position += 1

                        # print("loading next")
                        time.sleep(5)

                time.sleep(10)

                pass

            if self.stat_current_position > len(stat_list_urls):
                # no more link to work with
                print("DONE WITH ALL LINKS! NO MORE LINK TO WORK WITH PRESS START OR RESTART")

        except Exception as e:
            print(f'an error occurred in SceneEngieneController: {e}')

