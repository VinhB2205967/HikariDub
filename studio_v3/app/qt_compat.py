"""
Qt6 Compatibility Layer: Uses PySide6 by default and seamlessly falls back to PyQt6
so the application runs reliably in any Qt6 environment.
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
    from PySide6.QtCore import Signal, Slot, Property, Qt, QThread, QTimer, QUrl, QRectF, QSize
    from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QFontMetrics, QImage, QPixmap, QAction
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QToolButton,
        QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QSplitter, QLineEdit,
        QPlainTextEdit, QComboBox, QSlider, QProgressBar, QCheckBox, QTableWidget,
        QTableWidgetItem, QHeaderView, QFileDialog, QStackedWidget, QSizePolicy, QMenu
    )
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
    QT_BINDING = "PySide6"
except ImportError:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtMultimedia
    from PyQt6.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, pyqtProperty as Property, Qt, QThread, QTimer, QUrl, QRectF, QSize
    from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QFontMetrics, QImage, QPixmap, QAction
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QToolButton,
        QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QSplitter, QLineEdit,
        QPlainTextEdit, QComboBox, QSlider, QProgressBar, QCheckBox, QTableWidget,
        QTableWidgetItem, QHeaderView, QFileDialog, QStackedWidget, QSizePolicy, QMenu
    )
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
    QT_BINDING = "PyQt6"
