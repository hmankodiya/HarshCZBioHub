#!/bin/bash

# Check if required datasets exist
if [ ! -d "dataset1" ] || [ ! -d "dataset2" ]; then
    echo "❌ Error: 'dataset1/' and/or 'dataset2/' folder not found at the project root."
    echo "Please make sure both 'dataset1/' and 'dataset2/' are present before running this script."
    exit 1
fi

echo "✅ Found dataset1/ and dataset2/. Proceeding..."

# Create results folder if not exists
mkdir -p results/frames
mkdir -p results/subset_frames

echo "========== Inspect Zarr =========="
iohub-cli inspect --zarr_path dataset2/20241107_infection.zarr

echo "========== Inspect Zarr and Save JSON =========="
iohub-cli inspect --zarr_path dataset2/20241107_infection.zarr --save results/metadata.json

echo "========== Suppress Print, Save Only JSON =========="
iohub-cli inspect --zarr_path dataset2/20241107_infection.zarr --save results/metadata.json --no_pretty_print

echo "========== Segment: All Time Points, Save Frames =========="
iohub-cli segment --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --channel_idx 1 --output_dir results/frames --save_mode frames

echo "========== Segment: All Time Points, Save as Video =========="
iohub-cli segment --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --channel_idx 1 --save_mode video --video_path results/segmentation_video.mp4

echo "========== Segment: Time Indices 0 1 2 =========="
iohub-cli segment --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --time_indices 0 1 2 --output_dir results/subset_frames --save_mode frames

echo "========== Segment: Save to Zarr =========="
iohub-cli segment --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --save_zarr --output_zarr_path results/segmentations.zarr

echo "========== Infection Metrics: Visualization Only (no display) =========="
iohub-cli infection --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --time_index 0 --no_display

echo "========== Infection Metrics: Save Plot (no display) =========="
iohub-cli infection --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --save_infection_projections --infected_projection_filepath results/infected_cells.png --no_display

echo "========== Infection Metrics: Save CSV (no display) =========="
iohub-cli infection --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --save_infection_metrics --infection_metrics_filepath results/infection_metrics.csv --no_display

echo "========== Infection Metrics: Full Output (Plot + CSV, no display) =========="
iohub-cli infection --zarr_path dataset2/20241107_infection.zarr --zarr_name C/2/001000/0 --save_infection_projections --infected_projection_filepath results/infected_cells.png --save_infection_metrics --infection_metrics_filepath results/infection_metrics.csv --no_display

echo "✅ All tests executed successfully!"
