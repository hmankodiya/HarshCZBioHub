import os
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import imageio.v2 as imageio
from scipy.ndimage import gaussian_filter
from skimage.filters import threshold_otsu
from skimage.measure import label
from skimage.measure import regionprops_table

from iohub import open_ome_zarr
from tqdm import tqdm


def normalize_and_gamma(frame, gamma=1.97):
    frame = frame.astype(np.float32)
    norm_frame = (frame - frame.min()) / (frame.max() - frame.min() + 1e-8)
    return np.power(norm_frame, gamma)


def load_zarr_data(zarr_path, zarr_name):
    zarr_file = open_ome_zarr(zarr_path)
    return zarr_file[zarr_name].numpy()  # (T, C, Z, Y, X)


def preprocess_and_segment(frame, sigma=2):
    projection = frame.mean(axis=0)  # (Y, X)
    blurred = gaussian_filter(projection, sigma=sigma)
    threshold = threshold_otsu(blurred)
    binary = blurred > threshold
    labeled = label(binary)
    return labeled


def segment_zarr(zarr_path, zarr_name, channel_idx=1, time_indices=None, sigma=2):
    data = load_zarr_data(zarr_path, zarr_name)  # shape: (T, C, Z, Y, X)
    assert data.ndim == 5, "5D image expected"

    masks = []
    if not time_indices or time_indices == "all":
        time_indices = list(range(data.shape[0]))
    elif isinstance(time_indices, int):
        time_indices = [time_indices]

    for t in tqdm(time_indices, desc="Segmenting frames"):
        frame = data[t, channel_idx]  # (Z, Y, X)
        labeled = preprocess_and_segment(frame, sigma=sigma)
        masks.append(labeled)

    return np.stack(masks, axis=0)


