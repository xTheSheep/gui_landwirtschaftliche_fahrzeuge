import sys
import ressources_interface
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5.QtGui import QDoubleValidator, QValidator


# screens
class Startscreen(QMainWindow):
    def __init__(self):
        super(Startscreen, self).__init__()
        loadUi("interface.ui", self)
        self.stackedWidget.setCurrentIndex(0)
        self.pushButton_4.clicked.connect(self.login)
        self.pushButton.clicked.connect(self.register)
        self.home_button.clicked.connect(lambda: self.updatepage(0))
        self.search_button.clicked.connect(lambda: self.updatepage(1))

    def updatepage(self, number):
        self.stackedWidget_mainapp.setCurrentIndex(number)

    def login(self):
        if checklogin(self.input_username.text(), self.input_password.text()):
            self.stackedWidget.setCurrentIndex(1)  # switch to mainpage
            self.hint_login_information.setText('')
        else:
            self.hint_login_information.setText('Invalid Data')

    def register(self):
        registerwindow.show()


class CreateAccountDialog(QDialog):
    def __init__(self):
        super(CreateAccountDialog, self).__init__()
        loadUi("newaccountdialog.ui", self)
        self.input_budget.editingFinished.connect(self.validate)
        self.createAccount_button.clicked.connect(self.createAccount)
    def validate(self):
        rule = QDoubleValidator(1, 10000000000, 0)
        if rule.validate(self.input_budget.text(), 14)[0] == 2:
            pass
        else:
            self.input_budget.setText('')
    def createAccount(self):
        users.append({
            'username': self.input_username.text(),
            'password': self.input_password.text(),
            'budget': self.input_budget.text(),
        })
        self.account_hint.setText('Account has been created!')

# login data
def checklogin(username, password):
    for user in users:
        if username == user['username'] and password == user['password']:
            return True

users = [
    {'username': 'Oskar', 'password': '123', 'budget': 187},
    {'username': 'Benni', 'password': '123', 'budget': 187},
    {'username': 'Daniela', 'password': '123', 'budget': 187},
    {'username': 'Horst', 'password': '123', 'budget': 187},
    {'username': 'Sieglinde', 'password': '123', 'budget': 187},
]

# main
app = QApplication(sys.argv)
homescreen = Startscreen()
homescreen.show()
registerwindow = CreateAccountDialog()

try:
    sys.exit(app.exec_())
except:
    print("App wird beendet...")
