
# Blanko's Data Managing Protocol (BDMP) - Documentation

## Table of Contents
1. [Overview](#overview)
2. [File Format](#file-format)
3. [API Reference](#api-reference)
   - [BDMFile Class](#bdmfile-class)
   - [Data Class](#data-class)
   - [Section Class](#section-class)
   - [Item Class](#item-class)
   - [Info Class](#info-class)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Version Compatibility](#version-compatibility)

## Overview <a name="overview"></a>

BDMP is a hierarchical data management system that combines structured data with binary file storage in a single archive. It's particularly useful for applications that need to manage:

- Text content with metadata
- Associated binary files (like images)
- Hierarchical organization (sections and items)
- Version-controlled data storage

## File Format <a name="file-format"></a>

A BDMP file is a ZIP archive containing:

```
archive.bdm
├── data        # Pickled Data object
├── info        # Pickled Info object
└── files/      # Directory for stored binary files
    ├── abc123.jpg
    └── def456.png
```

## API Reference <a name="api-reference"></a>

### BDMFile Class <a name="bdmfile-class"></a>

Main interface for BDMP file operations.

#### Constructor
```python
BDMFile(path: str | Path, mode: str = "r")
```
- `path`: File path
- `mode`: 
  - `'r'` - Read only
  - `'w'` - Write (creates new file)
  - `'r+'` - Read/write

#### Methods
| Method | Description |
|--------|-------------|
| `save(path=None)` | Save changes to file |
| `add_file(path, file_id, internal_name=None)` | Add external file to archive |
| `read_file(file_id)` → bytes | Read file contents |
| `write_file(file_id, data)` | Write data to file |
| `open_file(file_id, mode='r')` → file object | Open file stream |
| `close()` | Close file (cleans temp files) |

### Data Class <a name="data-class"></a>

Top-level container for all sections.

#### Methods
| Method | Description |
|--------|-------------|
| `add_section(name, type, description)` | Create new section |
| `export_data()` → bytes | Serialize data |
| `import_data(data, parent)` → Data | Deserialize data |

### Section Class <a name="section-class"></a>

Container for related items.

#### Methods
| Method | Description |
|--------|-------------|
| `add_item(title, content, image_id, level, name=None, data=None)` | Add new item |
| `remove_item(name)` | Delete item |
| `to_dict()` → dict | Convert to dictionary |

### Item Class <a name="item-class"></a>

Individual data element.

#### Methods
| Method | Description |
|--------|-------------|
| `add_data(name, value)` | Add metadata |
| `remove_data(name)` | Remove metadata |
| `get_image()` → PIL.Image | Get image object |
| `export_image(path)` | Save image to file |
| `to_dict()` → dict | Convert to dictionary |

### Info Class <a name="info-class"></a>

Manages file metadata.

#### Methods
| Method | Description |
|--------|-------------|
| `export_data()` → bytes | Serialize info |
| `import_data(data, parent)` → Info | Deserialize info |

## Usage Examples <a name="usage-examples"></a>

### Creating a New BDMP File
```python
from bdmp import BDMFile

with BDMFile("new_data.bdm", "w") as bdm:
    # Add metadata
    bdm.info.name = "My Project"
    
    # Add a section
    bdm.data.add_section("notes", "text", "Personal notes")
    
    # Add an item with image
    bdm.data["notes"].add_item(
        title="First Note",
        content="This is my first note",
        image_id="note1_img",
        level=1
    )
    
    # Add the image file
    bdm.add_file("photo.jpg", "note1_img")
    
    # Save
    bdm.save()
```

### Reading a BDMP File
```python
with BDMFile("data.bdm", "r") as bdm:
    print(f"Archive name: {bdm.info.name}")
    
    for section_name in bdm.data:
        section = bdm.data[section_name]
        print(f"\nSection: {section_name}")
        print(f"Type: {section.type}")
        
        for item_name in section:
            item = section[item_name]
            print(f"\nItem: {item.title}")
            print(f"Content: {item.content[:50]}...")
            
            # Export image
            item.export_image(f"exported_{item_name}.jpg")
```

## Error Handling <a name="error-handling"></a>

### Exceptions
| Exception | Description |
|-----------|-------------|
| `InvalidFile` | Corrupted or invalid BDMP file |
| `VersionError` | Version incompatibility |
| `InvalidParent` | Hierarchy violation |
| `UnsupportedOperation` | Illegal operation for current mode |

### Common Patterns
```python
try:
    with BDMFile("data.bdm", "r+") as bdm:
        # Operations...
        bdm.save()
except InvalidFile as e:
    print(f"Invalid file: {e}")
except VersionError as e:
    print(f"Version mismatch: {e}")
```

## Version Compatibility <a name="version-compatibility"></a>

| Version | Changes | Compatibility |
|---------|---------|---------------|
| 2       | Current | -             |
| 1       |   badp  |     None      |


The module is incompatible with version 1.
The version 1 is a completely different system, but has the same original purpose. That's why this repo is labeled as the version 2