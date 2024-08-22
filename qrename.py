#!/usr/bin/env python

import sys, os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QDockWidget, QVBoxLayout,
                             QFormLayout , QListWidget, QFileDialog, QPushButton, QLineEdit)


class Renamer(QWidget):
    def __init__(self):
        super().__init__()

        # create a layout
        layout = QFormLayout()
        layout.addRow('Prefix:', QLineEdit(self))
        layout.addRow('Suffix:', QLineEdit(self))
        self.setLayout(layout)


class RenameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #size and title
        self.setWindowTitle("Qrename")
        self.resize(400, 300)

        self.setup_ui()
    
    def setup_ui(self):
        """ Creates the main window layout and widgets. """
        #create renamer central widget
        self.renamer = Renamer()
        self.setCentralWidget(self.renamer)
        #left dock for files management
        self.files = QListWidget()
        self.open_button = QPushButton("Open Files")
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.files)
        layout.addWidget(self.open_button)
        container.setLayout(layout)
        leftdock = QDockWidget('Selected Files')
        leftdock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        leftdock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, leftdock)
        #open file dialog when button is clicked
        self.open_button.clicked.connect(self.open_files)
        #right dock for new name presentation
        self.new_names = QListWidget()
        self.rename_button = QPushButton("Rename Files")
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.new_names)
        layout.addWidget(self.rename_button)
        container.setLayout(layout)
        rightdock = QDockWidget('New Names')
        rightdock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        rightdock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, rightdock)
        #rename files when button is clicked
        self.rename_button.clicked.connect(self.rename_files)

    def open_files(self):
        """ Opens file dialog and adds selected files to the left dock. """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        for file in files:
            self.files.addItem(file)
    
    def rename_files(self):
        """ Renames files based on the new names provided in the right dock. """
        #new_names = [item.text() for item in self.new_names.items()]
        #for i, file in enumerate(self.files.items()):
        #    self.files.setItemText(i, f"{file.text()} ({new_names[i]})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RenameWindow()
    window.show()
    sys.exit(app.exec())