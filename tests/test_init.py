import importlib
import sys

import napari_lazystack


def test_version_fallback(monkeypatch):
    # None in sys.modules makes the import raise ImportError
    monkeypatch.setitem(sys.modules, 'napari_lazystack._version', None)
    importlib.reload(napari_lazystack)

    assert napari_lazystack.__version__ == 'unknown'

    monkeypatch.undo()
    importlib.reload(napari_lazystack)

    assert napari_lazystack.__version__ != 'unknown'
