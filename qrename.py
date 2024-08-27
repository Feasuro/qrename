#!/usr/bin/env python

import sys, os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QDockWidget, QVBoxLayout,
                             QGridLayout , QListWidget, QFileDialog, QPushButton, QLineEdit,
                             QComboBox, QLabel)


class Renamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_controls()
        # create a layout
        layout = QGridLayout()
        layout.addWidget(QLabel('Prefix:'), 0, 0)
        layout.addWidget(self.ptype, 0, 1)
        layout.addWidget(self.pvalue, 0, 2)
        layout.addWidget(QLabel('Suffix:'), 1, 0)
        layout.addWidget(self.stype, 1, 1)
        layout.addWidget(self.svalue, 1, 2)
        layout.addWidget(QLabel('Name:'), 2, 0)
        layout.addWidget(self.ntype, 2, 1)
        layout.addWidget(self.nvalue, 2, 2)
        layout.addWidget(QLabel('Extension:'), 3, 0)
        layout.addWidget(self.etype, 3, 1)
        layout.addWidget(self.evalue, 3, 2)
        self.setLayout(layout)
    
    def setup_controls(self):
        """ Sets up the transformation widgets for the selected files. """
        # Prefix
        self.ptype = QComboBox(self)
        self.ptype.addItems(['Custom', 'Number', 'Date'])
        self.ptype.activated.connect(lambda index: self.deactivate_field(index, 'pvalue'))
        self.pvalue = QLineEdit(self)
        # Suffix
        self.stype = QComboBox(self)
        self.stype.addItems(['Custom', 'Number', 'Date'])
        self.stype.activated.connect(lambda index: self.deactivate_field(index,'svalue'))
        self.svalue = QLineEdit(self)
        # Name
        self.ntype = QComboBox(self)
        self.ntype.addItems(['Source name', 'lower case', 'UPPER CASE', 'Capitalize', 'Custom name'])
        self.ntype.activated.connect(lambda index: self.deactivate_field(index, 'nvalue'))
        self.nvalue = QLineEdit(self)
        self.nvalue.setDisabled(True)
        # Extension
        self.etype = QComboBox(self)
        self.etype.addItems(['Source extension', 'lower case', 'UPPER CASE', 'Capitalize', 'Custom extension'])
        self.etype.activated.connect(lambda index: self.deactivate_field(index, 'evalue'))
        self.evalue = QLineEdit(self)
        self.evalue.setDisabled(True)
    
    def transform(self, string: str) -> str:
        """ Performs the string transformation based on the selected options. """
        # TODO: Implement the transformation logic here
        pass
    
    def deactivate_field(self, index: int, field: str):
        """ Deactivates the transformation fields when specific option is chosen """
        match field:
            case 'pvalue':
                if index == 0:  # Custom
                    self.pvalue.setDisabled(False)
                else:  # Number, Date
                    self.pvalue.setDisabled(True)
            case 'svalue':
                if index == 0:  # Custom
                    self.svalue.setDisabled(False)
                else:  # Number, Date
                    self.svalue.setDisabled(True)
            case 'nvalue':
                if index == 4:  # Custom
                    self.nvalue.setDisabled(False)
                else:  # Other values
                    self.nvalue.setDisabled(True)
            case 'evalue':
                if index == 4:  # Custom
                    self.evalue.setDisabled(False)
                else:  # Other values
                    self.evalue.setDisabled(True)


class RenameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #size and title
        self.setWindowTitle("Qrename")
        self.resize(1000, 500)

        self.setup_ui()
        self.show()
    
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
    sys.exit(app.exec())