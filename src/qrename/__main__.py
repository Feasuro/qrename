""" Application entry point. This module handles commandline arguments,
app language setting, and displaying a window. """
import sys
import os

from PyQt6.QtCore import QCommandLineParser, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtWidgets import QApplication

from qrename import __version__
from qrename.mainwindow import RenameWindow


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


def main() -> int:
    """ Main program's entry point. """
    # Instantiate the application
    app = QApplication(sys.argv)
    app.setApplicationName("Qrename")
    app.setApplicationVersion(__version__)
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
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())