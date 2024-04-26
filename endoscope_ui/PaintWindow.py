from PyQt5.QtWidgets import QDialog, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QTimer, Qt, QPoint
from paint import *

class PaintWindow(QDialog):
    def __init__(self, pixmap):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.pixmap = pixmap
        self.scaled_pixmap = None
        self.drawing = False
        self.lastPoint = QPoint()

        self.ui.pen.clicked.connect(self.startDrawing)
        self.ui.close.clicked.connect(self.closeWindow)
        self.ui.save.clicked.connect(self.saveImage)

    def showEvent(self, event):
        super().showEvent(event)

        # 获取label的大小
        label_size = self.ui.imagelabel.size()

        # 缩放pixmap以适应label的大小
        self.scaled_pixmap = self.pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 将缩放后的pixmap设置为label的pixmap
        self.ui.imagelabel.setPixmap(self.scaled_pixmap)

    def startDrawing(self):
        self.drawing = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.lastPoint = event.pos() - self.ui.imagelabel.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.scaled_pixmap)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos() - self.ui.imagelabel.pos())
            self.lastPoint = event.pos() - self.ui.imagelabel.pos()
            self.ui.imagelabel.setPixmap(self.scaled_pixmap)
            painter.end()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False

    def saveImage(self):
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix('png')
        file_name, _ = file_dialog.getSaveFileName(self, 'Save Image', '','PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)')

        if file_name:
            self.scaled_pixmap.save(file_name)

    def closeWindow(self):
        self.close()