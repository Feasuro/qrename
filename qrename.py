#!/usr/bin/env python

import sys, os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QDockWidget, QVBoxLayout,
                             QGridLayout, QFormLayout, QListWidget, QFileDialog, QPushButton,
                             QLineEdit, QComboBox, QSpinBox, QDateEdit, QLabel, QGroupBox,
                             QMessageBox)


class Renamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_controls()
        self.setup_layout()

    def setup_layout(self):
        """ Sets up the layout for the renamer window. """
        # Basic controls
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
        # Number
        group = QGroupBox('Number')
        grouplayout = QFormLayout()
        grouplayout.addRow('Start number:', self.start)
        grouplayout.addRow('Number of digits:', self.digits)
        group.setLayout(grouplayout)
        layout.addWidget(group, 4, 0, 1, 3)
        # Date & Time
        group = QGroupBox('Date and Time')
        grouplayout = QFormLayout()
        grouplayout.addRow('Date:', self.date)
        group.setLayout(grouplayout)
        layout.addWidget(group, 5, 0, 1, 3)
        # set layout
        self.setLayout(layout)

    def setup_controls(self):
        """ Sets up the transformation widgets for the selected files. """
        # Prefix
        self.pvalue = QLineEdit(self)
        self.ptype = QComboBox(self)
        self.ptype.addItems(['Custom', 'Number', 'Date'])
        self.ptype.currentTextChanged.connect(lambda text: self.deactivate_field(text, self.pvalue))
        # Suffix
        self.svalue = QLineEdit(self)
        self.stype = QComboBox(self)
        self.stype.addItems(['Custom', 'Number', 'Date'])
        self.stype.currentTextChanged.connect(lambda text: self.deactivate_field(text, self.svalue))
        # Name
        self.nvalue = QLineEdit(self)
        self.nvalue.setDisabled(True)
        self.ntype = QComboBox(self)
        self.ntype.addItems(['Source name', 'lower case', 'UPPER CASE', 'Title Case',
                             'Capitalize text', 'Custom name'])
        self.ntype.currentTextChanged.connect(lambda text: self.deactivate_field(text, self.nvalue))
        # Extension
        self.evalue = QLineEdit(self)
        self.evalue.setDisabled(True)
        self.etype = QComboBox(self)
        self.etype.addItems(['Source extension', 'lower case', 'UPPER CASE', 'Title Case',
                             'Capitalize text', 'Custom extension'])
        self.etype.currentTextChanged.connect(lambda text: self.deactivate_field(text, self.evalue))
        # Number
        self.digits = QSpinBox(self)
        self.start = QSpinBox(self)
        # Date
        self.date = QDateEdit(self)
        self.date.setDisplayFormat('dd-MM-yyyy')
        self.date.setCalendarPopup(True)

    def transform(self, string: str, index: int) -> str:
        """ Performs the string transformation based on the selected options. """
        result = ''
        match self.ptype.currentText():
            case 'Number':
                result += str(self.start.value() + index).zfill(self.digits.value())
            case 'Date':
                result += self.date.date().toString('dd-MM-yyyy')
            case 'Custom':
                result += self.pvalue.text()
        basename = os.path.splitext(os.path.basename(string))[0]
        match self.ntype.currentText():
            case 'Source name':
                result += basename
            case 'lower case':
                result += basename.lower()
            case 'UPPER CASE':
                result += basename.upper()
            case 'Title Case':
                result += basename.title()
            case 'Capitalize text':
                result += basename.capitalize()
            case 'Custom name':
                result += self.nvalue.text()
        match self.stype.currentText():
            case 'Number':
                result += str(self.start.value() + index).zfill(self.digits.value())
            case 'Date':
                result += self.date.date().toString('dd-MM-yyyy')
            case 'Custom':
                result += self.svalue.text()
        extension = os.path.splitext(os.path.basename(string))[1]
        match self.etype.currentText():
            case 'Source extension':
                result += extension
            case 'lower case':
                result += extension.lower()
            case 'UPPER CASE':
                result += extension.upper()
            case 'Title Case':
                result += extension.title()
            case 'Capitalize':
                result += extension.capitalize()
            case 'Custom extension':
                if self.evalue.text():
                    result += '.'
                    result += self.evalue.text()
        return result

    def deactivate_field(self, text: str, field: QLineEdit):
        """ Deactivates the transformation fields when specific option is chosen """
        if text.startswith('Custom'):
            field.setDisabled(False)
        else:
            field.setDisabled(True)


