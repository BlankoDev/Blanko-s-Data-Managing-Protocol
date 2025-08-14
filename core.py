from os import remove
from pathlib import Path
from pickle import dumps as pickle_dumps
from pickle import loads as pickle_loads
from shutil import rmtree
from tempfile import gettempdir
from uuid import uuid1
from zipfile import ZipFile, is_zipfile
from io import UnsupportedOperation
from PIL import Image
from copy import deepcopy as obj_deepcopy

from .utils import ensure_class
from .class_utils import HierarchizedObject

from .exceptions import InvalidFile, VersionError, InvalidParent

VERSION = 2
TEMPDIR = Path(gettempdir())


class Item(HierarchizedObject):
    """
    Represents an item with a title, content, image, level, and optional data.
    """
    def __init__(self, parent, title: str, content: str, level: int, data: dict | None = None, image_id: str | None = None, image: str | None = None):
        """
        Initialize an Item instance.

        Args:
            parent: The parent object.
            title (str): The title of the item.
            content (str): The content of the item.
            image_id (str): The ID of the associated image.
            image (str | None): Same as image_id, for compatibility. If provided, it will override image_id.
            level (int): The level of the item.
            data (dict, optional): Additional data for the item.
        """
        super().__init__(parent)

        self.title = title
        self.content = content
        self.image_id = image_id if image_id is not None else image
        if image_id is None and image is None: raise ValueError("image_id or image must be provided")

        self.level = level
        self.data = data

    
    def to_dict(self):
        """
        Convert the item to a dictionary representation.

        Returns:
            dict: Dictionary containing item data.
        """
        data = {
            "title" : self.title,
            "content" : self.content,
            "image_id" : self.image_id,
            "level" : self.level
        }
        if self.data is not None: data["data"] = self.data
        return data
    
    def add_data(self, name: str, value):
        """
        Add a key-value pair to the item's data.

        Args:
            name (str): The key name.
            value: The value to add.

        Raises:
            UnsupportedOperation: If the parent is not writable.
        """
        if not self._parent.writable: raise UnsupportedOperation("Not writable")
        if self.data is None: self.data = {}
        self.data[name] = value

    def remove_data(self, name: str):
        """
        Remove a key from the item's data.

        Args:
            name (str): The key to remove.

        Raises:
            UnsupportedOperation: If the parent is not writable.
            ValueError: If the key does not exist or no data is present.
        """
        if not self._parent.writable: raise UnsupportedOperation("Not writable")
        if name not in self.data: raise ValueError(f"data '{name}' do not exists")
        if self.data is None: raise ValueError("No data yet")
        del(self.data[name])
        if len(self.data) == 0: self.data = None

    def get_image(self):
        """
        Get the item's image as a PIL Image object.

        Returns:
            Image: The image object.
        """
        io = self._parent.open_file(self.image_id, "rb")
        return Image.open(io)
    
    def export_image(self, path: str | Path):
        """
        Export the item's image to a file.

        Args:
            path (str | Path): The destination path.
        """
        path = ensure_class(path, Path)
        data = self._parent.info.read_file(self.image_id)
        path.write_bytes(data)

