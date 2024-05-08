import sys
import os
import cv2
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from ui.imagesettings import *

class imagesettingWindow(QDialog):
    imageSettingsChanged = pyqtSignal(str, str)  # 添加自定义信号

    def __init__(self):
        super().__init__()

        self.ui = Ui_ImageSettingsUi()
        self.ui.setupUi(self)


        self.ui.imageResolutionBox.addItem("640x480")
        self.ui.imageResolutionBox.addItem("800x600")
        self.ui.imageResolutionBox.addItem("1024x768")
        self.ui.imageResolutionBox.addItem("1280x720")
        self.ui.imageResolutionBox.addItem("1920x1080")


        self.ui.imageCodecBox.addItem("JPG")
        self.ui.imageCodecBox.addItem("PNG")
        self.ui.imageCodecBox.addItem("BMP")
        self.ui.imageCodecBox.addItem("TIFF")

    def accept(self):

        resolution = self.ui.imageResolutionBox.currentText()
        codec = self.ui.imageCodecBox.currentText()


        self.imageSettingsChanged.emit(resolution, codec)

        super().accept()