class RenameWindow(QMainWindow):
    def __init__(self):
        """ Initializes the main window and its components. """
        super().__init__()
        self.setWindowTitle("Qrename")
        self.resize(1000, 500)
        self.files = []
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        """ Creates the main window layout and widgets. """
        #create renamer central widget
        self.renamer = Renamer()
        self.setCentralWidget(self.renamer)
        #left dock for files management
        self.old_names = QListWidget()
        self.open_button = QPushButton("Open Files")
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.old_names)
        layout.addWidget(self.open_button)
        container.setLayout(layout)
        dock = QDockWidget('Selected Files')
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        #right dock for new name presentation
        self.new_names = QListWidget()
        self.rename_button = QPushButton("Rename Files")
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.new_names)
        layout.addWidget(self.rename_button)
        container.setLayout(layout)
        dock = QDockWidget('New Names')
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def setup_signals(self):
        """ Connects signals from the renamer and buttons to the main window. """
        self.renamer.ptype.textActivated.connect(self.compute_names)
        self.renamer.pvalue.textEdited.connect(self.compute_names)
        self.renamer.stype.textActivated.connect(self.compute_names)
        self.renamer.svalue.textEdited.connect(self.compute_names)
        self.renamer.ntype.textActivated.connect(self.compute_names)
        self.renamer.nvalue.textEdited.connect(self.compute_names)
        self.renamer.etype.textActivated.connect(self.compute_names)
        self.renamer.evalue.textEdited.connect(self.compute_names)
        self.renamer.digits.valueChanged.connect(self.compute_names)
        self.renamer.start.valueChanged.connect(self.compute_names)
        self.renamer.date.dateChanged.connect(self.compute_names)
        self.open_button.clicked.connect(self.open_files)
        self.rename_button.clicked.connect(self.rename_files)

    def open_files(self):
        """ Opens file dialog and adds selected files to the docks. """
        self.files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        self.old_names.clear()
        self.new_names.clear()
        for index, file in enumerate(self.files):
            self.old_names.addItem(os.path.basename(file))
            self.new_names.addItem(os.path.basename(self.renamer.transform(file, index)))

    def compute_names(self):
        """ Computes the new names for all files. """
        for index, file in enumerate(self.files):
            self.new_names.item(index).setText(self.renamer.transform(file, index))

    def rename_files(self):
        """ Renames files to the new names shown in the right dock. """
        answer = None
        new_files = list(self.files)
        for index, file in enumerate(self.files):
            new_name = os.path.join(os.path.dirname(file), self.renamer.transform(file, index))
            # Check if destination already exists
            if answer != QMessageBox.StandardButton.YesToAll and os.path.lexists(new_name):
                if answer == QMessageBox.StandardButton.NoToAll:
                    continue
                answer = QMessageBox.question(
                    self,
                    'File exists',
                    f'File {new_name} already exists, do you want to overwrite it?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.YesToAll |
                    QMessageBox.StandardButton.NoToAll | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes or answer == QMessageBox.StandardButton.YesToAll:
                # Rename the file
                try:
                    os.replace(file, new_name)
                except FileNotFoundError:
                    QMessageBox.critical(self, "Error", f"FileNotFoundError: The file '{file}' was not found.")
                except PermissionError:
                    QMessageBox.critical(self, 'Error', f"PermissionError: Permission denied when renaming the file '{file}'.")
                except IsADirectoryError:
                    QMessageBox.critical(self, 'Error', f"IsADirectoryError: '{file}' is a directory, not a file.")
                except OSError as e:
                    QMessageBox.critical(self, 'Error', f"OSError: An OS error occurred when renaming '{file}': {e}")
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f"Unexpected error when renaming '{file}': {e}")
                else:
                    new_files[index] = new_name
        # Update the file names in the docks
        self.files = new_files
        self.old_names.clear()
        self.new_names.clear()
        for index, file in enumerate(self.files):
            self.old_names.addItem(os.path.basename(file))
            self.new_names.addItem(os.path.basename(self.renamer.transform(file, index)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RenameWindow()
    window.show()
    sys.exit(app.exec())