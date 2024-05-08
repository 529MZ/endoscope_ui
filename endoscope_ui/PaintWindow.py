from PyQt5.QtWidgets import QColorDialog, QDialog, QMainWindow, QAction, QLabel, QPushButton, QFileDialog, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect
from ui.paint import *

class PaintWindow(QDialog):
    def __init__(self, pixmap):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.original_pixmap = pixmap
        self.pixmap = pixmap.copy()
        self.scaled_pixmap = None
        self.drawing = False
        self.panning = False
        self.lastPoint = QPoint()
        self.pen_color = Qt.red
        self.pen_width = 3

        self.zoom_factor = 1.0
        self.zoom_step = 0.1
        self.zoom_range = QRect(0, 0, self.original_pixmap.width(), self.original_pixmap.height())  # 初始缩放范围

        self.ui.pen.clicked.connect(self.startDrawing)
        self.ui.close.clicked.connect(self.closeWindow)
        self.ui.save.clicked.connect(self.saveImage)
        self.ui.zoomin.clicked.connect(self.zoomInImage)
        self.ui.zoomout.clicked.connect(self.zoomOutImage)
        self.ui.color.clicked.connect(self.choosePenColor)

        self.ui.comboBox.addItems(["1", "3", "5", "7", "9", "11", "13", "15", "17", "19"])
        self.ui.comboBox.setCurrentText(str(self.pen_width))
        self.ui.comboBox.currentTextChanged.connect(self.changePenWidth)

    def showEvent(self, event):
        super().showEvent(event)
        self.updateScaledPixmap()

    def updateScaledPixmap(self):
        # Gets the size of the label
        label_size = self.ui.imagelabel.size()

        # Get the desired portion from the original image according to the zoom range
        zoomed_pixmap = self.original_pixmap.copy(self.zoom_range)

        # Scale the pixmap to fit the label size
        self.scaled_pixmap = zoomed_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set the scaled pixmap to the label's pixmap
        self.ui.imagelabel.setPixmap(self.scaled_pixmap)

    def startDrawing(self):
        self.drawing = not self.drawing
        if self.drawing:
            r, g, b, _ = self.pen_color.getRgb()
            self.ui.pen.setStyleSheet(f"background-color: rgb({r}, {g}, {b})")
        else:
            self.ui.pen.setStyleSheet("")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drawing:
                self.lastPoint = event.pos() - self.ui.imagelabel.pos()
            else:
                self.panning = True
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and (event.buttons() & Qt.LeftButton):
            painter = QPainter(self.scaled_pixmap)
            painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos() - self.ui.imagelabel.pos())
            self.lastPoint = event.pos() - self.ui.imagelabel.pos()
            self.ui.imagelabel.setPixmap(self.scaled_pixmap)
            painter.end()
        elif self.panning and (event.buttons() & Qt.LeftButton):
            delta = event.pos() - self.lastPoint
            self.lastPoint = event.pos()

            # Compute the new zoom_range
            new_left = self.zoom_range.left() - int(delta.x() / self.zoom_factor)
            new_top = self.zoom_range.top() - int(delta.y() / self.zoom_factor)
            new_right = new_left + self.zoom_range.width()
            new_bottom = new_top + self.zoom_range.height()

            # Check boundary condition
            if new_left >= 0 and new_top >= 0 and new_right <= self.original_pixmap.width() and new_bottom <= self.original_pixmap.height():
                self.zoom_range.moveTo(new_left, new_top)
                self.updateScaledPixmap()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.panning:
                self.panning = False
                self.setCursor(QCursor(Qt.ArrowCursor))

    def saveImage(self):
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix('png')
        file_name, _ = file_dialog.getSaveFileName(self, 'Save Image', '', 'PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)')

        if file_name:
            self.scaled_pixmap.save(file_name)

    def zoomInImage(self):
        if self.zoom_factor < 1.0:
            self.zoom_factor += self.zoom_step
            self.updateZoomRange()
            self.updateScaledPixmap()

    def zoomOutImage(self):
        if self.zoom_factor > self.zoom_step:
            self.zoom_factor -= self.zoom_step
            self.updateZoomRange()
            self.updateScaledPixmap()

    def updateZoomRange(self):
        original_width = self.original_pixmap.width()
        original_height = self.original_pixmap.height()

        new_width = int(original_width * self.zoom_factor)
        new_height = int(original_height * self.zoom_factor)

        offset_x = max(0, min(self.zoom_range.left(), original_width - new_width))
        offset_y = max(0, min(self.zoom_range.top(), original_height - new_height))

        self.zoom_range = QRect(offset_x, offset_y, new_width, new_height)

    def choosePenColor(self):
        # Select a brush color
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color
            if self.drawing:
                r, g, b, _ = self.pen_color.getRgb()
                self.ui.pen.setStyleSheet(f"background-color: rgb({r}, {g}, {b})")

    def changePenWidth(self, width):
        # Change the brush size
        self.pen_width = int(width)

    def closeWindow(self):
        self.close()