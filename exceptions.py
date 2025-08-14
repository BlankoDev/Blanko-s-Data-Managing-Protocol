from .utils import ensure_class
from pathlib import Path

class BaseException(Exception):
    def __init__(self, path: str | Path):
            self.path = ensure_class(path, Path)

            print(f"file '{self.path}'")

class InvalidFile(BaseException):
    def __init__(self, path: str | Path, reason: str):
        super().__init__(path)

        self.reason = reason

        print("invalid 'bdm' file :", reason)

class VersionError(BaseException):
    def __init__(self, self_version: int, file_version: int, path: str | Path):
        super().__init__(path)

        self.self_version = self_version
        self.file_version = file_version

        print(f"incompatible 'bdm' file version '{file_version}' this version of bdmp is only compatible with varsion '{self_version}'")

class InvalidParent(BaseException):
    def __init__(self, expected_parent: int, given_parent: int, path: str | Path):
        super().__init__(path)

        self.expected_parent = expected_parent
        self.given_parent = given_parent

        print(f"Invalid parent '{given_parent}' expected '{expected_parent}'")