import logging
import os.path
import sys
import datetime

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QHeaderView, QTableWidgetItem

from UI import Ui_MainWindow
from function import NAME_TOOL, get_data_csv, update_data_csv, date_to_timestamp
from model import CustomFormatter, User
from thread import ThreadCrawl, ThreadGetToken


class MainView(QMainWindow):

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.thread = None
        self.logger = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_ui()
        self.setup_button()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(filename=f"std_log.log",
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
                            filemode="w",
                            encoding="utf-8")
        self.logger = logging.getLogger(NAME_TOOL.replace(" ", "_"))
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())

        self.logger.addHandler(ch)

    def setup_ui(self):
        self.ui.labelStatus.setHidden(True)
        self.ui.tblUser.setColumnHidden(0, True)
        self.ui.tblUser.setColumnHidden(9, True)
        self.ui.tblUser.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tblUser.selectionModel().selectionChanged.connect(self.on_selection_row_tbl_user)

        now = datetime.datetime.now()

        self.ui.checkBoxAfter.setChecked(True)
        self.ui.dateEditAfter.setEnabled(True)
        self.ui.dateEditAfter.setDisplayFormat("dd/MM/yyyy")
        self.ui.dateEditAfter.setDate(now)

        self.ui.checkBoxBefore.setChecked(False)
        self.ui.dateEditBefore.setEnabled(False)
        self.ui.dateEditBefore.setDisplayFormat("dd/MM/yyyy")
        self.ui.dateEditBefore.setDate(now + datetime.timedelta(days=1))

        self.ui.checkBoxAfter.toggled.connect(self.action_toggled_check_box)
        self.ui.checkBoxBefore.toggled.connect(self.action_toggled_check_box)

    def setup_button(self):
        self.ui.btnBrowser.clicked.connect(self.action_open_file)
        self.ui.btnUpdate.clicked.connect(self.action_save_file)
        self.ui.btnAdd.clicked.connect(self.action_add_row)
        self.ui.btnDelete.clicked.connect(self.action_remove_row)
        self.ui.btnCrawl.clicked.connect(self.action_crawl)
        self.ui.btnGetToken.clicked.connect(self.action_get_token)

    def closeEvent(self, event):
        if not self.is_running:
            event.accept()
            return

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Cảnh báo")
        dlg.setText("Bạn muốn tắt?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def load_data(self):
        path = self.ui.lineEditPath.text().strip()
        if os.path.isfile(path):
            users, error = get_data_csv(path=path)
            if users is None:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Lỗi")
                dlg.setText(error)
                dlg.setIcon(QMessageBox.Critical)
                dlg.exec()
                return

            self.ui.tblUser.setRowCount(0)
            for user in users:
                self.add_row_tbl_user(user)

    def action_toggled_check_box(self):
        self.ui.dateEditBefore.setEnabled(self.ui.checkBoxBefore.isChecked())
        self.ui.dateEditAfter.setEnabled(self.ui.checkBoxAfter.isChecked())

    def action_open_file(self):
        path = QFileDialog.getOpenFileName(filter="*.csv")
        if path[0] != "":
            self.ui.lineEditPath.setText(path[0].replace("\\", "/"))
            self.load_data()

    def action_add_row(self):
        current_row = self.ui.tblUser.currentRow()
        self.ui.tblUser.insertRow(current_row + 1)

    def action_remove_row(self):
        if self.ui.tblUser.rowCount() > 0:
            current_row = self.ui.tblUser.currentRow()
            self.ui.tblUser.removeRow(current_row)

    def action_save_file(self):
        path = self.ui.lineEditPath.text().strip()
        if path != "" and os.path.isfile(path):
            lines = []
            users = self.get_user_from_tbl_user()
            for user in users:
                lines.append(user.to_list())
            f, msg = update_data_csv(path=path, data=lines)
            self.load_data()
            if not f:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Lỗi")
                dlg.setText(msg)
                dlg.setIcon(QMessageBox.Critical)
                dlg.exec()
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Thông báo")
                dlg.setText("Lưu thành công")
                dlg.setIcon(QMessageBox.Information)
                dlg.exec()

    def add_row_tbl_user(self, user):
        row_count = self.ui.tblUser.rowCount()
        self.ui.tblUser.setRowCount(row_count + 1)
        if user.id:
            self.ui.tblUser.setItem(row_count, 0, QTableWidgetItem(f'{user.id}'))
        if user.name:
            self.ui.tblUser.setItem(row_count, 1, QTableWidgetItem(f'{user.name}'))
        if user.team:
            self.ui.tblUser.setItem(row_count, 2, QTableWidgetItem(f'{user.team}'))
        if user.client_id:
            self.ui.tblUser.setItem(row_count, 3, QTableWidgetItem(f'{user.client_id}'))
        if user.client_secret:
            self.ui.tblUser.setItem(row_count, 4, QTableWidgetItem(f'{user.client_secret}'))
        if user.code:
            self.ui.tblUser.setItem(row_count, 5, QTableWidgetItem(f'{user.code}'))
        if user.access_token:
            self.ui.tblUser.setItem(row_count, 6, QTableWidgetItem(f'{user.access_token}'))
        if user.refresh_token:
            self.ui.tblUser.setItem(row_count, 7, QTableWidgetItem(f'{user.refresh_token}'))
        if user.url_get_code:
            self.ui.tblUser.setItem(row_count, 8, QTableWidgetItem(f'{user.url_get_code}'))

    def get_user_from_tbl_user(self):
        users = []
        for index in range(self.ui.tblUser.rowCount()):
            user = User(_id=index,
                        _name=self.ui.tblUser.item(index, 1).text()
                        if self.ui.tblUser.item(index, 1) is not None else None,
                        _team=self.ui.tblUser.item(index, 2).text()
                        if self.ui.tblUser.item(index, 2) is not None else None,
                        _client_id=self.ui.tblUser.item(index, 3).text()
                        if self.ui.tblUser.item(index, 3) is not None else None,
                        _client_secret=self.ui.tblUser.item(index, 4).text()
                        if self.ui.tblUser.item(index, 4) is not None else None,
                        _code=self.ui.tblUser.item(index, 5).text()
                        if self.ui.tblUser.item(index, 5) is not None else None,
                        _access_token=self.ui.tblUser.item(index, 6).text()
                        if self.ui.tblUser.item(index, 6) is not None else None,
                        _refresh_token=self.ui.tblUser.item(index, 7).text()
                        if self.ui.tblUser.item(index, 7) is not None else None)
            users.append(user)

        return users

    def on_selection_row_tbl_user(self, selected):
        self.ui.labelStatus.setHidden(False)
        for ix in selected.indexes():
            item_selected = self.ui.tblUser.item(ix.row(), ix.column())
            if item_selected:
                self.ui.labelStatus.setStyleSheet("color: blue")
                self.ui.labelStatus.setText(item_selected.text())
            return

    def action_get_token(self):
        if self.ui.tblUser.rowCount() > 0:
            users = self.get_user_from_tbl_user()
            current_row = self.ui.tblUser.currentRow()

            self.set_status_button(False)
            self.is_running = True
            self.thread = ThreadGetToken(_user=users[current_row], _index=current_row)
            self.thread.sender_status.connect(self.set_status_row)
            self.thread.token.connect(self.set_token)
            self.thread.logs.connect(self.set_logs)
            self.thread.start()

    def action_crawl(self):
        time_after = None
        time_before = None
        if self.ui.checkBoxBefore.isChecked():
            time_before = self.ui.dateEditBefore.date().toString("dd/MM/yyyy")
            time_before = date_to_timestamp(_date=time_before)
        if self.ui.checkBoxAfter.isChecked():
            time_after = self.ui.dateEditAfter.date().toString("dd/MM/yyyy")
            time_after = date_to_timestamp(_date=time_after)

        users = self.get_user_from_tbl_user()
        if len(users) == 0:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Lỗi")
            dlg.setText("Không có bản ghi nào")
            dlg.setIcon(QMessageBox.Critical)
            dlg.exec()
            return

        self.set_status_button(False)
        self.is_running = True
        self.thread = ThreadCrawl(_users=users, _time_after=time_after, _time_before=time_before)
        self.thread.sender_status.connect(self.set_status_row)
        self.thread.token.connect(self.set_token)
        self.thread.logs.connect(self.set_logs)
        self.thread.start()

    def set_status_row(self, index, status):
        self.ui.tblUser.setColumnHidden(9, False)
        self.ui.tblUser.setItem(index, 9, QTableWidgetItem(status))

    def set_token(self, index, access_token, refresh_token):
        self.ui.tblUser.setItem(index, 6, QTableWidgetItem(access_token))
        self.ui.tblUser.setItem(index, 7, QTableWidgetItem(refresh_token))

    def set_logs(self, kind, val):
        self.ui.labelStatus.setHidden(False)
        if kind == 0:
            self.ui.labelStatus.setStyleSheet("color: blue")
            self.ui.labelStatus.setText(val)
            self.logger.info(val)
        elif kind == 1:
            self.ui.labelStatus.setStyleSheet("color: red")
            self.ui.labelStatus.setText(val)
            self.logger.error(val)
        elif kind == 2:
            self.ui.labelStatus.setStyleSheet("color: green")
            self.ui.labelStatus.setText(val)
            self.logger.info(val)
        elif kind == 3:
            self.is_running = False
            self.set_status_button(True)

    def set_status_button(self, val):
        self.ui.btnAdd.setEnabled(val)
        self.ui.btnDelete.setEnabled(val)
        self.ui.btnUpdate.setEnabled(val)
        self.ui.btnCrawl.setEnabled(val)
        self.ui.btnBrowser.setEnabled(val)
        self.ui.btnGetToken.setEnabled(val)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainView()
    window.show()
    app.setWindowIcon(QIcon('logo.ico'))
    window.setWindowIcon(QIcon('logo.ico'))
    sys.exit(app.exec())
