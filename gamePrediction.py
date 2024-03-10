from PyQt5.QtWidgets import QMainWindow, QApplication, QSizeGrip,QLineEdit,QPushButton, QDesktopWidget, \
    QMessageBox,QInputDialog, QVBoxLayout,  QSizePolicy, QGridLayout, QLabel, QProgressBar, QProgressDialog
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QBasicTimer
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from ui import games_
from sceneEngine import SceneEngine
from SceneEngeineController import SceneEngineController

restart = False


class Tennis(QMainWindow, games_.Ui_MainWindow):

    def __init__(self):
        super(Tennis, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.title = "[ JBA ] Game Winning Probability"
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 700, 500)  # Set initial size (you can adjust this)
        self.center()  # Center the application on the screen
        # -----------------------------------------------------------------
        self.button_start.clicked.connect(self.start)
        self.threadController = {}

    def center(self):
        # Get the screen geometry
        screen_geo = QDesktopWidget().screenGeometry()

        # Calculate the center point
        center_point = screen_geo.center()

        # Calculate the new position for the window
        new_position = center_point - self.rect().center()

        # Move the window to the new position
        self.move(new_position)

    def start(self):
        try:
            self.threadController['engine1'] = SceneEngine(self.label_screen1, self.button_skip1, "", 1)
            self.threadController['engine2'] = SceneEngine(self.label_screen2, self.button_skip2, "", 2)
            self.threadController['engine3'] = SceneEngine(self.label_screen3, self.button_skip3, "", 3)
            self.threadController['engine4'] = SceneEngine(self.label_screen4, self.button_skip4, "", 4)
        except Exception as e:
            print(e)

        # engine = SceneEngine(self.label_screen1, 'https://paripesa.ng/en/statisticpopup/game/4/65d9da5a0d8c0bfbf1323a8f/main', 1)
        # engine.start_engine()

        try:
            engine = SceneEngineController('tennis', self)
            engine.start_controller()
        except Exception as e:
            print(e)
        pass

    def closeEvent(self, a0):
        try:
            for item in self.threadController:
                try:
                    print(f"stopping {item}")
                    self.threadController[item].stop()
                    self.threadController[item].driver.quit()
                    print(f"\t\t{item} stopped successfully")
                    pass
                except:
                    continue
            pass
        except:
            pass


if __name__ == '__main__':
    def mains():
        app = QApplication([])
        app.setStyle('fusion')

        win = Tennis()
        win.show()
        app.exec_()

    while True:
        restart = False
        mains()
        if restart is False:
            break
