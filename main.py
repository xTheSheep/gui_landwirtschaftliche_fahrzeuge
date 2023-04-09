import sys
import sqlite3
from ui_files import ressources_interface
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5.QtGui import QDoubleValidator, QValidator


# screens
class Startscreen(QMainWindow):
    def __init__(self):
        super(Startscreen, self).__init__()
        loadUi("./ui_files/interface.ui", self)
        self.stackedWidget.setCurrentIndex(0)
        self.pushButton_4.clicked.connect(self.login)
        self.pushButton.clicked.connect(self.register)
        self.home_button.clicked.connect(lambda: self.updatepage(0))
        self.search_button.clicked.connect(lambda: self.updatepage(1))

    def updatepage(self, number):
        self.stackedWidget_mainapp.setCurrentIndex(number)

    def login(self):
        user = self.input_username.text()
        password = self.input_password.text()
        if len(user) == 0 or len(password) == 0:
            self.hint_login_information.setText('Please fill out all fields.')

        else:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            query = 'SELECT password, seller FROM users WHERE username =\'' + user + "\'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result is None:
                self.hint_login_information.setText('Invalid Data')
            elif result[0] == password and result[1] == 0:
                # set user information
                self.welcome_label.setText(f'welcome back {user}'.upper())
                self.stackedWidget.setCurrentIndex(1)  # switch to buyerpage
                self.hint_login_information.setText('')
            elif result[0] == password and result[1] == 1:
                self.welcome_label.setText(f'welcome back {user}'.upper())
                self.stackedWidget.setCurrentIndex(2)  # switch to sellerpage
                self.hint_login_information.setText('')
            else:
                self.hint_login_information.setText('Invalid Data')

    def register(self):
        registerwindow.show()


class CreateAccountDialog(QDialog):
    def __init__(self):
        super(CreateAccountDialog, self).__init__()
        loadUi("./ui_files/newaccountdialog.ui", self)
        self.input_budget.editingFinished.connect(self.validate)
        self.createAccount_button.clicked.connect(self.createAccount)

    def validate(self):
        rule = QDoubleValidator(1, 10000000000, 0)
        if rule.validate(self.input_budget.text(), 14)[0] == 2:
            pass
        else:
            self.input_budget.setText('')

    def createAccount(self):
        username = self.input_username.text()
        password = self.input_password.text()
        budget = self.input_budget.text()

        if len(username) == 0 or len(password) == 0 or len(budget) == 0:
            self.account_hint.setText('Please fill out ALL fields.')
        elif len(username) < 4:
            self.account_hint.setText('The username cant be shorter than 4')
        elif len(password) < 3:
            self.account_hint.setText('The password is too short')
        else:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            query = 'SELECT username FROM users WHERE username =\'' + username + "\'"
            cursor.execute(query)
            if cursor.fetchone() is None:
                user_info = [username, password, budget, 0]
                cursor.execute('INSERT INTO users (username, password, budget, seller) VALUES (?, ?, ?, ?)', user_info)
                db.commit()
                db.close()
                self.input_username.setText('')
                self.input_password.setText('')
                self.input_budget.setText('')
                self.account_hint.setText('Account has been created!')
            else:
                self.account_hint.setText('Username already exists')


# main
app = QApplication(sys.argv)
homescreen = Startscreen()
homescreen.show()
registerwindow = CreateAccountDialog()

try:
    sys.exit(app.exec_())
except:
    print("App wird beendet...")
