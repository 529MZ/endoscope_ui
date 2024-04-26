import sys
import os
import cv2
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QTimer, Qt
from videosettings import *

class videosettingWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_VideoSettingsUi()
        self.ui.setupUi(self)

        # 添加常用分辨率选项到resolutionComboBox
        self.ui.videoResolutionBox.addItem("640x480")
        self.ui.videoResolutionBox.addItem("800x600")
        self.ui.videoResolutionBox.addItem("1024x768")
        self.ui.videoResolutionBox.addItem("1280x720")
        self.ui.videoResolutionBox.addItem("1920x1080")

        # 添加常见图片文件后缀到imageCodecBox
        self.ui.videoCodecBox.addItem("H.264 (AVC)")
        self.ui.videoCodecBox.addItem("H.265 (HEVC)")
        self.ui.videoCodecBox.addItem("MPEG-4")
        self.ui.videoCodecBox.addItem("VP8")

        self.ui.videoFramerateBox.addItem("30")
        self.ui.videoFramerateBox.addItem("60")

