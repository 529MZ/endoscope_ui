import sys
import pymysql
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QDialog, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget, QListView, QApplication
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QTimer, Qt, QPoint, QStringListModel
from ui.video_managementWindow import *
from database import *

class videomanagement(QWidget):
    def __init__(self, num):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.num = num

        self.is_playing = True

        self.current_index = self.ui.listView.currentIndex()

        self.model = QStringListModel(self)

        self.connection = connect_to_database()

        self.ui.listView.setModel(self.model)

        image_addresses = self.get_image_addresses()

        self.model.setStringList(image_addresses)

        self.ui.listView.clicked.connect(self.on_list_view_clicked)

        self.ui.label.mousePressEvent = self.on_label_clicked

        self.ui.pushButton.clicked.connect(self.on_delete_button_clicked)

        self.ui.pushButton_2.clicked.connect(self.on_save_button_clicked)

        self.ui.horizontalSlider.setRange(0, 100)
        self.ui.horizontalSlider.sliderMoved.connect(self.on_slider_moved)

    def get_image_addresses(self):
        cursor = self.connection.cursor()

        # Execute the SQL query to get the image address that meets the conditions
        query = "SELECT address_video FROM video WHERE patient_num = %s"
        cursor.execute(query, (self.num,))

        # Obtain query results
        results = cursor.fetchall()

        # Extract the image address and store it in a list
        video_addresses = [row["address_video"] for row in results]

        cursor.close()

        return video_addresses

    def on_label_clicked(self, event):
        if self.is_playing:
            self.timer.stop()
            self.is_playing = False
        else:
            self.timer.start()
            self.is_playing = True

    def on_list_view_clicked(self, index):
        # Get the text of the clicked item (video address)
        self.current_index = index

        video_address = self.model.data(self.current_index, Qt.DisplayRole)

        self.is_playing = True

        self.cap = cv2.VideoCapture(video_address)

        if not self.cap.isOpened():
            print("Failed to open video file:", video_address)
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # Create a QTimer that periodically updates video frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Set the timer interval (milliseconds) based on the video frame rate
        interval = int(1000 / self.fps)
        self.timer.start(interval)

    def update_frame(self):
        # Read the next frame of the video
        ret, frame = self.cap.read()

        if not self.is_playing:
            return

        if ret:
            # Convert the frame to QImage format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.ui.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Display QImage on QLabel
            self.ui.label.setPixmap(scaled_pixmap)

            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            progress = (current_frame / self.total_frames) * 100
            self.ui.horizontalSlider.setValue(int(progress))
        else:
            # After the video is played or read fails, stop the timer
            self.timer.stop()
            self.cap.release()

    def on_slider_moved(self, position):
        # Calculates the frame number to jump based on the position of the slider
        frame_number = (position / 100) * self.total_frames

        # Sets the current frame of the video
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def on_save_button_clicked(self):
        current_index = self.ui.listView.currentIndex()


    def on_delete_button_clicked(self):

        current_index = self.ui.listView.currentIndex()


        current_video_address = self.model.data(current_index, Qt.DisplayRole)


        cursor = self.connection.cursor()
        query = "DELETE FROM video WHERE address_video = %s"
        try:
            cursor.execute(query, (current_video_address,))
            self.connection.commit()
            print("Database row deleted successfully")
        except Exception as e:
            self.connection.rollback()
            print("Error deleting database row:", str(e))
        finally:
            cursor.close()



        row = current_index.row()
        self.model.removeRow(row)


        self.ui.label.clear()




"""if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = videomanagement()
    mainWindow.show()
    sys.exit(app.exec_())"""