"""This module contains abstraction and implementation of the widgets handling user controls
and names transformation logic."""
import os
import re
from abc import ABC, abstractmethod

from PyQt6.QtCore import QDate, QCoreApplication, QLocale
from PyQt6.QtWidgets import (QWidget, QGridLayout, QFormLayout, QGroupBox, QLabel, QLineEdit,
                             QComboBox, QSpinBox, QDateEdit)


class MetaRenamer(type(QWidget), type(ABC)):
    """ Metaclass for creating renamer widgets. """
    pass

class Renamer(QWidget, ABC, metaclass=MetaRenamer):
    """ Abstract base class for renaming widgets. """
    @abstractmethod
    def transform(self, path: str, index: int) -> str:
        """ Transforms a filename based on the user-provided parameters.

        Args:
            path (str): The absolute path of a file.
            index (int): The index of the current file being renamed.
        
        Returns:
            str: The transformed filename (not a path)."""
        raise NotImplementedError


class BasicRenamer(Renamer):
    """ A widget for simple renaming with controls for prefix, suffix, name, extension,
    number, and date/time. """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setup_controls()
        self.setup_layout()

    def setup_layout(self) -> None:
        """ Sets up the layout for the renamer window. """
        # Basic controls
        layout = QGridLayout()
        layout.addWidget(QLabel(self.tr("Prefix:")), 0, 0)
        layout.addWidget(self.ptype, 0, 1)
        layout.addWidget(self.pvalue, 0, 2)
        layout.addWidget(QLabel(self.tr("Suffix:")), 1, 0)
        layout.addWidget(self.stype, 1, 1)
        layout.addWidget(self.svalue, 1, 2)
        layout.addWidget(QLabel(self.tr("Name:")), 2, 0)
        layout.addWidget(self.ntype, 2, 1)
        layout.addWidget(self.nvalue, 2, 2)
        layout.addWidget(QLabel(self.tr("Extension:")), 3, 0)
        layout.addWidget(self.etype, 3, 1)
        layout.addWidget(self.evalue, 3, 2)
        # Number
        group = QGroupBox(self.tr("Number"))
        grouplayout = QFormLayout()
        grouplayout.addRow(self.tr("Start number:"), self.start)
        grouplayout.addRow(self.tr("Number of digits:"), self.digits)
        group.setLayout(grouplayout)
        layout.addWidget(group, 4, 0, 1, 3)
        # Date & Time
        group = QGroupBox(self.tr("Date and Time"))
        grouplayout = QFormLayout()
        grouplayout.addRow(self.tr("Date:"), self.date)
        grouplayout.addRow(self.tr("Date format:"), self.dformat)
        group.setLayout(grouplayout)
        layout.addWidget(group, 5, 0, 1, 3)
        # set layout
        self.setLayout(layout)

    def setup_controls(self) -> None:
        """ Sets up the transformation widgets for the selected files. """
        # Prefix
        self.pvalue = QLineEdit(self)
        self.ptype = QComboBox(self)
        self.ptype.addItems([self.tr("Custom"), self.tr("Number"), self.tr("Date")])
        self.ptype.currentIndexChanged.connect(lambda index: self.deactivate_field(index, self.pvalue))
        # Suffix
        self.svalue = QLineEdit(self)
        self.stype = QComboBox(self)
        self.stype.addItems([self.tr("Custom"), self.tr("Number"), self.tr("Date")])
        self.stype.currentIndexChanged.connect(lambda index: self.deactivate_field(index, self.svalue))
        # Name
        self.nvalue = QLineEdit(self)
        self.nvalue.setDisabled(True)
        self.ntype = QComboBox(self)
        self.ntype.addItems([self.tr("Custom name"), self.tr("Source name"),self.tr("lower case"),
                             self.tr("UPPER CASE"), self.tr("Title Case"), self.tr("Capitalize text")])
        self.ntype.setCurrentIndex(1)
        self.ntype.currentIndexChanged.connect(lambda index: self.deactivate_field(index, self.nvalue))
        # Extension
        self.evalue = QLineEdit(self)
        self.evalue.setDisabled(True)
        self.etype = QComboBox(self)
        self.etype.addItems([self.tr("Custom extension"), self.tr("Source extension"), self.tr("lower case"),
                             self.tr("UPPER CASE"), self.tr("Title Case"), self.tr("Capitalize text")])
        self.etype.setCurrentIndex(1)
        self.etype.currentIndexChanged.connect(lambda index: self.deactivate_field(index, self.evalue))
        # Number
        self.digits = QSpinBox(self)
        self.start = QSpinBox(self)
        self.start.setMaximum(2147483647)
        # Date
        self.date = QDateEdit(QDate().currentDate(), self)
        self.date.setDisplayFormat('dd-MM-yyyy')
        self.date.setCalendarPopup(True)
        self.dformat = QComboBox(self)
        self.dformat.addItems(['dd-MM-yyyy', 'dd.MM.yyyy', 'dd-MM-yy', 'dd.MM.yy', 'ddMMMyyyy',
                               'ddMMMMyyyy', 'dd MMMM yyyy'])
        self.dformat.currentTextChanged.connect(self.date.setDisplayFormat)

    def transform(self, path: str, index: int) -> str:
        """ Performs the string transformation based on the selected options. """
        result = ''
        match self.ptype.currentIndex():
            case 0:    # Custom
                result += self.pvalue.text()
            case 1:    # Number
                result += str(self.start.value() + index).zfill(self.digits.value())
            case 2:    # Date
                result += QLocale.system().toString(self.date.date(), self.date.displayFormat())
        basename = os.path.splitext(os.path.basename(path))[0]
        match self.ntype.currentIndex():
            case 0:    # Custom name
                result += self.nvalue.text()
            case 1:    # Source name
                result += basename
            case 2:    # lower case
                result += basename.lower()
            case 3:    # UPPER CASE
                result += basename.upper()
            case 4:    # Title Case
                result += basename.title()
            case 5:    # Capitalize text
                result += basename.capitalize()
        match self.stype.currentIndex():
            case 0:    # Custom
                result += self.svalue.text()
            case 1:    # Number
                result += str(self.start.value() + index).zfill(self.digits.value())
            case 2:    # Date
                result += QLocale.system().toString(self.date.date(), self.date.displayFormat())
        extension = os.path.splitext(os.path.basename(path))[1]
        match self.etype.currentIndex():
            case 0:    # Custom extension
                if self.evalue.text():
                    result += '.'
                    result += self.evalue.text()
            case 1:    # Source extension
                result += extension
            case 2:    # lower case
                result += extension.lower()
            case 3:    # UPPER CASE
                result += extension.upper()
            case 4:    # Title Case
                result += extension.title()
            case 5:    # Capitalize
                result += extension.capitalize()
        return result

    def deactivate_field(self, index: int, field: QLineEdit) -> None:
        """ Deactivates the transformation fields when specific option is chosen """
        if not index: # Custom options are under index 0
            field.setDisabled(False)
        else:
            field.setDisabled(True)


