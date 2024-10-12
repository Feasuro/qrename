#!/usr/bin/env python

import sys, os

from PyQt6.QtCore import Qt, QCommandLineParser, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QDockWidget, QVBoxLayout,
                             QListWidget, QFileDialog, QPushButton, QMessageBox, QTabWidget)

from renamers import BasicRenamer, AdvancedRenamer
import resources


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
        tabs.addTab(self.b_renamer, self.tr("Basic Renamer"))
        tabs.addTab(self.a_renamer, self.tr("Advanced Renamer"))
        tabs.currentChanged.connect(self.set_renamer)
        self.setCentralWidget(tabs)
        #left dock for files management
        self.old_names = QListWidget()
        open_button = QPushButton(self.tr("Open Files"))
        open_button.clicked.connect(self.open_files)
        add_button = QPushButton(self.tr("Add Files"))
        add_button.clicked.connect(lambda: self.open_files(add=True))
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.old_names)
        layout.addWidget(open_button)
        layout.addWidget(add_button)
        container.setLayout(layout)
        dock = QDockWidget(self.tr("Selected Files"))
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        #right dock for new name presentation
        self.new_names = QListWidget()
        rename_button = QPushButton(self.tr("Rename Files"))
        rename_button.clicked.connect(self.rename_files)
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.new_names)
        layout.addWidget(rename_button)
        container.setLayout(layout)
        dock = QDockWidget(self.tr("New Names"))
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def setup_signals(self) -> None:
        """ Connects signals from the renamers to the main window. """
        self.b_renamer.ptype.currentTextChanged.connect(self.refresh_names)
        self.b_renamer.pvalue.textEdited.connect(self.refresh_names)
        self.b_renamer.stype.currentTextChanged.connect(self.refresh_names)
        self.b_renamer.svalue.textEdited.connect(self.refresh_names)
        self.b_renamer.ntype.currentTextChanged.connect(self.refresh_names)
        self.b_renamer.nvalue.textEdited.connect(self.refresh_names)
        self.b_renamer.etype.currentTextChanged.connect(self.refresh_names)
        self.b_renamer.evalue.textEdited.connect(self.refresh_names)
        self.b_renamer.digits.valueChanged.connect(self.refresh_names)
        self.b_renamer.start.valueChanged.connect(self.refresh_names)
        self.b_renamer.date.dateChanged.connect(self.refresh_names)
        self.b_renamer.dformat.currentTextChanged.connect(self.refresh_names)
        self.a_renamer.inreg.textEdited.connect(self.refresh_names)
        self.a_renamer.outreg.textEdited.connect(self.refresh_names)
        self.a_renamer.count.valueChanged.connect(self.refresh_names)

    def set_renamer(self, index: int) -> None:
        """ Sets the current renamer based on the selected tab. """
        if index == 0:
            self.renamer = self.b_renamer
        else: # index == 1
            self.renamer = self.a_renamer

    def open_files(self, add=False) -> None:
        """ Opens file dialog and adds selected files to the docks. """
        files , _ = QFileDialog.getOpenFileNames(self, self.tr("Select Files"), "", self.tr("All Files (*)"))
        if add:
            self.files.extend(files)
        else:
            self.files = files
        self.display_files()

    def display_files(self) -> None:
        """ Displays selected files in the left and right dock. """
        self.old_names.clear()
        self.new_names.clear()
        for index, file in enumerate(self.files):
            self.old_names.addItem(os.path.basename(file))
            self.new_names.addItem(self.renamer.transform(file, index))

    def refresh_names(self) -> None:
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
                    self.tr("File exists"),
                    self.tr("File {} already exists, do you want to overwrite it?").format(new_name),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.YesToAll |
                    QMessageBox.StandardButton.NoToAll | QMessageBox.StandardButton.No)
            if answer is None or answer == QMessageBox.StandardButton.Yes or answer == QMessageBox.StandardButton.YesToAll:
                # Rename the file
                try:
                    os.replace(file, new_name)
                except FileNotFoundError:
                    QMessageBox.critical(self, self.tr("Error"),
               self.tr("FileNotFoundError: The file '{}' was not found.").format(file))
                except PermissionError:
                    QMessageBox.critical(self, self.tr("Error"),
               self.tr("PermissionError: Permission denied when renaming the file '{}'.").format(file))
                except IsADirectoryError:
                    QMessageBox.critical(self, self.tr("Error"),
               self.tr("IsADirectoryError: '{}' is a directory, not a file.").format(file))
                except OSError as e:
                    QMessageBox.critical(self, self.tr("Error"),
               self.tr("OSError: An OS error occurred when renaming '{}': {}").format(file, e))
                except Exception as e:
                    QMessageBox.critical(self, self.tr("Error"),
               self.tr("Unexpected error when renaming '{}': {}").format(file, e))
                else:
                    new_files[index] = new_name
        # Update the file names in the docks
        self.files = new_files
        self.display_files()


class ArgumentParser(QCommandLineParser):
    """ Parses command-line arguments. """
    tr = lambda obj, string: QApplication.translate(type(obj).__name__, string)
    def __init__(self, *args, **kwargs):
        """ Initializes the argument parser options. """
        super().__init__(*args, **kwargs)
        self.setApplicationDescription(self.tr("Rename files based on user-provided parameters."))
        self.addHelpOption()
        self.addVersionOption()
        self.addPositionalArgument(self.tr("file"),
                                   self.tr("files to be renamed or containing directory path"),
                                   self.tr("[directory/file1 file2 ...]"))

    def file_list(self) -> list:
        """ Returns a list of file paths from positional arguments. """
        if self.positionalArguments():
            if os.path.isdir(self.positionalArguments()[0]):
                return [os.path.abspath(path) for path in os.listdir(self.positionalArguments()[0])]
            return [os.path.abspath(path) for path in self.positionalArguments() if os.path.lexists(path)]
        return []

    def check_args(self, app: QApplication) -> None:
        """ Checks if positional arguments are valid paths. """
        self.process(app)
        if self.positionalArguments():
            for arg in self.positionalArguments():
                if not os.path.lexists(arg):
                    print(self.tr("Error: File '{}' does not exist.\n").format(arg))
                    self.showHelp(exitCode=1)


if __name__ == "__main__":
    # Instantiate the application
    app = QApplication(sys.argv)
    app.setApplicationName("Qrename")
    app.setApplicationVersion("v1.1")
    # Load translations
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale(), "qtbase", "_", path):
        app.installTranslator(translator)
    translator = QTranslator(app)
    if translator.load(QLocale(), "qrename", "_", ":/i18n"):
        app.installTranslator(translator)
    # Parse command line arguments and show window
    parser = ArgumentParser()
    parser.check_args(app)
    window = RenameWindow()
    window.files = parser.file_list()
    window.display_files()
    window.show()
    sys.exit(app.exec())