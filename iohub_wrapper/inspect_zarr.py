import argparse
import json
from iohub.ngff import open_ome_zarr


def reterive_zarr_arrays(zarr_obj):
    """
    Recursively traverses an OME-Zarr file and collects all leaf node images.

    Returns:
        List[iohub.ImageArray]: A list of image nodes found at leaf positions.
    """
    images = []

    def recurse(group):
        if group.is_leaf():
            images.extend(list(map(lambda x: x[1], group.images())))
            return

        for _, child_group in group.iteritems():
            recurse(child_group)

    recurse(zarr_obj)

    return images


def _get_zarr_metadata(zarr_obj):
    meta = {"channel_names": zarr_obj.channel_names}
    zarr_arrays = reterive_zarr_arrays(zarr_obj)
    for zarr_array in zarr_arrays:
        meta[zarr_array.name] = get_array_metadata(zarr_array)

    return meta


def get_zarr_metadata(zarr_path):
    zarr_obj = open_ome_zarr(zarr_path)
    meta_data = _get_zarr_metadata(zarr_obj)

    return meta_data


def get_array_metadata(zarr_array):
    meta = {
        "name": zarr_array.name,
        "shape": str(zarr_array.shape),
        "dtype": str(zarr_array.dtype),
        "chunks": str(zarr_array.chunks),
        "order": zarr_array.order,
        "fill_value": str(zarr_array.fill_value),
        "nbytes": zarr_array.nbytes,
        "size": zarr_array.size,
        "ndim": zarr_array.ndim,
        "path": zarr_array.path,
        "store": type(zarr_array.store).__name__,
    }
    return meta


def pretty_print_zarr_metadata(zarr_path):
    """
    Prints metadata in a structured, human-readable format including file path.

    Args:
        zarr_obj: The opened iohub zarr file object.
        metadata (dict): The extracted metadata.
        path (str): The file path to the .zarr store.
    """
    zarr_obj = open_ome_zarr(zarr_path)
    metadata = _get_zarr_metadata(zarr_obj)

    print("OME-Zarr Metadata Summary")
    print("-------------------------")
    print(f"Path          : {zarr_path}\n")

    zarr_obj.print_tree()

    print(f"\nChannel Names : {metadata.get('channel_names', [])}\n")

    for name, meta in metadata.items():
        if name == "channel_names":
            continue
        print(f"[Image Array] {meta['path']}")
        print(f"  Shape       : {meta['shape']}")
        print(f"  NDim        : {meta['ndim']}")
        print(f"  Size        : {meta['size']}")
        print(f"  nbytes      : {meta['nbytes']}")
        print(f"  Dtype       : {meta['dtype']}")
        print(f"  Chunk Sizes : {meta['chunks']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract and optionally pretty-print metadata from an OME-Zarr file."
    )
    parser.add_argument(
        "--zarr_path", required=True, help="Path to the .zarr directory"
    )
    parser.add_argument(
        "--save", help="Path to save the metadata as a JSON file", default=None
    )
    parser.add_argument(
        "--no_pretty_print",
        action="store_true",
        default=False,
        help="Disable pretty printing of metadata",
    )

    args = parser.parse_args()

    try:
        if not args.no_pretty_print:
            pretty_print_zarr_metadata(args.zarr_path)

        if args.save:
            metadata = get_zarr_metadata(args.zarr_path)
            with open(args.save, "w") as f:
                json.dump(metadata, f, indent=2)
            print(f"\n✅ Metadata saved to {args.save}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
