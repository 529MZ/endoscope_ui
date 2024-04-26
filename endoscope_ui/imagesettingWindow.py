import sys
import os
import cv2
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QTimer, Qt
from imagesettings import *

class imagesettingWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_ImageSettingsUi()
        self.ui.setupUi(self)

        # 添加常用分辨率选项到resolutionComboBox
        self.ui.imageResolutionBox.addItem("640x480")
        self.ui.imageResolutionBox.addItem("800x600")
        self.ui.imageResolutionBox.addItem("1024x768")
        self.ui.imageResolutionBox.addItem("1280x720")
        self.ui.imageResolutionBox.addItem("1920x1080")

        # 添加常见图片文件后缀到imageCodecBox
        self.ui.imageCodecBox.addItem("JPG")
        self.ui.imageCodecBox.addItem("PNG")
        self.ui.imageCodecBox.addItem("BMP")
        self.ui.imageCodecBox.addItem("TIFF")


