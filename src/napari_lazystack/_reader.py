from collections.abc import Callable, Sequence
from pathlib import Path

import h5py
from lazystack import lazystack
from napari.types import LayerData

from ._widgets import ask_dset_name

PathLike = str | Path
PathOrPaths = PathLike | Sequence[PathLike]
ReaderFunction = Callable[[PathOrPaths], list[LayerData]]


def get_reader(path: PathOrPaths) -> ReaderFunction | None:
    """Return lazystack_reader for a path or list of paths.

    Parameters
    ----------
    path : str, Path, or list of them
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, PathLike | list):
        # Only valid filename patterns get to this point, so no need to check
        #   again.
        # Lists are included here and assumed to be stacks of individual TIFF
        #   files by lazystack; mixed or other file types are not supported.
        return lazystack_reader

    return None


def lazystack_reader(path):
    """Take a path or list of paths and return a list of LayerData tuples,
    loading the underlying image data via lazystack
    (github.com/domjurkschat/lazystack).

    Currently supported formats are:

    - HDF5 (.h5, .hdf5, ... ), read as (num_images, height, width) grayscale
      stacks.
    - TIFF-family files via tifffile (.tif, .tiff, .ome.tif, ... ), e.g.
      multi-page TIFF, BigTIFF, Micro-Manager MMStack, and NDTiff. Grayscale
      only; colour/multichannel images and hyperstacks are rejected. Files
      storing the whole stack as one 3D image require the optional ``zarr``
      package.
    - Hamamatsu DCIMG (.dcimg).
    - Hamamatsu HIS (.his).

    Parameters
    ----------
    path : str, Path, or list of them
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        [(data, add_kwargs, 'image')], or [(None,)] if the HDF5 dataset
        prompt is cancelled.
    """
    path = Path(path) if isinstance(path, str) else path

    dset_name = None
    if not isinstance(path, list) and h5py.is_hdf5(path):
        dset_name = ask_dset_name(path)
        if dset_name is None:
            return [(None,)]

    # Optional kwargs for `viewer.add_image`. We add the path as the metadata
    #   for future reference, and ensure RGB is disabled (not supported by
    #   lazystack).
    metadata = {'path': path[0]} if isinstance(path, list) else {'path': path}
    add_kwargs = {
        'metadata': metadata,
        'rgb': False,
    }
    layer_type = 'image'

    return [(lazystack(path, dset_name), add_kwargs, layer_type)]
