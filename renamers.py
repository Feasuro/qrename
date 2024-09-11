#!/usr/bin/env python

import os
import re

from abc import ABC, abstractmethod
from PyQt6.QtCore import QDate
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
    """ A widget forsimple renaming with controls for prefix, suffix, name, extension,
    number, and date/time. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_controls()
        self.setup_layout()

    def setup_layout(self) -> None:
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
        grouplayout.addRow('Date format:', self.dformat)
        group.setLayout(grouplayout)
        layout.addWidget(group, 5, 0, 1, 3)
        # set layout
        self.setLayout(layout)

    def setup_controls(self) -> None:
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
        self.date = QDateEdit(QDate().currentDate(), self)
        self.date.setDisplayFormat('dd-MM-yyyy')
        self.date.setCalendarPopup(True)
        self.dformat = QComboBox(self)
        self.dformat.addItems(['dd-MM-yyyy', 'dd.MM.yyyy', 'dd-MM-yy', 'dd.MM.yy', 'ddMMMyyyy', 'ddMMMMyyyy'])
        self.dformat.currentTextChanged.connect(self.date.setDisplayFormat)

    def transform(self, path: str, index: int) -> str:
        """ Performs the string transformation based on the selected options. """
        result = ''
        match self.ptype.currentText():
            case 'Number':
                result += str(self.start.value() + index).zfill(self.digits.value())
            case 'Date':
                result += self.date.date().toString(self.date.displayFormat())
            case 'Custom':
                result += self.pvalue.text()
        basename = os.path.splitext(os.path.basename(path))[0]
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
                result += self.date.date().toString(self.date.displayFormat())
            case 'Custom':
                result += self.svalue.text()
        extension = os.path.splitext(os.path.basename(path))[1]
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

    def deactivate_field(self, text: str, field: QLineEdit) -> None:
        """ Deactivates the transformation fields when specific option is chosen """
        if text.startswith('Custom'):
            field.setDisabled(False)
        else:
            field.setDisabled(True)


class AdvancedRenamer(Renamer):
    """ A widget for advanced renaming based on provided regular expressions. """
    def __init__(self, *args, **kwargs):
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
        layout.addRow('Pattern regular expression:', self.inreg)
        layout.addRow('Replacement', self.outreg)
        layout.addRow('Maximal number of replacements', self.count)
        self.setLayout(layout)

    def transform(self, path: str, index: int) -> str:
        """ Performs the string transformation based on the provided regular expressions. """
        try:
            return re.sub(self.inreg.text(), self.outreg.text(), os.path.basename(path), count=self.count.value())
        except re.error as e:
            print(f"Warning: Invalid regular expression: {e}")
            return os.path.basename(path)