class Section(HierarchizedObject):
    """
    Represents a section containing multiple items.
    """
    def __init__(self, parent, type: str, description: str, content: dict):
        """
        Initialize a Section instance.

        Args:
            parent: The parent object.
            type (str): The type of the section.
            description (str): The section description.
            content (dict): Dictionary of items.
        """
        super().__init__(parent)

        self.type = type
        self.description = description
        self._content : dict[str, Item] = {}
        for item_key in content:
            item = content[item_key]
            self._content[item_key] = Item(parent, **item)
    
    def add_item(self, title: str, content: str, image_id: str, level: int, name: str = None, data: dict | None = None):
        """
        Add an item to the section.

        Args:
            title (str): Item title.
            content (str): Item content.
            image_id (str): Image ID.
            level (int): Item level.
            name (str, optional): Item key name.
            data (dict, optional): Additional item data.
        """
        if name is None: name = uuid1().hex
        self[name] = Item(self._parent, title, content, image_id, level, data)
    
    def remove_item(self, name: str):
        """
        Remove an item from the section.

        Args:
            name (str): The key of the item to remove.

        Raises:
            ValueError: If the item does not exist.
        """
        if name not in self: raise ValueError(f"Item with name '{name}' do not exist")
        del(self[name])

    def to_dict(self):
        """
        Convert the section to a dictionary representation.

        Returns:
            dict: Dictionary containing section data.
        """
        data = {}
        data["type"] = self.type
        data["description"] = self.description
        data["content"] = {}

        for item_key in self._content: data["content"][item_key] = self._content[item_key].to_dict()
        return data

    def __len__(self):
        """
        Get the number of items in the section.

        Returns:
            int: Number of items.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        return self._content.__len__()

    def __iter__(self):
        """
        Iterate over the section's items.

        Returns:
            Iterator: Iterator over item keys.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        return self._content.__iter__()
    
    def __contains__(self, key: str):
        """
        Check if an item exists in the section.

        Args:
            key (str): Item key.

        Returns:
            bool: True if exists, False otherwise.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        return self._content.__contains__(key)
    
    def __getitem__(self, key: str) -> Item:
        """
        Get an item by key.

        Args:
            key (str): Item key.

        Returns:
            Item: The item object.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        return self._content.__getitem__(key)
    
    def __delitem__(self, key: str):
        """
        Delete an item by key.

        Args:
            key (str): Item key.

        Raises:
            UnsupportedOperation: If the parent is not writable.
        """
        if not self._parent.writable: raise UnsupportedOperation("Not writable")
        self._content.__delitem__(key)

    def __setitem__(self, key: str, value: Item):
        """
        Set an item in the section.

        Args:
            key (str): Item key.
            value (Item): The item object.

        Raises:
            UnsupportedOperation: If the parent is not writable.
            InvalidParent: If the item's parent does not match.
        """
        if not self._parent.writable: raise UnsupportedOperation("Not writable")
        if value._parent != self._parent: raise InvalidParent(self._parent, value._parent, self._parent.path)
        self._content.__setitem__(key, value) 

class Data(HierarchizedObject):
    """
    Represents the main data structure containing all sections.
    """
    DEFAULT = {"version" : VERSION, "sections" : {}}
    def __init__(self, parent, sections: dict):
        """
        Initialize a Data instance.

        Args:
            parent: The parent object.
            sections (dict): Dictionary of sections.
        """
        super().__init__(parent)
        self._sections : dict[str, Section] = {}
        for section_key in sections:
            section = sections[section_key]
            self._sections[section_key] = Section(parent, **section)
    
    def add_section(self, name: str, type: str, description: str):
        """
        Add a section to the data.

        Args:
            name (str): Section key.
            type (str): Section type.
            description (str): Section description.
        """
        self[name] = Section(self._parent, type, description, {})

    def __len__(self):
        """
        Get the total number of items in all sections.

        Returns:
            int: Total number of items.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        length = 0
        for key in self: length += len(self[key])
        return length


    def __iter__(self):
        """
        Iterate over the section keys.

        Returns:
            Iterator: Iterator over section keys.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        return self._sections.__iter__()
    
    def __contains__(self, key: str):
        """
        Check if a section exists.

        Args:
            key (str): Section key.

        Returns:
            bool: True if exists, False otherwise.
        """
        return self._sections.__contains__(key)
    
    def __getitem__(self, key: str) -> Section:
        """
        Get a section by key.

        Args:
            key (str): Section key.

        Returns:
            Section: The section object.

        Raises:
            UnsupportedOperation: If the parent is not readable.
        """
        if not self._parent.readable: raise UnsupportedOperation("Not readable")
        return self._sections.__getitem__(key)
    
    def __delitem__(self, key: str):
        """
        Delete a section by key.

        Args:
            key (str): Section key.

        Raises:
            UnsupportedOperation: If the parent is not writable.
        """
        if not self._parent.writable: raise UnsupportedOperation("Not writable")
        self._sections.__delitem__(key)

    def __setitem__(self, key: str, value: Section):
        """
        Set a section in the data.

        Args:
            key (str): Section key.
            value (Section): The section object.

        Raises:
            UnsupportedOperation: If the parent is not writable.
            InvalidParent: If the section's parent does not match.
        """
        if not self._parent.writable: raise UnsupportedOperation("Not writable")
        if value._parent != self._parent: raise InvalidParent(self._parent, value._parent, self._parent.path)
        self._sections.__setitem__(key, value) 

    def export_data(self):
        """
        Export the data as a pickled bytes object.

        Returns:
            bytes: Pickled data.
        """
        data = obj_deepcopy(self.DEFAULT)
        for section_key in self._sections: data["sections"][section_key] = self._sections[section_key].to_dict()
        
        data = pickle_dumps(data)
        return data
    
    @classmethod
    def import_data(cls, data: bytes, parent):
        """
        Import data from pickled bytes.

        Args:
            data (bytes): Pickled data.
            parent: The parent object.

        Returns:
            Data: The Data instance.

        Raises:
            InvalidFile: If the data is invalid.
            VersionError: If the version is incompatible.
        """
        data = pickle_loads(data)
        if not isinstance(data, dict): raise InvalidFile(parent.path, "Invalid 'data' file")

        if data["version"] > VERSION: raise VersionError(VERSION, data["version"], parent.path)
        del(data["version"])
        return cls(parent, data["sections"])
    

