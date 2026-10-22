import h5py
from qtpy.QtCore import QSettings
from qtpy.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)
from superqt import QSearchableTreeWidget


def _list_dsets(path) -> dict[str, str]:
    """Map every dataset path in the HDF file to its 'shape dtype'."""
    dsets = {}

    def add(name, obj):
        if isinstance(obj, h5py.Dataset):
            dsets[name] = f'{obj.shape} {obj.dtype}'

    with h5py.File(path, 'r') as f:
        f.visititems(add)

    return dsets


def _browse(path, edit: QLineEdit) -> None:
    """Pick a dataset from a searchable list and put it in `edit`."""
    dialog = QDialog(edit.window())
    dialog.setWindowTitle('Browse datasets')

    layout = QVBoxLayout(dialog)

    browser = QSearchableTreeWidget.fromData(_list_dsets(path))
    browser.tree.setHeaderLabels(('Dataset', 'Shape, dtype'))
    browser.tree.itemDoubleClicked.connect(lambda *_: dialog.accept())
    layout.addWidget(browser)

    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok
        | QDialogButtonBox.StandardButton.Cancel
    )
    layout.addWidget(buttons)

    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)

    if dialog.exec() and (item := browser.tree.currentItem()):
        edit.setText(item.text(0))


def ask_dset_name(path) -> str | None:
    """Ask for the HDF dataset path; None if cancelled or empty."""
    settings = QSettings('napari-lazystack', 'napari-lazystack')

    dialog = QDialog()
    dialog.setWindowTitle('Dataset path')

    form = QFormLayout(dialog)
    edit = QLineEdit(settings.value('dataset', 'images'))
    form.addRow('Dataset path (within HDF file):', edit)

    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok
        | QDialogButtonBox.StandardButton.Cancel
    )
    form.addRow(buttons)

    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)

    browse = buttons.addButton(
        'Browse...', QDialogButtonBox.ButtonRole.ResetRole
    )
    browse.clicked.connect(lambda: _browse(path, edit))

    default = buttons.addButton(
        'Set default', QDialogButtonBox.ButtonRole.ResetRole
    )

    def set_default():
        if name := edit.text().strip():
            settings.setValue('dataset', name)

    default.clicked.connect(set_default)
    if dialog.exec():
        return edit.text().strip() or None

    return None