class AdvancedRenamer(Renamer):
    """ A widget for advanced renaming based on provided regular expressions. """
    def __init__(self, *args, **kwargs) -> None:
        """ Initializes the advanced renamer window. """
        super().__init__(*args, **kwargs)
        self.setup_controls()
        self.setup_layout()

    def setup_controls(self) -> None:
        """ Sets up fields for the transformation regular expressions. """
        self.inreg = QLineEdit(self)
        self.outreg = QLineEdit(self)
        self.count = QSpinBox(self)

    def setup_layout(self) -> None:
        """ Sets up the layout for the advanced renamer window. """
        layout = QFormLayout()
        layout.addRow(self.tr("Pattern regular expression:"), self.inreg)
        layout.addRow(self.tr("Replacement:"), self.outreg)
        layout.addRow(self.tr("Maximal number of replacements:"), self.count)
        group = QGroupBox(self.tr('Hints:'))
        grouplayout = QFormLayout(group)
        for pattern, meaning in self.hints().items():
            grouplayout.addRow(QLabel(pattern), QLabel(meaning))
        layout.addRow(group)
        self.setLayout(layout)

    def hints(self) -> dict:
        """ Short reference on regular expressions to display. """
        return {
            r'\w': self.tr(r'Match a single word character a-z, A-Z, 0-9, and underscore (_)'),
            r'\d': self.tr(r'Match a single digit 0-9'),
            r'\s': self.tr(r'Match whitespace including \t, \n, and \r and space character'),
            r'.':  self.tr(r'Match any character except the newline'),
            r'\W': self.tr(r'Match a character except for a word character'),
            r'\D': self.tr(r'Match a character except for a digit'),
            r'\S': self.tr(r'Match a single character except for a whitespace character'),
            r'^':  self.tr(r'Match at the beginning of a string'),
            r'$':  self.tr(r'Match at the end of a string'),
            r'\b': self.tr(r'Match a position defined as a word boundary'),
            r'\B': self.tr(r'Match a position that is not a word boundary'),
            r'(X)':self.tr(r'Capture the X in the group'),
            r'\N': self.tr(r'Reference the capturing group #N'),
            r'*':  self.tr(r'Match its preceding element zero or more times. *? for lazy version.'),
            r'+':  self.tr(r'Match its preceding element one or more times. +? for lazy version.'),
            r'?':  self.tr(r'Match its preceding element zero or one time. ?? for lazy version.'),
            r'{n}':self.tr(r'Match its preceding element exactly n times. {n}? for lazy version.'),
            r'{n , }':  self.tr(r'Match its preceding element at least n times. {n,}? for lazy version.'),
            r'{n , m}': self.tr(r'Match its preceding element from n to m times {n , m}? for lazy version.'),
        }

    def transform(self, path: str, index: int) -> str:
        """ Performs the string transformation based on the provided regular expressions. """
        try:
            return re.sub(self.inreg.text(), self.outreg.text(), os.path.basename(path),
                          count=self.count.value())
        except re.error as e:
            print(self.tr("Warning: Invalid regular expression: {}").format(e))
            return os.path.basename(path)
