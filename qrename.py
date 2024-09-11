#!/usr/bin/env python

import sys, os

from PyQt6.QtCore import Qt, QCommandLineParser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QDockWidget, QVBoxLayout,
                             QListWidget, QFileDialog, QPushButton, QMessageBox, QTabWidget)

from renamers import BasicRenamer, AdvancedRenamer

class RenameWindow(QMainWindow):
    """ The main window for renaming files program. """
    def __init__(self):
        """ Initializes the main window and its components. """
        super().__init__()
        self.setWindowTitle("Qrename")
        self.resize(1000, 500)
        self.files = []
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self) -> None:
        """ Creates the main window layout and widgets. """
        #create renamer central widget
        self.b_renamer = BasicRenamer()
        self.a_renamer = AdvancedRenamer()
        self.renamer = self.b_renamer
        tabs = QTabWidget()
        tabs.addTab(self.b_renamer, "Basic Renamer")
        tabs.addTab(self.a_renamer, "Advanced Renamer")
        tabs.currentChanged.connect(self.set_renamer)
        self.setCentralWidget(tabs)
        #left dock for files management
        self.old_names = QListWidget()
        open_button = QPushButton("Open Files")
        open_button.clicked.connect(self.open_files)
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.old_names)
        layout.addWidget(open_button)
        container.setLayout(layout)
        dock = QDockWidget('Selected Files')
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        #right dock for new name presentation
        self.new_names = QListWidget()
        rename_button = QPushButton("Rename Files")
        rename_button.clicked.connect(self.rename_files)
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.new_names)
        layout.addWidget(rename_button)
        container.setLayout(layout)
        dock = QDockWidget('New Names')
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def setup_signals(self) -> None:
        """ Connects signals from the renamers to the main window. """
        self.b_renamer.ptype.textActivated.connect(self.compute_names)
        self.b_renamer.pvalue.textEdited.connect(self.compute_names)
        self.b_renamer.stype.textActivated.connect(self.compute_names)
        self.b_renamer.svalue.textEdited.connect(self.compute_names)
        self.b_renamer.ntype.textActivated.connect(self.compute_names)
        self.b_renamer.nvalue.textEdited.connect(self.compute_names)
        self.b_renamer.etype.textActivated.connect(self.compute_names)
        self.b_renamer.evalue.textEdited.connect(self.compute_names)
        self.b_renamer.digits.valueChanged.connect(self.compute_names)
        self.b_renamer.start.valueChanged.connect(self.compute_names)
        self.b_renamer.date.dateChanged.connect(self.compute_names)

    def set_renamer(self, index: int) -> None:
        """ Sets the current renamer based on the selected tab. """
        if index == 0:
            self.renamer = self.b_renamer
        else:
            self.renamer = self.a_renamer

    def open_files(self) -> None:
        """ Opens file dialog and adds selected files to the docks. """
        self.files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        self.display_files()

    def display_files(self) -> None:
        """ Displays selected files in the left and right dock. """
        self.old_names.clear()
        self.new_names.clear()
        for index, file in enumerate(self.files):
            self.old_names.addItem(os.path.basename(file))
            self.new_names.addItem(self.renamer.transform(file, index))

    def compute_names(self) -> None:
        """ Computes the new names for all files. """
        for index, file in enumerate(self.files):
            self.new_names.item(index).setText(self.renamer.transform(file, index))

    def rename_files(self) -> None:
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
        self.display_files()


class ArgumentParser(QCommandLineParser):
    """ Parses command-line arguments. """
    def __init__(self, *args, **kwargs):
        """ Initializes the argument parser options. """
        super().__init__(*args, **kwargs)
        self.setApplicationDescription("Rename files based on user-provided parameters.")
        self.addHelpOption()
        self.addVersionOption()
        self.addPositionalArgument('file', 'files to be renamed or directory path', '[directory/file file ...]')

    def file_list(self) -> list:
        """ Returns a list of file paths from positional arguments. """
        if self.positionalArguments():
            if os.path.isdir(self.positionalArguments()[0]):
                return [os.path.abspath(path) for path in os.listdir(self.positionalArguments()[0])]
            return [os.path.abspath(path) for path in self.positionalArguments() if os.path.lexists(path)]
        return []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Qrename")
    app.setApplicationVersion("v1.1")
    parser = ArgumentParser()
    parser.process(app)
    window = RenameWindow()
    window.files = parser.file_list()
    window.display_files()
    window.show()
    sys.exit(app.exec())