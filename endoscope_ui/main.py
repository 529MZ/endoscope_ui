import sys
import os
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QTimer, Qt
from ui.MainWindow import *
from PaintWindow import *
from database import *
from imagesettingWindow import *
from videosettingWindow import *
from Image_management import *
from video_management import *

class MainWindow(QMainWindow):
    def __init__(self, num_value):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.num_value = num_value
        self.contrast_value = 1.0
        self.zoom_level = 100

        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)
        self.is_recording = False
        self.video_writer = None

        self.initCameraMenu()

        self.initManagementMenu()

        self.ui.pushButton_Shot.clicked.connect(self.captureImage)

        self.ui.pushButton_3.clicked.connect(self.toggleRecording)

        self.ui.pushButton_imagesetting.clicked.connect(self.ImageSetting)

        self.ui.pushButton_4.clicked.connect(self.VideoSetting)

        self.ui.horizontalSlider.valueChanged.connect(self.adjustContrast)

        self.ui.horizontalSlider_2.valueChanged.connect(self.adjustZoom)

        self.ui.imagelabel.mouseDoubleClickEvent = self.imageDoubleClicked

        self.connection = connect_to_database()



    def initCameraMenu(self):
        camera_menu = self.ui.menubar.addMenu("Camera")
        camera_devices = self.getAvailableCameras()

        for device_id, device_name in camera_devices.items():
            action = QAction(device_name, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, dev_id=device_id: self.switchCamera(dev_id))
            camera_menu.addAction(action)

    def initManagementMenu(self):
        management_menu = self.ui.menubar.addMenu("Management")

        image_management_action = QAction("Image Management", self)
        image_management_action.triggered.connect(self.openImageManagementWindow)
        management_menu.addAction(image_management_action)

        video_management_action = QAction("Video Management", self)
        video_management_action.triggered.connect(self.openVideoManagementWindow)
        management_menu.addAction(video_management_action)

    def getAvailableCameras(self):
        camera_devices = {}
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                camera_devices[i] = f"Camera {i}"
            cap.release()
        return camera_devices

    def switchCamera(self, device_id):
        if self.camera:
            self.camera.release()
        self.camera = cv2.VideoCapture(device_id)

    def updateFrame(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                frame = frame.astype(np.float32)
                mean = frame.mean(axis=(0, 1))
                contrast_value = 1.0 + self.contrast_value / 100.0
                frame = (frame - mean) * contrast_value + mean + self.contrast_value
                frame = np.clip(frame, 0, 255).astype(np.uint8)

                original_height, original_width, _ = frame.shape
                scale_factor = self.zoom_level / 100.0
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                offset_x = (original_width - new_width) // 2
                offset_y = (original_height - new_height) // 2
                frame = frame[offset_y:offset_y+new_height, offset_x:offset_x+new_width]

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                label_size = self.ui.videolabel.size()
                scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.videolabel.setPixmap(scaled_pixmap)

                if self.is_recording and self.video_writer:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.video_writer.write(frame)

                self.updateHistogram(frame)

    def captureImage(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                image_folder = "image"
                os.makedirs(image_folder, exist_ok=True)
                image_path = os.path.join(image_folder, f"screenshot_{timestamp}.jpg")
                cv2.imwrite(image_path, frame)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                label_size = self.ui.imagelabel.size()
                scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ui.imagelabel.setPixmap(scaled_pixmap)

                new_text = f"Screenshot captured successfully. Image saved at: {image_path}"

                self.ui.plainTextEdit.appendPlainText(new_text)

                txt = f"None"

                insert_data_1(self.connection, self.num_value, image_path, txt)

    def toggleRecording(self):
        if not self.is_recording:
            self.startRecording()
        else:
            self.stopRecording()

    def startRecording(self):
        if self.camera and not self.is_recording:
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            video_folder = "video"
            os.makedirs(video_folder, exist_ok=True)
            video_path = os.path.join(video_folder, f"recording_{timestamp}.avi")

            frame_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (frame_width, frame_height))

            insert_data_2(self.connection, self.num_value, video_path)

            self.is_recording = True
            self.ui.pushButton_3.setText("Stop")
            self.ui.pushButton_3.setStyleSheet("background-color: red; font: 75 24pt '微软雅黑';")

            new_text = f"Start Recording!!"
            self.ui.plainTextEdit.appendPlainText(new_text)

    def stopRecording(self):
        if self.is_recording:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            self.ui.pushButton_3.setText("Recording")
            self.ui.pushButton_3.setStyleSheet("font: 75 24pt '微软雅黑';")

            new_text = f"Stop Recording!!"
            self.ui.plainTextEdit.appendPlainText(new_text)

    def updateHistogram(self, frame):
        hist_item = cv2.calcHist([frame], [0], None, [256], [0, 256])
        cv2.normalize(hist_item, hist_item, 0, 255, cv2.NORM_MINMAX)
        hist_img = np.full((200, 512, 3), 0, dtype=np.uint8)  # 增大直方图的尺寸
        for x, y in enumerate(hist_item):
            cv2.line(hist_img, (x * 2, 199), (x * 2, 199 - int(y * 0.78)), (255, 255, 255), 1)  # 调整直方图的缩放比例
        hist_img = cv2.cvtColor(hist_img, cv2.COLOR_BGR2RGB)
        qImg = QImage(hist_img.data, hist_img.shape[1], hist_img.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaled(self.ui.label_2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_2.setPixmap(scaled_pixmap)


    def closeEvent(self, event):
        self.timer.stop()
        self.camera.release()

        if self.connection:  # 检查是否有活动的数据库连接
            disconnect_from_database(self.connection)  # 断开数据库连接

        event.accept()

    def imageDoubleClicked(self, event):
        if not self.ui.imagelabel.pixmap():
            return

        self.paintWindow = PaintWindow(self.ui.imagelabel.pixmap())
        self.paintWindow.exec()

    def showEvent(self, event):
        super().showEvent(event)
        str = query_data_2(self.connection, self.num_value)
        self.ui.label_patient.setText(str)

    def ImageSetting(self):
        self.imagesetting = imagesettingWindow()
        self.imagesetting.exec()

    def VideoSetting(self):
        self.videosetting = videosettingWindow()
        self.videosetting.exec()

    def openImageManagementWindow(self):
        self.imagemanagement = imagemanagement(self.num_value)
        self.imagemanagement.show()

    def openVideoManagementWindow(self):
        self.videomanagement = videomanagement(self.num_value)
        self.videomanagement.show()

    def adjustContrast(self, value):
        self.contrast_value = value

    def adjustZoom(self, value):
        self.zoom_level = 100-value


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    #mainWindow.show()
    sys.exit(app.exec_())
