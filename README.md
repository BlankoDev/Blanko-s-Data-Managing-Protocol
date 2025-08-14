# Blanko's Data Managing Protocol (BDMP)

BDMP is a Python module for managing structured data and associated files in a hierarchical format. It provides tools for reading, writing, and manipulating sections and items, along with storing and retrieving binary files (like images) within a single archive.

## Features

- Hierarchical data organization with sections and items
- Binary file storage (e.g., images) within the archive
- Version control for compatibility
- Read/write operations with safety checks
- Temporary file handling for safe modifications
- Context manager support (`with` statement)

## Installation

copy the repo folder into your project. There is no PyPi pakage for now

## Basic Usage

```python
from bdmp import BDMFile

# Create or open a BDMP file
with BDMFile("data.bdm", "r+") as bdm:
    # Add a section
    bdm.data.add_section("notes", "text", "Personal notes")
    
    # Add an image file
    bdm.add_file("image.png", "note1_img")

    # Add an item to the section
    bdm.data["notes"].add_item(
        title="First Note",
        content="This is my first note",
        image_id="note1_img",
        level=1
    )
    
    
    # Save changes
    bdm.save()
```

## Classes Overview

### Main Classes

- **BDMFile**: Main interface for reading/writing BDMP files
- **Data**: Contains all sections and items
- **Section**: Collection of related items
- **Item**: Individual data entry with content and optional image
- **Info**: Manages file metadata and information

### Key Features

- **Item**: Can contain text content, an image, and custom metadata
- **Section**: Organizes items by type with description
- **Data**: Manages multiple sections and provides statistics
- **BDMFile**: Handles file operations including:
  - Creating new archives
  - Reading existing files
  - Modifying content
  - Managing embedded files

## Dependencies

- tested in Python 3.11.2 (may work with older version)
- Pillow (PIL) for image handling
- Standard library modules:
  - os, pathlib, pickle, shutil, tempfile, uuid, zipfile, io, copy

## Error Handling

The module provides specific exceptions for error cases:

- `InvalidFile`: Raised for invalid BDMP files
- `VersionError`: Raised for version incompatibility
- `InvalidParent`: Raised for parent-child relationship errors
- Standard Python exceptions for file operations


## Documentation
[documentation](doc.md)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please open an issue or pull request.