class Info(HierarchizedObject):
    """
    Represents file information and metadata.
    """
    DEFAULT = {"version" : VERSION, "files" : {}, "name" : "NoName"}
    def __init__(self, parent, name: str, files: dict):
        """
        Initialize an Info instance.

        Args:
            parent: The parent object.
            name (str): The name of the info.
            files (dict): Dictionary of file IDs to paths.
        """
        super().__init__(parent)
        self.name = name
        self.files : dict[str, Path] = {}

        for file_id in files:
            file = files[file_id]
            self.files[file_id] = Path(file)
    
    
    def export_data(self):
        """
        Export the info as a pickled bytes object.

        Returns:
            bytes: Pickled info data.
        """
        data = obj_deepcopy(self.DEFAULT)
        data["name"] = self.name

        for file_id in self.files: data["files"][file_id] = str(self.files[file_id])
        
        data = pickle_dumps(data)
        return data
    
    @classmethod
    def import_data(cls, data: bytes, parent):
        """
        Import info from pickled bytes.

        Args:
            data (bytes): Pickled info data.
            parent: The parent object.

        Returns:
            Info: The Info instance.

        Raises:
            InvalidFile: If the info is invalid.
            VersionError: If the version is incompatible.
        """
        data = pickle_loads(data)
        if not isinstance(data, dict): raise InvalidFile(parent.path, "Invalid 'info' file")

        if data["version"] > VERSION: raise VersionError(VERSION, data["version"], parent.path)
        del(data["version"])
        return cls(parent, data["name"], data["files"])


