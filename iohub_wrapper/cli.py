import argparse
import json

from iohub_wrapper.inspect_zarr import get_zarr_metadata, pretty_print_zarr_metadata
from iohub_wrapper.infection_pipeline import (
    save_segmented_format,
    infection_metrics_from_zarr,
)


def main():
    parser = argparse.ArgumentParser(
        description="CLI for OME-Zarr inspection, segmentation, and infection analysis"
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Subcommands: 'inspect', 'segment', 'infection'"
    )

    # Inspect Subcommand
    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect metadata from OME-Zarr"
    )
    inspect_parser.add_argument(
        "--zarr_path", required=True, help="Path to the OME-Zarr dataset"
    )
    inspect_parser.add_argument("--save", help="Path to save metadata JSON")
    inspect_parser.add_argument(
        "--no_pretty_print", action="store_true", help="Suppress printed summary"
    )

    # Segment Subcommand
    segment_parser = subparsers.add_parser("segment", help="Segment nuclei from Zarr")
    segment_parser.add_argument(
        "--zarr_path", required=True, help="Path to OME-Zarr dataset"
    )
    segment_parser.add_argument(
        "--zarr_name", required=True, help="Group path inside the Zarr store"
    )
    segment_parser.add_argument(
        "--time_indices", type=int, nargs="+", default=None, help="Time indices"
    )
    segment_parser.add_argument(
        "--output_dir",
        default="./results/visualizations",
        help="Directory to save PNGs",
    )
    segment_parser.add_argument(
        "--channel_idx", type=int, default=1, help="Channel index for nuclei"
    )
    segment_parser.add_argument(
        "--save_mode", choices=["frames", "video"], default="frames", help="Save mode"
    )
    segment_parser.add_argument(
        "--video_path",
        default="./results/segmentation_video.mp4",
        help="Path to save video",
    )
    segment_parser.add_argument(
        "--save_zarr", action="store_true", help="Store masks to Zarr"
    )
    segment_parser.add_argument(
        "--output_zarr_path",
        default="./results/segmentations.zarr",
        help="Zarr path to save segmentations",
    )
    segment_parser.add_argument(
        "--sigma", type=float, default=2, help="Gaussian blur sigma"
    )

    # Infection Subcommand
    infection_parser = subparsers.add_parser(
        "infection", help="Run infection metrics and projections"
    )
    infection_parser.add_argument(
        "--zarr_path", required=True, help="Path to OME-Zarr dataset"
    )
    infection_parser.add_argument(
        "--zarr_name", required=True, help="Group path inside the Zarr store"
    )
    infection_parser.add_argument(
        "--time_index", type=int, default=0, help="Time index to process"
    )
    infection_parser.add_argument(
        "--nuclie_channel_idx", type=int, default=1, help="Nuclei channel index"
    )
    infection_parser.add_argument(
        "--virus_channel_idx", type=int, default=2, help="Virus channel index"
    )
    infection_parser.add_argument(
        "--no_display", action="store_true", help="Disable plotting"
    )
    infection_parser.add_argument(
        "--save_infection_projections",
        action="store_true",
        help="Save projection figure",
    )
    infection_parser.add_argument(
        "--infected_projection_filepath",
        default=None,
        help="Path to save infected plot",
    )
    infection_parser.add_argument(
        "--save_infection_metrics", action="store_true", help="Save metrics CSV"
    )
    infection_parser.add_argument(
        "--infection_metrics_filepath", default=None, help="Path to save metrics CSV"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        if not args.no_pretty_print:
            pretty_print_zarr_metadata(args.zarr_path)
        if args.save:
            metadata = get_zarr_metadata(args.zarr_path)
            with open(args.save, "w") as f:
                json.dump(metadata, f, indent=2)
            print(f"Saved metadata to: {args.save}")

    elif args.command == "segment":
        save_segmented_format(
            zarr_path=args.zarr_path,
            zarr_name=args.zarr_name,
            time_indices=args.time_indices,
            output_dir=args.output_dir,
            channel_idx=args.channel_idx,
            save_mode=args.save_mode,
            video_path=args.video_path,
            save_zarr=args.save_zarr,
            output_zarr_path=args.output_zarr_path,
            sigma=args.sigma,
        )

    elif args.command == "infection":
        infection_metrics_from_zarr(
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

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
