# HarshCZBioHub

## Setup Environment

### 1. Clone the repository

```bash
git clone git@github.com:hmankodiya/HarshCZBioHub.git
cd HarshCZBioHub
```

---

### 2. Create and activate a conda environment

```bash
conda create -n CZ python=3.11 -y
conda activate CZ
```

---

### 3. Install the iohub library (if not already installed)

```bash
git clone https://github.com/czbiohub-sf/iohub.git
pip install ./iohub
```

---

### 4. Install the local `iohub-wrapper` package

```bash
pip install .
```

# Generate Results Using Provided Script

After completing the installation, you can directly generate results by running:

```bash
bash ./run_tests.sh
```

This script will automatically:

- Inspect and extract metadata from the OME-Zarr datasets.
- Save the metadata into the `results/` directory.
- Prepare necessary outputs for further analysis or visualization.

If everything runs successfully, you will find:

- Metadata JSON files in `results/`
- Pretty-printed metadata in the console
- Ready-to-use inputs for the segmentation and infection analysis pipeline.

Perfect — I see exactly what you want:  
You want the README to **explain important folders** briefly after the setup, mentioning that **individual task results** are inside `task1/` and `task2/`, and also describing things like `iohub_wrapper/`, `results/`, etc.

Here’s the **full cleaned-up version** of your README based on everything you just said:

---

# 📚 Important Folder Details

| Folder | Description |
|:------|:------------|
| `task1/` | Contains `play.ipynb` and `README.md` for **Task 1** (TIFF ➔ OME-Zarr conversion, metadata extraction). Outputs like Zarr stores are also saved here. |
| `task2/` | Contains `play.ipynb` and `README.md` for **Task 2** (Segmentation and Infection Analysis). Visualization files like `.gif` and `.mp4` are saved here. |
| `iohub_wrapper/` | Contains CLI scripts and Python utilities for inspecting Zarr files, running segmentation, and computing infection metrics. Main scripts: `cli.py`, `infection_pipeline.py`, `inspect_zarr.py`. |
| `results/` | Stores generated outputs from the CLI, including segmented frames, infection projections, videos, segmentation Zarrs, and infection metrics CSVs. |
| `outputs/` | Stores visualizations and intermediate outputs manually generated during notebook exploration. |
| `dataset1/` and `dataset2/` | Contain raw input datasets used for analysis. |
| `run_tests.sh` | Shell script to automate metadata extraction and basic result generation. |

---

# 📌 Notes

- **Individual task results** (for **Task 1** and **Task 2**) can be found inside the `task1/` and `task2/` folders.
- CLI outputs such as segmentation videos, infected cell images, and CSV metrics are saved under `results/`.
- Notebooks (`play.ipynb`) demonstrate detailed step-by-step workflows for each task.

---

# ✅ Final Deliverables Checklist


## 📂 Task 1

- Human-readable output with the OME-Zarr metadata

---

## 📂 Task 2

- Script to demo your Python API
- Valid OME-Zarr store with the segmentations
- Visualizations of the results
- Infection detection
---

## 📂 Task 3
- Implement a command line interface (CLI) on top of this to interact with image
management and analysis API.

---