class BDMFile:
    """
    Main class for managing BDM files (Blanko's Data Managing Protocol).
    """
    REQUIRED_CONTENT = ("info", "data",)

    def __init__(self, path: str | Path, mode: str = "r"):
        """
        Initialize a BDMFile instance.

        Args:
            path (str | Path): Path to the BDM file.
            mode (str): File mode ('r', 'w', or 'r+').

        Raises:
            ValueError: If the mode is invalid.
            FileNotFoundError: If the file does not exist in read mode.
        """
        self.path = ensure_class(path, Path)

        if mode not in ("w", "r", "r+"): raise ValueError(f"Invalid or incompatible mode {mode}")
        self.mode = mode

        self.readable = "r" in mode
        self.writable = mode in ("w", "r+")

        exists = self.path.exists()
        if exists: self._check_validity()
        if not exists and mode == "r": raise FileNotFoundError(str(self.path))

        if self.writable: self._setup_temp_env()

        if not exists:
            self.info = Info(self, Info.DEFAULT["name"], Info.DEFAULT["files"])
            self.data = Data(self, Data.DEFAULT["sections"])
        else: self._load_data()
        
    
    def save(self, path: str | Path | None = None):
        """
        Save the BDM file to disk.

        Args:
            path (str | Path | None): Optional path to save to.

        Raises:
            UnsupportedOperation: If not writable.
            Exception: If an error occurs during saving.
        """
        if not self.writable: raise UnsupportedOperation("Not writable")
        if path is None:path = self.path
        else: ensure_class(path, Path)


        if path.exists(): old_file = path.rename(path.parent / (path.name + ".old"))
        else: old_file = None

        try:
            zip_file = ZipFile(path, "w")

            data = self.data.export_data()
            zip_file.writestr("data", data)

            info = self.info.export_data()
            zip_file.writestr("info", info)

            for file_id in self.info.files:
                file = self.info.files[file_id]
                arcname = f"files/{file}"
                temp_path = self._internal_files_dir / file
                zip_file.write(temp_path, arcname)
            
            if old_file is not None: remove(old_file)
        except Exception as err:
            if path.exists(): remove(path)
            if old_file is not None: old_file.rename(path)

            raise err
    
    def add_file(self, path: str | Path, file_id: str, internal_name : str | None = None):
        """
        Add a file to the BDM archive.

        Args:
            path (str | Path): Path to the file.
            file_id (str): File identifier.
            internal_name (str, optional): Internal name for the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            FileExistsError: If the file_id already exists.
            UnsupportedOperation: If not writable.
        """
        path = ensure_class(path, Path)
        if not path.exists(): raise FileNotFoundError(str(path))
        if file_id in self.info.files: raise FileExistsError(file_id)
        if not self.writable: raise UnsupportedOperation("Not writable")

        if "." in path.name: ext = "." + path.name.split(".")[-1]
        else: ext = ""

        if internal_name is None: internal_name = f'{uuid1().hex}{ext}'
        self.info.files[file_id] = internal_name

        data = path.read_bytes()
        self.write_file(file_id, data)
    
    def read_file(self, file_id: str):
        """
        Read a file from the BDM archive.

        Args:
            file_id (str): File identifier.

        Returns:
            bytes: File data.

        Raises:
            UnsupportedOperation: If not readable.
        """
        if self.mode == "r+":
            path = self._internal_files_dir / self.info.files[file_id]
            data = path.read_bytes()
        elif self.readable: 
            zip_file = ZipFile(self.path)
            data = zip_file.read(f"files/{self.info.files[file_id]}")
            zip_file.close()
        else: raise UnsupportedOperation(f"Not readable")
        
        return data
    
    def write_file(self, file_id: str, data):
        """
        Write data to a file in the BDM archive.

        Args:
            file_id (str): File identifier.
            data: Data to write.

        Raises:
            UnsupportedOperation: If not writable.
        """
        if not self.writable: raise UnsupportedOperation(f"Not writable")
        
        path = self._internal_files_dir / self.info.files[file_id]
        path.write_bytes(data)

    def open_file(self, file_id: str, mode: str = "r"):
        """
        Open a file in the BDM archive.

        Args:
            file_id (str): File identifier.
            mode (str): File mode.

        Returns:
            file object: Opened file object.

        Raises:
            UnsupportedOperation: If not readable or writable as required.
        """
        if "r" in mode and not self.readable: raise UnsupportedOperation(f"Not readable")
        if not self.writable and mode in ("w", "r+", "a"): raise UnsupportedOperation(f"Not writable")

        if self.writable:
            path = self._internal_files_dir / self.info.files[file_id]
            io = path.open(mode)
        elif self.readable:
            zip_file = ZipFile(self.path)
            io = zip_file.open(f"files/{self.info.files[file_id]}")
            zip_file.close()
        
        return io
    
    def close(self):
        """
        Close the BDM file and clean up temporary files.

        Note: This function does not save modifications.
        """
        if self.writable: rmtree(self._internal_root_dir)


    def _setup_temp_env(self):
        """
        Set up the temporary environment for file operations.
        """
        self._internal_root_dir = TEMPDIR / uuid1().hex
        self._internal_root_dir.mkdir()

        if self.path.exists(): self._extract_files()

        self._internal_files_dir = self._internal_root_dir / "files"
        self._internal_files_dir.mkdir(exist_ok=True)
    
    def _extract_files(self):
        """
        Extract files from the BDM archive to the temporary directory.
        """
        file = ZipFile(self.path)

        namelist = file.namelist()
        for content in self.REQUIRED_CONTENT: namelist.remove(content)

        file.extractall(self._internal_root_dir, namelist)

    
    def _check_validity(self):
        """
        Check if the BDM file is valid.

        Raises:
            InvalidFile: If the file is not a valid BDM archive.
        """
        if not is_zipfile(self.path): raise InvalidFile(self.path, "Not a zip file")
        
        file = ZipFile(self.path)

        namelist = file.namelist()
        
        for content in self.REQUIRED_CONTENT:
            if content not in namelist: raise InvalidFile(self.path, f"Missing '{content}'")
        
        file.close()
    
    def _load_data(self):
        """
        Load data and info from the BDM archive.
        """
        zip_file = ZipFile(self.path)

        data = zip_file.read("data")
        self.data = Data.import_data(data, self)

        info = zip_file.read("info")
        self.info = Info.import_data(info, self)

        zip_file.close()

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        Returns:
            BDMFile: The BDMFile instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.
        """
        self.close()

