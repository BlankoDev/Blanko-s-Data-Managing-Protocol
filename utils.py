"""
A module full of useful class and functions, used in many projects by Blanko
"""

from pathlib import Path
from os.path import getsize as path_getsize


def is_path(string: str):
    forbidden_chars = '/\\*?:"<>|\n\r'
    for forbidden_char in forbidden_chars:
        if forbidden_char in string:return False
    return True

def ensure_class(obj, _class):
    if not isinstance(obj, _class): return _class(obj)
    else: return obj


def get_size(path : str | Path):
    path = ensure_class(path, Path)
    if path.is_file(): return path_getsize(path)
    if path.is_symlink(): return 0
    if path.is_dir():
        size = 0
        for item in path.iterdir():
            size += get_size(item)
        return size
    else:return 0


