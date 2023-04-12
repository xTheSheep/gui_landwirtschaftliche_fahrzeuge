import sys
import sqlite3
from ui_files import ressources_interface
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QDoubleValidator
from PyQt5 import QtSql


# screens
class Startscreen(QMainWindow):
    def __init__(self):
        super(Startscreen, self).__init__()
        loadUi("./ui_files/interface.ui", self)
        # set session data
        self.user = ''
        self.budget = 0
        # set initial session values
        self.stackedWidget.setCurrentIndex(0)
        self.pushButton_4.clicked.connect(self.login)
        self.pushButton.clicked.connect(self.register)
        self.searchitem_button.clicked.connect(self.refreshtable)
        # setup buttons sidebar buyer
        self.home_button.clicked.connect(lambda: self.updatepage_buyer(0))
        self.search_button.clicked.connect(lambda: self.updatepage_buyer(1))
        self.cart_button.clicked.connect(lambda: self.updatepage_buyer(2))
        self.logout_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        # setup buttons sidebar seller
        self.home_button_seller.clicked.connect(lambda: self.updatepage_seller(0))
        self.search_button_seller.clicked.connect(lambda: self.updatepage_seller(1))
        self.logout_button_seller.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        for n in range(10):
            self.search_layout.addWidget(ItemView('test', 120000))

        for n in range(10):
            temp = ItemView('test', 120000)
            self.layout_search_buyer.addWidget(temp)
            temp.addtochart(self.cart_buyer_layout)

    def refreshtable(self):

        self.clearlayout()

        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        query = 'SELECT * FROM bestand'
        cursor.execute(query)
        result = cursor.fetchall()

        #  NEXT: rework cart functionality, maybe put widgets in array? -> just push array items to layout

        for product in result:
            temp = ItemView(product[0], product[1], product[2], product[3], product[4], product[5])
            self.layout_search_buyer.addWidget(temp)
            temp.addtochart(self.cart_buyer_layout)

    def clearlayout(self):
        for i in reversed(range(self.layout_search_buyer.count())):
            self.layout_search_buyer.itemAt(i).widget().deleteLater()

    def updatepage_buyer(self, number):
        self.stackedWidget_mainapp.setCurrentIndex(number)

    def updatepage_seller(self, number):
        self.stackedWidget_mainapp_seller.setCurrentIndex(number)

    def login(self):
        user = self.input_username.text()
        password = self.input_password.text()
        if len(user) == 0 or len(password) == 0:
            self.hint_login_information.setText('Please fill out all fields.')

        else:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            query = 'SELECT password, budget, seller FROM users WHERE username =\'' + user + "\'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result is None:
                self.hint_login_information.setText('Invalid Data')
            elif result[0] == password and result[2] == 0:  # login as buyer
                self.user = user
                self.budget = result[1]
                self.welcome_label.setText(f'welcome back {user}'.upper())
                self.startpage_budget_label.setText(f'Budget {int(self.budget)} €')
                self.searchpage_budget_label.setText(f'Budget {int(self.budget)} €')
                self.stackedWidget.setCurrentIndex(1)  # switch to buyerpage
                self.hint_login_information.setText('')
                self.input_password.setText('')
                self.updatepage_buyer(0)
            elif result[0] == password and result[2] == 1:  # login as seller
                self.user = user
                self.budget = result[1]
                self.welcome_label.setText(f'welcome back {user}'.upper())
                self.stackedWidget.setCurrentIndex(2)  # switch to sellerpage
                self.input_password.setText('')
                self.updatepage_seller(0)
            else:
                self.hint_login_information.setText('Invalid Data')

    def register(self):
        registerwindow.show()


class CreateAccountDialog(QDialog):
    def __init__(self):
        super(CreateAccountDialog, self).__init__()
        loadUi("./ui_files/newaccountdialog.ui", self)
        self.input_budget.editingFinished.connect(self.validate)
        self.createAccount_button.clicked.connect(self.createaccount)

    def validate(self):
        rule = QDoubleValidator(1, 10000000000, 0)
        if rule.validate(self.input_budget.text(), 14)[0] == 2:
            pass
        else:
            self.input_budget.setText('')

    def createaccount(self):
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


class ItemView(QWidget):
    def __init__(self, hersteller='hersteller', typ='typ', ps='ps', kmh='kmh', preis='preis', baujahr='baujahr'):
        super(ItemView, self).__init__()
        loadUi("./ui_files/stockitem.ui", self)
        self.typ.setText(str(typ))
        self.hersteller.setText(str(hersteller))
        self.year.setText('Year:' + str(baujahr))
        self.ps.setText(str(ps) + 'PS')
        self.kmh.setText(str(kmh) + 'km/h')
        self.preis.setText('Price: ' + str(preis) + '€')

    def addtochart(self, layout):
        self.cart_button.clicked.connect(lambda: self.addselftochart(layout))

    def addselftochart(self, layout):
        layout.addWidget(self)


database = QtSql.QSqlDatabase.addDatabase('QSQLITE')
database.setDatabaseName("db.db")

# main
app = QApplication(sys.argv)
homescreen = Startscreen()
homescreen.show()
registerwindow = CreateAccountDialog()

try:
    sys.exit(app.exec_())
except:
    print("App wird beendet...")