def save_segmentation_frame(labeled, filepath, t, verbose=1):
    plt.imshow(labeled, cmap="nipy_spectral", alpha=1)
    plt.title(f"Nuclei Segmentation - Time {t}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    if verbose:
        print(f"Saved segmentation frame: {filepath}")

    return filepath


def create_video_from_frames(frame_paths, output_video_path, fps=1):
    with imageio.get_writer(
        output_video_path,
        mode="I",
        format="ffmpeg",
        fps=fps,
    ) as writer:
        for path in tqdm(frame_paths, desc="Encoding video frames"):
            img = imageio.imread(path)
            writer.append_data(img)
    print(f"Saved video at: {output_video_path}")


def save_segmentations_to_zarr(masks, output_zarr_path):
    os.makedirs(output_zarr_path, exist_ok=True)
    with open_ome_zarr(
        output_zarr_path, layout="fov", channel_names=["c1"], mode="w"
    ) as out_zarr:
        out_zarr["masks"] = masks
    print(f"Saved segmentation masks to Zarr at: {output_zarr_path}")


def naive_compute_infection_metrics(nuclei_labels, virus_img):
    props = regionprops_table(
        label_image=nuclei_labels,
        intensity_image=virus_img,
        properties=["label", "area", "mean_intensity", "max_intensity", "centroid"],
    )
    df = pd.DataFrame(props)
    threshold = df["mean_intensity"].mean() + df["mean_intensity"].std()
    df["infected"] = df["mean_intensity"] > threshold
    return df


def calculate_infected_coordinates(infection_metrics):
    infected = infection_metrics[infection_metrics["infected"] == True]
    return infected["centroid-1"], infected["centroid-0"]


def project_infected_coordinates(
    coordinates_x,
    coordinates_y,
    projection_image,
    display=True,
    save_fig=False,
    filepath=None,
    verbose=0,
):
    plt.imshow(projection_image, cmap="gray")
    plt.scatter(coordinates_x, coordinates_y, color="red", label="Infected")
    plt.legend()
    plt.title("Detected Infected Cells")

    if save_fig and filepath:
        plt.savefig(filepath)
        if verbose:
            print(f"Saved projection to {filepath}")
    if display:
        plt.show()
    else:
        plt.close()


def infection_metrics_from_zarr(
    zarr_path,
    zarr_name,
    time_index=0,
    nuclie_channel_idx=1,
    virus_channel_idx=2,
    display_projections=True,
    save_projection=False,
    projection_filepath=None,
    save_metrics=False,
    metrics_filepath=None,
):
    nuclie_masks = segment_zarr(
        zarr_path, zarr_name, time_indices=time_index, channel_idx=nuclie_channel_idx
    )[0]
    virus_projections = load_zarr_data(zarr_path, zarr_name)[
        time_index, virus_channel_idx
    ].mean(axis=0)

    infection_metrics = naive_compute_infection_metrics(nuclie_masks, virus_projections)
    if save_metrics and metrics_filepath:
        infection_metrics.to_csv(metrics_filepath, index=False)
        print(f"Saved infection metrics to: {metrics_filepath}")

    infected_coordinate_x, infected_coordinate_y = calculate_infected_coordinates(
        infection_metrics
    )

    project_infected_coordinates(
        infected_coordinate_x,
        infected_coordinate_y,
        virus_projections,
        display=display_projections,
        save_fig=save_projection,
        filepath=projection_filepath,
        verbose=1,
    )

    return infection_metrics


def save_segmented_format(
    zarr_path,
    zarr_name,
    time_indices=None,
    output_dir="./results/frames",
    channel_idx=1,
    save_mode="frames",
    video_path="./results/segmentation_video.mp4",
    save_zarr=False,
    output_zarr_path="./results/segmentations.zarr",
    sigma=2,
):
    os.makedirs(output_dir, exist_ok=True)
    masks = segment_zarr(
        zarr_path,
        zarr_name,
        time_indices=time_indices,
        channel_idx=channel_idx,
        sigma=sigma,
    )

    if save_mode in ("frames", "video"):
        saved_frames = []
        for t, labeled in tqdm(
            enumerate(masks), total=len(masks), desc="Saving frames"
        ):
            filepath = os.path.join(output_dir, f"seg_t{t:03d}.png")
            frame_path = save_segmentation_frame(labeled, filepath, t, verbose=0)
            saved_frames.append(frame_path)

    if save_mode == "video":
        create_video_from_frames(saved_frames, video_path)

    if save_zarr:
        save_segmentations_to_zarr(masks[:, None, None, :, :], output_zarr_path)

    print(f"Done. Total frames processed: {len(masks)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OME-Zarr Nuclei Segmentation Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand 1: Save segmentations
    seg_parser = subparsers.add_parser(
        "save_segmentations", help="Save segmentation frames/video/zarr"
    )
    seg_parser.add_argument(
        "--zarr_path", required=True, help="Path to OME-Zarr dataset."
    )
    seg_parser.add_argument("--zarr_name", help="Group path inside the Zarr store.")
    seg_parser.add_argument(
        "--output_dir",
        default="./results/visualizations",
        help="Directory to save PNGs.",
    )
    seg_parser.add_argument(
        "--channel_idx", type=int, default=1, help="Channel index for nuclei."
    )
    seg_parser.add_argument(
        "--time_indices",
        type=int,
        nargs="+",
        default=None,
        help="List of time indices.",
    )
    seg_parser.add_argument(
        "--save_mode",
        choices=["frames", "video"],
        default="frames",
        help="Output mode.",
    )
    seg_parser.add_argument(
        "--video_path",
        default="./results/segmentation_video.mp4",
        help="Path to save video.",
    )
    seg_parser.add_argument(
        "--save_zarr", action="store_true", help="Save segmentation masks as Zarr."
    )
    seg_parser.add_argument(
        "--output_zarr_path",
        default="./results/segmentations.zarr",
        help="Zarr output path.",
    )
    seg_parser.add_argument(
        "--sigma", type=float, default=2, help="Sigma for Gaussian blur."
    )

    # Subcommand 2: Infection metrics
    inf_parser = subparsers.add_parser(
        "infection_metrics", help="Run infection metric analysis and projection."
    )
    inf_parser.add_argument(
        "--zarr_path", required=True, help="Path to OME-Zarr dataset."
    )
    inf_parser.add_argument("--zarr_name", help="Group path inside the Zarr store.")
    inf_parser.add_argument(
        "--time_index", type=int, default=0, help="Time index to process."
    )
    inf_parser.add_argument(
        "--nuclie_channel_idx", type=int, default=1, help="Channel index for nuclei."
    )
    inf_parser.add_argument(
        "--virus_channel_idx", type=int, default=2, help="Channel index for virus."
    )
    inf_parser.add_argument(
        "--no_display", action="store_true", help="Disable plotting of projection."
    )
    inf_parser.add_argument(
        "--save_infection_projections",
        action="store_true",
        help="Disable plotting of projection.",
    )
    inf_parser.add_argument(
        "--infected_projection_filepath",
        default=None,
    )
    inf_parser.add_argument("--save_infection_metrics", action="store_true")
    inf_parser.add_argument("--infection_metrics_filepath", default=None)

    args = parser.parse_args()

    if args.command == "save_segmentations":
        save_segmented_format(
            zarr_path=args.zarr_path,
            zarr_name=args.zarr_name,
            output_dir=args.output_dir,
            channel_idx=args.channel_idx,
            time_indices=args.time_indices,
            save_mode=args.save_mode,
            video_path=args.video_path,
            save_zarr=args.save_zarr,
            output_zarr_path=args.output_zarr_path,
            sigma=args.sigma,
        )

    elif args.command == "infection_metrics":
        infection_metrics = infection_metrics_from_zarr(
            zarr_path=args.zarr_path,
            zarr_name=args.zarr_name,
            time_index=args.time_index,
            nuclie_channel_idx=args.nuclie_channel_idx,
            virus_channel_idx=args.virus_channel_idx,
            display_projections=not args.no_display,
            save_projection=args.save_infection_projections,
            projection_filepath=args.infected_projection_filepath,
            save_metrics=args.save_infection_metrics,
            metrics_filepath=args.infection_metrics_filepath,
        )
