import sys
import pymysql
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QDialog, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget, QListView, QApplication
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QTimer, Qt, QPoint, QStringListModel
from ui.image_managementWindow import *
from database import *

class imagemanagement(QWidget):
    def __init__(self, num):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.num = num

        self.current_index = self.ui.listView.currentIndex()

        self.model = QStringListModel(self)

        self.connection = connect_to_database()

        self.ui.listView.setModel(self.model)

        image_addresses = self.get_image_addresses()

        self.model.setStringList(image_addresses)

        self.ui.listView.clicked.connect(self.on_list_view_clicked)

        self.ui.pushButton.clicked.connect(self.on_delete_button_clicked)

        self.ui.pushButton_2.clicked.connect(self.on_save_button_clicked)

    def get_image_addresses(self):
        cursor = self.connection.cursor()

        # Execute the SQL query to get the image address that meets the conditions
        query = "SELECT address_pic FROM image WHERE patient_num = %s"
        cursor.execute(query, (self.num,))

        # Obtain query results
        results = cursor.fetchall()

        # Extract the image address and store it in a list
        image_addresses = [row["address_pic"] for row in results]

        cursor.close()

        return image_addresses

    def on_list_view_clicked(self, index):
        # Get the text of the clicked item (image address)
        self.current_index = index

        image_address = self.model.data(self.current_index, Qt.DisplayRole)

        # Load image file
        image = QImage(image_address)

        image_1 = cv2.imread(image_address)

        if image.isNull():
            # If the image fails to load, an error message is displayed
            self.ui.label.setText("Failed to load image")
            self.ui.label_3.clear()
            self.ui.label_4.clear()
        else:
            # Displays the image on the QLabel
            pixmap = QPixmap.fromImage(image)
            self.ui.label.setPixmap(
                pixmap.scaled(self.ui.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

            hist = cv2.calcHist([image_1], [0], None, [256], [0, 256])

            # Draw histogram images
            hist_img = self.draw_histogram(hist)

            # Displays the histogram image on the QLabel
            hist_pixmap = QPixmap.fromImage(self.cvt_cv_qt(hist_img))
            self.ui.label_4.setPixmap(
                hist_pixmap.scaled(self.ui.label_4.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

            height, width, channels = image_1.shape

            # Generate image information text
            info_text = f"尺寸: {width}x{height}\n通道数: {channels}"
            self.ui.label_3.setText(info_text)

        cursor = self.connection.cursor()
        query = "SELECT * FROM image WHERE address_pic = %s"
        cursor.execute(query, (image_address,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            text_address = result["address_txt"]
            if text_address == "None":
                # If address_txt is "None", clear the contents of QTextEdit
                self.ui.textEdit.clear()
            else:
                # Read the contents of the txt file
                try:
                    with open(text_address, 'r') as file:
                        content = file.read()
                        self.ui.textEdit.setPlainText(content)
                except IOError:
                    # If the file fails to be read, an error message is displayed
                    self.ui.textEdit.setPlainText("Failed to load text file")

            num_value = result["patient_num"]
            str = query_data_2(self.connection, num_value)
            self.ui.label_2.setText(str)
        else:
            # If no matching rows are found, clear the contents of QTextEdit
            self.ui.textEdit.clear()

    def on_save_button_clicked(self):
        # Gets the index of the currently selected item
        current_index = self.ui.listView.currentIndex()

        # Gets the text of the currently selected item (image address)
        current_image_address = self.model.data(current_index, Qt.DisplayRole)

        # txt file path
        txt_directory = "txt"
        txt_file_name = os.path.splitext(os.path.basename(current_image_address))[0] + ".txt"
        txt_file_path = os.path.join(txt_directory, txt_file_name)

        # Save the text in textEdit to a txt file
        text_content = self.ui.textEdit.toPlainText()
        try:
            with open(txt_file_path, 'w') as file:
                file.write(text_content)
            print("Text file saved:", txt_file_path)
        except IOError:
            print("Failed to save text file:", txt_file_path)
            return

        # Update the address_txt column for the corresponding row in the database using pymysql
        cursor = self.connection.cursor()
        query = "UPDATE image SET address_txt = %s WHERE address_pic = %s"
        try:
            cursor.execute(query, (txt_file_path, current_image_address))
            self.connection.commit()
            print("Database updated successfully")
        except Exception as e:
            self.connection.rollback()
            print("Error updating database:", str(e))
        finally:
            cursor.close()

    def on_delete_button_clicked(self):

        current_index = self.ui.listView.currentIndex()

        current_image_address = self.model.data(current_index, Qt.DisplayRole)

        # Use pymysql to delete the corresponding row in the database
        cursor = self.connection.cursor()
        query = "DELETE FROM image WHERE address_pic = %s"
        try:
            cursor.execute(query, (current_image_address,))
            self.connection.commit()
            print("Database row deleted successfully")
        except Exception as e:
            self.connection.rollback()
            print("Error deleting database row:", str(e))
        finally:
            cursor.close()

        # Delete the corresponding image file
        try:
            os.remove(current_image_address)
            print("Image file deleted:", current_image_address)
        except FileNotFoundError:
            print("Image file not found:", current_image_address)
        except Exception as e:
            print("Error deleting image file:", str(e))

        # Delete the corresponding txt file
        txt_file_path = os.path.splitext(current_image_address)[0] + ".txt"
        try:
            os.remove(txt_file_path)
            print("Text file deleted:", txt_file_path)
        except FileNotFoundError:
            print("Text file not found:", txt_file_path)
        except Exception as e:
            print("Error deleting text file:", str(e))

        # Deletes the corresponding project from QStringListModel
        row = current_index.row()
        self.model.removeRow(row)

        # Clear the contents of QLabel and QTextEdit
        self.ui.label.clear()
        self.ui.textEdit.clear()

    def cvt_cv_qt(self, img):
        # Convert OpenCV image to QImage
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qt_image

    def draw_histogram(self, hist):
        # Draw histogram images
        hist_img = np.zeros((256, 256, 3), dtype=np.uint8)
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)

        bin_width = hist_img.shape[1] / len(hist)
        for i in range(len(hist)):
            intensity = int(hist[i][0])
            cv2.rectangle(hist_img, (int(i * bin_width), hist_img.shape[0]),
                          (int((i + 1) * bin_width), hist_img.shape[0] - intensity),
                          (255, 255, 255), -1)

        return hist_img

"""if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = imagemanagement()
    mainWindow.show()
    sys.exit(app.exec_())"""