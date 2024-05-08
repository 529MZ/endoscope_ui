import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QTimer, Qt
from main import *
from ui.LoginWindow import *
from database import *
import cv2

class login(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.connection = connect_to_database()  # 添加数据库连接属性

        # 连接button_1的点击事件到槽函数
        self.ui.loginButton.clicked.connect(self.on_button_1_clicked)

        self.ui.registerButton.clicked.connect(self.on_button_2_clicked)

    def on_button_1_clicked(self):

        id_value = self.ui.idEdit.text()

        name_value = self.ui.nameEdit.text()


        label_value = str(query_data(self.connection, name_value))  # 替换为实际的label值


        patient_id, patient_num = query_data(self.connection, name_value)

        if patient_id == id_value:
            disconnect_from_database(self.connection)

            self.close()
            mainWindow = MainWindow(patient_num)
            mainWindow.show()

    def on_button_2_clicked(self):
        name_value = self.ui.nameEdit_r.text()
        gender_value = self.ui.genderEdit_r.text()
        age_value = self.ui.ageEdit_r.text()
        id_value = self.ui.idEdit_r.text()

        insert_data(self.connection, name_value, gender_value, age_value, id_value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = login()
    mainWindow.show()
    sys.exit(app.exec_())