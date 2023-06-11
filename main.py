import sys
import sqlite3

from PyQt5.QtCore import QPoint, Qt
from ui_files import ressources_interface
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QLabel, QShortcut, QPushButton
from PyQt5.QtGui import QDoubleValidator, QPixmap, QPainter, QCursor, QIcon, QKeySequence


# screens
class Startscreen(QMainWindow):
    def __init__(self):
        super(Startscreen, self).__init__()
        loadUi("./ui_files/interface.ui", self)
        # set session data
        self.user = ''
        self.budget = 0
        self.cartsum = 0
        # set initial session values
        self.stackedWidget.setCurrentIndex(0)
        self.pushButton_4.clicked.connect(self.login)
        self.input_password.returnPressed.connect(self.login)
        self.pushButton.clicked.connect(self.register)
        self.searchitem_button.clicked.connect(self.refreshtable)
        self.searchitem_button_seller.clicked.connect(self.refreshtable)
        self.clear_button_buyer.clicked.connect(self.clearsearchfields)
        self.addtocart_button.clicked.connect(self.addtocart)
        self.checkout_button_buyer.clicked.connect(self.buyproducts)
        self.checkout_button_seller.clicked.connect(self.sellproducts)
        self.clear_cart_button_buyer.clicked.connect(self.clearcart)
        # add validators to search fields
        self.search_field_ps_buyer.setValidator(QDoubleValidator(1, 10000000000, 0))
        self.search_field_kmh_buyer.setValidator(QDoubleValidator(1, 10000000000, 0))
        self.search_field_max_price_buyer.setValidator(QDoubleValidator(1, 10000000000, 0))
        self.search_field_min_price_buyer.setValidator(QDoubleValidator(1, 10000000000, 0))
        self.search_field_year_buyer.setValidator(QDoubleValidator(1, 10000000000, 0))
        # setup buttons sidebar buyer
        self.home_button.clicked.connect(lambda: self.updatepage_buyer(0))
        self.search_button.clicked.connect(lambda: self.updatepage_buyer(1))
        self.cart_button.clicked.connect(lambda: self.updatepage_buyer(3))
        self.logout_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        # setup buttons sidebar seller
        self.home_button_seller.clicked.connect(lambda: self.updatepage_seller(0))
        self.search_button_seller.clicked.connect(lambda: self.updatepage_seller(1))
        self.cart_button_seller.clicked.connect(lambda: self.updatepage_seller(2))
        self.logout_button_seller.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        # set shortcuts
        self.shortcut_close = QShortcut(QKeySequence('ESC'), self)
        self.shortcut_close.activated.connect(self.navigateback)

    def navigateback(self):
        if self.stackedWidget.currentIndex() == 0:
            app.quit()
        if not self.isbuyer() and self.stackedWidget_mainapp_seller.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(0)
        if self.isbuyer() and self.stackedWidget_mainapp.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(0)
        if self.isbuyer() and self.stackedWidget_mainapp.currentIndex() != 0:
            self.updatepage_buyer(0)
        if not self.isbuyer() and self.stackedWidget_mainapp_seller.currentIndex() != 0:
            self.stackedWidget_mainapp_seller.setCurrentIndex(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            focused_widget = QApplication.focusWidget()

            if isinstance(focused_widget, QPushButton):
                focused_widget.click()

    def refreshtable(self):
        self.clearlayout()
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        query = 'SELECT * FROM bestand'
        cursor.execute(query)
        result = cursor.fetchall()
        search_results = result.copy()

        for product in result:
            if product[6] == 0 and self.isbuyer():
                search_results.remove(product)
                continue
            if self.search_field_ps_buyer.text() != '':
                if product[2] <= int(self.search_field_ps_buyer.text()):
                    search_results.remove(product)
                    continue
            if self.search_field_kmh_buyer.text() != '':
                if product[3] <= int(self.search_field_kmh_buyer.text()):
                    search_results.remove(product)
                    continue
            if self.search_field_min_price_buyer.text() != '':
                if product[4] <= int(self.search_field_min_price_buyer.text()):
                    search_results.remove(product)
                    continue
            if self.search_field_max_price_buyer.text() != '':
                if product[4] >= int(self.search_field_max_price_buyer.text()):
                    search_results.remove(product)
                    continue
            if self.search_field_year_buyer.text() != '':
                if product[5] <= int(self.search_field_year_buyer.text()):
                    search_results.remove(product)
                    continue

        if not self.isbuyer():
            query = 'SELECT * FROM zusatzgeraete'
            cursor.execute(query)
            result = cursor.fetchall()
            descending = True
            if self.sortbox_seller.currentIndex() == 0:
                index = 2
                descending = False
            elif self.sortbox_seller.currentIndex() == 1:
                index = 2
            elif self.sortbox_seller.currentIndex() == 2:
                index = 1
                descending = False
            elif self.sortbox_seller.currentIndex() == 3:
                index = 1
            result.sort(reverse=descending, key=lambda x: x[index])

        if self.sort_field_buyer.currentIndex() != 0 or not self.isbuyer():
            descending = True
            if self.sort_field_buyer.currentIndex() == 1:
                index = 2
            elif self.sort_field_buyer.currentIndex() == 2:
                index = 3
            elif self.sort_field_buyer.currentIndex() == 3 or self.sortbox_seller.currentIndex() == 2:
                index = 4
                descending = False
            elif self.sort_field_buyer.currentIndex() == 4 or self.sortbox_seller.currentIndex() == 3:
                index = 4
            elif self.sort_field_buyer.currentIndex() == 5:
                index = 5
            elif self.sortbox_seller.currentIndex() == 0 and not self.isbuyer():
                index = 6
                descending = False
            elif self.sortbox_seller.currentIndex() == 1:
                index = 6
            search_results.sort(reverse=descending, key=lambda x: x[index])

        for product in search_results:
            temp = ItemView(product[0], product[1], product[2], product[3], product[4], product[5], product[6])
            temp2 = SellerItem(product[0] + "_" + product[1], product[4], product[6])
            temp2.addtocart(self.cart_layout_seller, self.calculate_price_seller, self.layout_search_seller)
            self.layout_search_buyer.addWidget(temp)
            self.layout_search_seller.addWidget(temp2)
            temp.addtocart(self.configuration_layout_stockitem, self.configuration_layout_stockitem_details,
                            self.configuration_layout_stockitem_details_2, self.configuration_layout,
                            self.stackedWidget_mainapp)
        for extra in result:
            temp = SellerItem(extra[0], extra[1], extra[2], True)
            temp.addtocart(self.cart_layout_seller, self.calculate_price_seller, self.layout_search_seller)
            self.layout_search_seller_extra.addWidget(temp)

    def clearsearchfields(self):
        self.search_field_ps_buyer.setText('')
        self.search_field_kmh_buyer.setText('')
        self.search_field_max_price_buyer.setText('')
        self.search_field_min_price_buyer.setText('')
        self.search_field_year_buyer.setText('')
        self.sort_field_buyer.setCurrentIndex(0)
        self.refreshtable()

    def clearlayout(self):
        for i in reversed(range(self.layout_search_buyer.count())):
            self.layout_search_buyer.itemAt(i).widget().deleteLater()
        for i in reversed(range(self.layout_search_seller.count())):
            self.layout_search_seller.itemAt(i).widget().deleteLater()
        for i in reversed(range(self.layout_search_seller_extra.count())):
            self.layout_search_seller_extra.itemAt(i).widget().deleteLater()

    def clearcart(self):
        for i in reversed(range(self.cart_buyer_layout.count())):
            self.cart_buyer_layout.itemAt(i).widget().deleteLater()
        self.label_totalprice.setText("-Total Price: 0 €")
        self.label_sum_cart_buyer.setText(f"{int(self.budget)} €")
        self.checkout_button_buyer.setEnabled(False)

    def buyproducts(self):
        self.budget -= self.cartsum
        self.setuservalues()
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        query1 = 'SELECT budget FROM users WHERE username = "Klaus"'
        query2 = 'UPDATE users SET budget = ? WHERE username = ?'
        query3 = 'UPDATE bestand SET bestand = ? WHERE typ = ?'
        query4 = 'UPDATE zusatzgeraete SET bestand = ? WHERE geraet = ?'
        cursor.execute(query1)
        budget_seller = cursor.fetchone()[0]
        cursor.execute(query2, (self.budget, self.user))
        cursor.execute(query2, (self.cartsum + budget_seller, 'Klaus'))
        for i in reversed(range(self.cart_buyer_layout.count())):
            if int(self.cart_buyer_layout.itemAt(i).widget().price.text().split(' ')[1][:-1]) < 4700:
                self.cart_buyer_layout.itemAt(i).widget().stock -= int(self.cart_buyer_layout.itemAt(i).widget().anzahlbox.value())
                cursor.execute(query4, (self.cart_buyer_layout.itemAt(i).widget().stock, self.cart_buyer_layout.itemAt(i).widget().name.text()))
            else:
                self.cart_buyer_layout.itemAt(i).widget().instock -= 1
                cursor.execute(query3, (self.cart_buyer_layout.itemAt(i).widget().instock, self.cart_buyer_layout.itemAt(i).widget().typ.text()))
        db.commit()
        db.close()
        for i in reversed(range(self.cart_buyer_layout.count())):
            self.cart_buyer_layout.itemAt(i).widget().deleteLater()
        self.updatepage_buyer(4)
        self.label_totalprice.setText("-Total Price: 0 €")
        self.label_sum_cart_buyer.setText(f"{int(self.budget)} €")
        self.checkout_button_buyer.setEnabled(False)

    def sellproducts(self):
        self.budget -= self.calculate_price_seller()
        self.setuservalues()
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        query1 = 'UPDATE users SET budget = ? WHERE username = ?'
        query2 = 'UPDATE bestand SET bestand = ? WHERE typ = ?'
        query3 = 'UPDATE zusatzgeraete SET bestand = ? WHERE geraet = ?'
        cursor.execute(query1, (self.budget, 'Klaus'))
        for i in reversed(range(self.cart_layout_seller.count())):
            self.cart_layout_seller.itemAt(i).widget().instock += int(self.cart_layout_seller.itemAt(i).widget().stocknumber_box.value())
            if int(self.cart_layout_seller.itemAt(i).widget().price.text().split(' ')[1][:-1]) < 4700:
                cursor.execute(query3, (self.cart_layout_seller.itemAt(i).widget().instock, self.cart_layout_seller.itemAt(i).widget().name.text()))
            else:
                cursor.execute(query2, (self.cart_layout_seller.itemAt(i).widget().instock, self.cart_layout_seller.itemAt(i).widget().name.text().split('_', 1)[1]))
        db.commit()
        db.close()
        for i in reversed(range(self.cart_layout_seller.count())):
            self.cart_layout_seller.itemAt(i).widget().deleteLater()
        self.label_totalprice_seller.setText("-Total Price: 0 €")
        self.label_sum_cart_seller.setText(f"{int(self.budget)} €")
        self.checkout_button_seller.setEnabled(False)


    def updatepage_buyer(self, number):
        self.stackedWidget_mainapp.setCurrentIndex(number)

    def updatepage_seller(self, number):
        if number == 2:
            self.calculate_price_seller()
            for i in reversed(range(self.cart_layout_seller.count())):
                self.cart_layout_seller.itemAt(i).widget().stocknumber_box.textChanged.connect(self.calculate_price_seller)
        self.stackedWidget_mainapp_seller.setCurrentIndex(number)

    def addtocart(self):
        if self.configuration_layout_stockitem.count() != 0:
            self.configuration_layout_stockitem.itemAt(0).widget().stock.deleteLater()
            self.cart_buyer_layout.addWidget(self.configuration_layout_stockitem.itemAt(0).widget(),
                                             alignment=Qt.AlignTop)
        for i in reversed(range(self.configuration_layout_stockitem_details.count())):
            temp = self.configuration_layout_stockitem_details.itemAt(i).widget()
            self.cart_buyer_layout.addWidget(ExtraItemCart(temp.chiplabel.text(), temp.price, temp.stock))
        for i in reversed(range(self.configuration_layout_stockitem_details_2.count())):
            temp = self.configuration_layout_stockitem_details_2.itemAt(i).widget()
            self.cart_buyer_layout.addWidget(ExtraItemCart(temp.chiplabel.text(), temp.price, temp.stock))
        for i in reversed(range(self.cart_buyer_layout.count())):
            try:
                self.cart_buyer_layout.itemAt(i).widget().anzahlbox.textChanged.connect(self.calculate_price)
            except:
                pass

        self.calculate_price()
        self.updatepage_buyer(3)

    def calculate_price(self):
        sum = 0
        for i in reversed(range(self.cart_buyer_layout.count())):
            if int(self.cart_buyer_layout.itemAt(i).widget().price.text().split(' ')[1][:-1]) < 4700:
                sum += int(self.cart_buyer_layout.itemAt(i).widget().price.text().split(' ')[1][:-1]) * int(self.cart_buyer_layout.itemAt(i).widget().anzahlbox.value())
            else:
                sum += int(self.cart_buyer_layout.itemAt(i).widget().price.text().split(' ')[1][:-1])
        self.label_totalprice.setText(f"-Total Price: {sum} €")
        self.label_sum_cart_buyer.setText(f"{int(self.budget-sum)} €")
        self.cartsum = sum
        if int(self.budget-sum) < 0:
            self.checkout_button_buyer.setEnabled(False)
        else:
            self.checkout_button_buyer.setEnabled(True)

    def calculate_price_seller(self):
        sum = 0
        for i in reversed(range(self.cart_layout_seller.count())):
            sum += int(self.cart_layout_seller.itemAt(i).widget().price.text().split(' ')[1][:-1]) * int(
                self.cart_layout_seller.itemAt(i).widget().stocknumber_box.value())
        self.label_totalprice_seller.setText(f"-Total Price: {sum} €")
        self.label_sum_cart_seller.setText(f"{int(self.budget - sum)} €")
        if int(self.budget - sum) < 0:
            self.checkout_button_seller.setEnabled(False)
        else:
            self.checkout_button_seller.setEnabled(True)
        return sum

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
                self.setuservalues()
                self.clearsearchfields()
                self.stackedWidget.setCurrentIndex(1)  # switch to buyerpage
                self.refreshtable()
                self.hint_login_information.setText('')
                self.input_password.setText('')
                self.updatepage_buyer(0)
            elif result[0] == password and result[2] == 1:  # login as seller
                self.user = user
                self.budget = result[1]
                self.setuservalues()
                self.clearsearchfields()
                self.stackedWidget.setCurrentIndex(2)  # switch to sellerpage
                self.refreshtable()
                self.hint_login_information.setText('')
                self.input_password.setText('')
                self.updatepage_seller(0)
            else:
                self.hint_login_information.setText('Invalid Data')

    def register(self):
        registerwindow.show()

    def isbuyer(self):
        return self.stackedWidget.currentIndex() == 1

    def setuservalues(self):
        self.welcome_label.setText(f'welcome {self.user}'.upper())
        self.startpage_budget_label.setText(f'Budget {int(self.budget)} €')
        self.searchpage_budget_label.setText(f'Budget {int(self.budget)} €')
        self.welcome_label_username.setText(f'welcome {self.user}'.upper())
        self.welcome_label_budget.setText(f'your current budget is {int(self.budget)}€'.upper())
        self.label_cart_budget.setText(f'Current Money: {int(self.budget)}€')
        self.label_cart_budget_seller.setText(f'Current Money: {int(self.budget)}€')


class CreateAccountDialog(QDialog):
    def __init__(self):
        super(CreateAccountDialog, self).__init__()
        loadUi("./ui_files/newaccountdialog.ui", self)
        self.input_budget.setValidator(QDoubleValidator(1, 10000000000, 0))
        self.createAccount_button.clicked.connect(self.createaccount)

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
    def __init__(self, hersteller='hersteller', typ='typ', ps='ps', kmh='kmh', price='preis', baujahr='baujahr', stock='stock'):
        super(ItemView, self).__init__()
        loadUi("./ui_files/stockitem.ui", self)
        self.instock = stock
        self.typ.setText(str(typ))
        self.hersteller.setText(str(hersteller))
        self.year.setText('Year:' + str(baujahr))
        self.ps.setText(str(ps) + 'PS')
        self.kmh.setText(str(kmh) + 'km/h')
        self.price.setText('Price: ' + str(price) + '€')
        self.stock.setText('Stock: ' + str(stock))
        picture = QPixmap(f"./ui_files/product_images/{hersteller}_{typ}.jpg")
        self.picture.setPixmap(picture)
        self.picture.mousePressEvent = lambda event: self.showimage(picture)

    def text(self):
        return self.hersteller.text()

    def showimage(self, event):
        preview.show()
        preview.set_pixmap(event)

    def addtocart(self, layoutitem, layoutdetails, layoutdetails2, layoutextras, screen):
        self.cart_button.clicked.connect(lambda: self.addselftochart(layoutitem, layoutdetails, layoutdetails2, layoutextras, screen))

    def addselftochart(self, layoutitem, layoutdetails, layoutdetails2, layoutextras,  screen):
        for i in reversed(range(layoutitem.count())):
            layoutitem.itemAt(i).widget().deleteLater()
        for i in reversed(range(layoutextras.count())):
            layoutextras.itemAt(i).widget().deleteLater()
        for i in reversed(range(layoutdetails.count())):
            layoutdetails.itemAt(i).widget().deleteLater()
        for i in reversed(range(layoutdetails2.count())):
            layoutdetails2.itemAt(i).widget().deleteLater()

        layoutitem.addWidget(self)
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        query = 'SELECT * FROM zusatzgeraete'
        cursor.execute(query)
        result = cursor.fetchall()
        n = -1
        for extra in result:
            temp = None
            if extra[3] == 1 and self.hersteller.text() == 'Fendt':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[4] == 1 and self.hersteller.text() == 'Claas':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[5] == 1 and self.hersteller.text() == 'John Deere':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[6] == 1 and self.hersteller.text() == 'Steyr':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[7] == 1 and self.hersteller.text() == 'Deutz':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[10] == 1 and self.hersteller.text() == 'JCB':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[9] == 1 and self.hersteller.text() == 'New Holland':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[11] == 1 and self.hersteller.text() == 'Valtra':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[8] == 1 and self.hersteller.text() == 'Kubota':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[12] == 1 and self.hersteller.text() == 'Massey Ferguson':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            elif extra[13] == 1 and self.hersteller.text() == 'Lindner':
                temp = ExtraItem(extra[0], extra[1], extra[2])
                n += 1
            if temp is not None:
                temp.addtolayout(layoutdetails, layoutdetails2)
                layoutextras.addWidget(temp, n / 2, n % 2)

        self.cart_button.deleteLater()

        screen.setCurrentIndex(2)


class ExtraItem(QWidget):
    def __init__(self, name='name', price='preis', stock='stock'):
        super(ExtraItem, self).__init__()
        loadUi("./ui_files/extra_item.ui", self)
        self.stock.setText('Stock: ' + str(stock))
        self.price.setText('Price: ' + str(price) + '€')
        self.name.setText(str(name))
        picture = QPixmap(f"./ui_files/extras_images/{name}.jpg")
        self.picture.setPixmap(picture)
        self.picture.mousePressEvent = lambda event: self.showimage(picture)

    def showimage(self, event):
        preview.show()
        preview.set_pixmap(event)

    def addtolayout(self, layout, layout2):
        self.add_addon_button.clicked.connect(lambda: self.addselftolayout(layout, layout2))

    def addselftolayout(self, layout, layout2):

        itemisinlayout = False

        for i in reversed(range(layout.count())):
            if layout.itemAt(i).widget().text() == self.name.text():
                self.add_addon_button.setIcon(QIcon(QPixmap("./ui_files/assets/icons/icons_png/add_FILL0_wght400_GRAD0_opsz48.png")))
                layout.itemAt(i).widget().deleteLater()
                itemisinlayout = True

        for i in reversed(range(layout2.count())):
            if layout2.itemAt(i).widget().text() == self.name.text():
                self.add_addon_button.setIcon(QIcon(QPixmap("./ui_files/assets/icons/icons_png/add_FILL0_wght400_GRAD0_opsz48.png")))
                layout2.itemAt(i).widget().deleteLater()
                itemisinlayout = True

        if not itemisinlayout:
            self.add_addon_button.setIcon(QIcon(QPixmap("./ui_files/assets/icons/icons_png/remove.png")))
            if layout.count() < 7:
                layout.addWidget(Addondetails(self.name.text(), self.stock.text(), self.price.text()))
            else:
                layout2.addWidget(Addondetails(self.name.text(), self.stock.text(), self.price.text()))


class SellerItem(QWidget):
    def __init__(self, name='name', price='preis', stock='stock', extra=False):
        super(SellerItem, self).__init__()
        loadUi("./ui_files/item_seller.ui", self)
        self.stock.setText('Stock: ' + str(stock))
        self.price.setText('Price: ' + str(price) + '€')
        self.name.setText(str(name))
        self.extra = extra
        self.instock = stock
        if not self.extra:
            picture = QPixmap(f"./ui_files/product_images/{name}.jpg")
        else:
            picture = QPixmap(f"./ui_files/extras_images/{name}.jpg")
        self.picture.setPixmap(picture)

    def addtocart(self, cartlayout, calculateprice, searchlayout):
        self.addtocart_button.clicked.connect(lambda: self.addselftocart(cartlayout, calculateprice, searchlayout))

    def addselftocart(self, cartlayout, calculateprice, searchlayout):
        cartlayout.addWidget(self)
        self.addtocart_button.setText('Remove')
        self.addtocart_button.clicked.connect(lambda: self.removefromcart(calculateprice, searchlayout))

    def removefromcart(self, calculateprice, searchlayout):
        searchlayout.addWidget(self)
        calculateprice()

class Addondetails(QWidget):
    def __init__(self, name='name', stock=1, price=0):
        super(Addondetails, self).__init__()
        loadUi("./ui_files/addon.ui", self)
        self.chiplabel.setText(str(name))
        self.stock = str(stock)
        self.price = str(price)

    def text(self):
        return self.chiplabel.text()


class ZoomablePixmapWidget(QLabel):
    def __init__(self, pixmap):
        super().__init__()
        self.pixmap = pixmap
        self.zoom_factor = 1.0
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Preview')
        self.pan_start = QPoint()
        self.pixmap_offset = QPoint()
        self.setPixmap(self.pixmap)

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pixmap_offset)
        painter.drawPixmap(0, 0, self.pixmap)

    def wheelEvent(self, event):
        # Zoom in/out using mouse wheel
        zoom_factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.zoom_factor *= zoom_factor
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pan_start = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.pan_start
            self.pan_start = event.pos()
            self.pixmap_offset += delta
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pan_start = QPoint()
            self.setCursor(QCursor(Qt.ArrowCursor))

class ExtraItemCart(QWidget):
    def __init__(self, name='name', price='preis', anzahl=1):
        super(ExtraItemCart, self).__init__()
        loadUi("./ui_files/cart_extraitem.ui", self)
        self.price.setText(str(price))
        self.name.setText(str(name))
        self.anzahlbox.setMaximum(int(anzahl[7:]))
        self.stock = int(anzahl[7:])




# main
app = QApplication(sys.argv)
homescreen = Startscreen()
preview = ZoomablePixmapWidget(QPixmap('./ui_files/product_images/JCB_7270.jpg'))
homescreen.show()
registerwindow = CreateAccountDialog()

try:
    sys.exit(app.exec_())
except:
    print("App wird beendet...")
