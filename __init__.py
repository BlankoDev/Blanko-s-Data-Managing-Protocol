"""
Blanko's Data Managing Protocol (BDMP)
======================================

This module provides classes and functions for managing structured data and associated files
using the BDMP format (version 2). It supports reading, writing, and manipulating hierarchical
data (sections and items), as well as storing and retrieving binary files (such as images)
within a single archive.

Classes:
    - Item: Represents an individual item with content, image, and metadata.
    - Section: Represents a collection of items.
    - Data: Represents the main data structure containing all sections.
    - Info: Stores file information and metadata.
    - BDMFile: Main interface for reading/writing BDMP files.

Exceptions:
    - InvalidFile: Raised for invalid BDMP files.
    - VersionError: Raised for version incompatibility.
    - InvalidParent: Raised for parent-child relationship errors.

Dependencies:
    - Python standard library: os, pathlib, pickle, shutil, tempfile, uuid, zipfile, io, copy
    - PIL (Pillow): For image handling
    - utils, class_utils: Project-specific utilities
    - exceptions: Project-specific exceptions
"""

from .core import Item, Section, Data, Info, BDMFile
from .exceptions import InvalidFile, VersionError, InvalidParent

__all__ = [
    "Item",
    "Section",
    "Data",
    "Info",
    "BDMFile",
    "InvalidFile",
    "VersionError",
    "InvalidParent",
]

__version__ = "2.0.0"
__author__ = "BlankoDev"
__license__ = "MIT"
__maintainer__ = "BlankoDev"

__docformat__ = "restructuredtext en"
__title__ = "bdmp"
__description__ = "Blanko's Data Managing Protocol (BDMP) for structured data management"
