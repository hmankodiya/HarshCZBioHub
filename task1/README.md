## Explore play.ipynb to explore more

## 📁 Input

Folder containing Micro-Manager TIFF images:

```
dataset1/
└── KazanskyStar/
    ├── Kazansky_MMStack.ome.tif
```

---

## 🔄 Step 1: TIFF to OME-Zarr Conversion

Using `iohub.convert.TIFFConverter`, we convert TIFF files into Zarr format:

```python
from iohub.convert import TIFFConverter

input_path = "../dataset1/KazanskyStar/"
output_path = "./ome_zarr/ome.zarr"

converter = TIFFConverter(input_path, output_dir=output_path)
converter()  # Converts the TIFF stack into OME-Zarr format
```

---

## 🔍 Step 2: Metadata Extraction Functions

We define helper functions in `inspect_zarr.py`:

- `reterive_zarr_arrays(zarr_obj)`: Recursively collects all image arrays from a Zarr hierarchy.
- `get_array_metadata(zarr_array)`: Extracts metadata such as shape, dtype, chunk sizes, etc.
- `get_zarr_metadata(zarr_path)`: Retrieves and compiles metadata from a full OME-Zarr store.
- `pretty_print_zarr_metadata(zarr_path)`: Prints a clean, human-readable summary of the metadata.

---

### 🔬 Example Usage (from `play.ipynb`)

```python
from iohub_wrapper.inspect_zarr import (
    reterive_zarr_arrays,
    get_zarr_metadata,
    pretty_print_zarr_metadata,
)
from iohub.ngff import open_ome_zarr

# Open the Zarr store
zarr_path = "./ome_zarr/ome.zarr"
ome_zarr = open_ome_zarr(zarr_path)

# Retrieve images
images = reterive_zarr_arrays(ome_zarr)

# Extract metadata
meta = get_zarr_metadata(zarr_path)
print(meta.keys())

# Pretty print metadata
pretty_print_zarr_metadata(zarr_path)
```

---

## 🧪 Step 3: Command Line Interface (CLI)

A simple CLI is provided to make inspecting Zarr files easier.

### Example commands:

#### Basic inspection (pretty printed to console):

```bash
iohub-cli inspect --zarr_path dataset2/20241107_infection.zarr
```

#### Save metadata as JSON:

```bash
iohub-cli inspect --zarr_path dataset2/20241107_infection.zarr --save results/metadata.json
```

#### Suppress printing (save only):

```bash
iohub-cli inspect --zarr_path dataset2/20241107_infection.zarr --save results/metadata.json --no_pretty_print
```

The CLI uses Python's `argparse` to manage flags such as:
- `--zarr_path`: path to the OME-Zarr dataset (**required**)
- `--save`: optional path to save extracted metadata
- `--no_pretty_print`: disables console output if you only want JSON saved

---

## 📋 Output Example

Pretty-printed metadata looks like:

```
OME-Zarr Metadata Summary
-------------------------
Path          : ./ome_zarr/ome.zarr

/
 └── 0
     ├── 0
     │   └── 0
     │       └── 0 (2, 4, 81, 231, 498) uint16
     ├── 1
     │   └── 0
     │       └── 0 (2, 4, 81, 231, 498) uint16
     └── 2
         └── 0
             └── 0 (2, 4, 81, 231, 498) uint16

Channel Names : ['State0', 'State1', 'State2', 'State3']

[Image Array] 0/0/0/0
  Shape       : (2, 4, 81, 231, 498)
  NDim        : 5
  Size        : 74544624
  nbytes      : 149089248
  Dtype       : uint16
  Chunk Sizes : (1, 1, 81, 231, 498)

[Image Array] 0/1/0/0
  Shape       : (2, 4, 81, 231, 498)
  NDim        : 5
  Size        : 74544624
  nbytes      : 149089248
  Dtype       : uint16
  Chunk Sizes : (1, 1, 81, 231, 498)

[Image Array] 0/2/0/0
  Shape       : (2, 4, 81, 231, 498)
  NDim        : 5
  Size        : 74544624
  nbytes      : 149089248
  Dtype       : uint16
  Chunk Sizes : (1, 1, 81, 231, 498)

```
