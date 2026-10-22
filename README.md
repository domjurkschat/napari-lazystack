# napari-lazystack

[![License BSD-3](https://img.shields.io/pypi/l/napari-lazystack.svg?color=green)](https://github.com/domjurkschat/napari-lazystack/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-lazystack.svg?color=green)](https://pypi.org/project/napari-lazystack)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-lazystack.svg?color=green)](https://python.org)
[![tests](https://github.com/domjurkschat/napari-lazystack/workflows/tests/badge.svg)](https://github.com/domjurkschat/napari-lazystack/actions)
[![codecov](https://codecov.io/gh/domjurkschat/napari-lazystack/branch/main/graph/badge.svg)](https://codecov.io/gh/domjurkschat/napari-lazystack)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-lazystack)](https://napari-hub.org/plugins/napari-lazystack)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

A napari reader wrapping [lazystack]: a lightweight, cross-platform unified interface for lazily reading scientific image stacks.

**Supported formats**

* HDF (via h5py) — datasets must be (num_images, height, width) grayscale images.
* TIFF and other TIFF-family files (via tifffile) — grayscale stacks only; colour/multichannel images and hyperstacks are not supported.
* Hamamatsu DCIMG (.dcimg).
* Hamamatsu HIS (.his).

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template] (None).

## Installation

You can install `napari-lazystack` via [pip]:

```bash
pip install napari-lazystack
```

If napari is not already installed, you can install `napari-lazystack` with napari and Qt via:

```bash
pip install "napari-lazystack[all]"
```


To install latest development version:

```bash
pip install git+https://github.com/domjurkschat/napari-lazystack.git
```

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-lazystack" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[lazystack]: https://github.com/domjurkschat/lazystack
[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/domjurkschat/napari-lazystack/issues

[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
