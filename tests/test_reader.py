from pathlib import Path

import h5py
import numpy as np
import pytest
from napari.layers import Image
from tifffile import imwrite

from napari_lazystack._reader import get_reader, lazystack_reader
from napari_lazystack._widgets import _list_dsets


@pytest.fixture()
def example_3d_data():
    return np.arange(120).reshape(10, 3, 4).astype(np.uint16)


@pytest.fixture()
def example_single_path(example_3d_data, tmp_path):
    out_path = tmp_path / 'tmp.tif'
    imwrite(out_path, example_3d_data[0])
    return out_path


@pytest.fixture()
def example_list_of_paths(example_3d_data, tmp_path):
    out_dir = tmp_path / 'multifile_tif'
    out_dir.mkdir(exist_ok=True)

    paths = []
    for i, image in enumerate(example_3d_data):
        path = out_dir / f'{i:04}.tif'
        imwrite(path, image)
        paths.append(path)

    return paths


@pytest.mark.parametrize(
    ('path', 'expected'),
    [
        ('tmp.tif', lazystack_reader),
        (Path('tmp.tif'), lazystack_reader),
        (['x.tif', 'y.tif'], lazystack_reader),
        (('x.tif', 'y.tif'), None),
    ],
)
def test_get_reader(path, expected):
    assert get_reader(path) is expected


@pytest.mark.parametrize(
    'path_fixture', ['example_single_path', 'example_list_of_paths']
)
def test_reader_format(path_fixture, request):
    layer_data_list = lazystack_reader(request.getfixturevalue(path_fixture))
    layer_data_tuple = layer_data_list[0]

    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0


@pytest.mark.parametrize(
    ('path_fixture', 'num_images'),
    [('example_single_path', 1), ('example_list_of_paths', 10)],
)
def test_reader_data(path_fixture, num_images, request, example_3d_data):
    data = lazystack_reader(request.getfixturevalue(path_fixture))[0][0]

    np.testing.assert_array_equal(
        np.asarray(data), example_3d_data[:num_images]
    )


def test_reader_list_metadata(example_list_of_paths):
    metadata = lazystack_reader(example_list_of_paths)[0][1]['metadata']

    assert metadata['path'] == example_list_of_paths[0]


def test_viewer_layer(
    make_napari_viewer_proxy, example_single_path, example_3d_data
):
    viewer = make_napari_viewer_proxy()
    viewer.open(example_single_path, plugin='napari-lazystack', name='test')

    np.testing.assert_allclose(
        viewer.layers['test'].data[0], example_3d_data[0]
    )
    assert not viewer.layers['test'].rgb
    assert viewer.layers['test'].metadata['path'] == example_single_path
    assert isinstance(viewer.layers['test'], Image)


@pytest.fixture()
def example_hdf5_path(tmp_path, example_3d_data):
    path = tmp_path / 'tmp.h5'

    with h5py.File(path, 'w') as f:
        f['images'] = example_3d_data

    return path


def test_hdf5_reader(monkeypatch, example_hdf5_path, example_3d_data):
    reader = get_reader(example_hdf5_path)

    monkeypatch.setattr(
        'napari_lazystack._reader.ask_dset_name', lambda _: 'images'
    )
    np.testing.assert_array_equal(
        np.asarray(reader(example_hdf5_path)[0][0]), example_3d_data
    )

    monkeypatch.setattr(
        'napari_lazystack._reader.ask_dset_name', lambda _: None
    )

    assert reader(example_hdf5_path) == [(None,)]


def test_list_dsets(tmp_path):
    path = tmp_path / 'a.h5'

    with h5py.File(path, 'w') as f:
        f['images'] = np.zeros((2, 3), np.uint8)
        f['group/stack'] = np.zeros(4, np.float32)

    assert _list_dsets(path) == {
        'images': '(2, 3) uint8',
        'group/stack': '(4,) float32',
    }
