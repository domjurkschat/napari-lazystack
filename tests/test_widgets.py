import h5py
import numpy as np
import pytest
from qtpy.QtCore import QSettings, Qt
from qtpy.QtWidgets import QDialog, QLineEdit, QPushButton
from superqt import QSearchableTreeWidget

from napari_lazystack._widgets import _browse, ask_dset_name


@pytest.fixture()
def h5_path(tmp_path):
    path = tmp_path / 'a.h5'

    with h5py.File(path, 'w') as f:
        f['images'] = np.zeros((2, 3), np.uint8)
        f['group/stack'] = np.zeros(4, np.float32)

    return path


@pytest.fixture(autouse=True)
def tmp_settings(tmp_path, monkeypatch):
    """Keep QSettings out of the real registry / config dir."""
    ini = str(tmp_path / 'settings.ini')
    monkeypatch.setattr(
        'napari_lazystack._widgets.QSettings',
        lambda *_: QSettings(ini, QSettings.Format.IniFormat),
    )


def fake_exec(monkeypatch, handler):
    """Replace the blocking QDialog.exec with `handler(dialog) -> bool`."""
    monkeypatch.setattr(QDialog, 'exec', handler)


def click(dialog, label):
    button = next(
        b for b in dialog.findChildren(QPushButton) if b.text() == label
    )
    button.click()


@pytest.mark.parametrize(
    ('typed', 'accepted', 'expected'),
    [
        ('  stack ', True, 'stack'),
        ('   ', True, None),
        ('stack', False, None),
    ],
)
def test_ask_dset_name(qtbot, monkeypatch, typed, accepted, expected):
    def handler(dialog):
        dialog.findChild(QLineEdit).setText(typed)
        return accepted

    fake_exec(monkeypatch, handler)

    assert ask_dset_name('a.h5') == expected


def test_ask_dset_name_set_default(qtbot, monkeypatch):
    typed = iter(['saved', '   ', 'unused'])
    initial = []

    def handler(dialog):
        edit = dialog.findChild(QLineEdit)
        initial.append(edit.text())
        edit.setText(next(typed))
        click(dialog, 'Set default')
        return False

    fake_exec(monkeypatch, handler)
    for _ in range(3):
        ask_dset_name('a.h5')

    # Blank input must not overwrite the saved default
    assert initial == ['images', 'saved', 'saved']


@pytest.mark.parametrize(
    ('accepted', 'expected'), [(True, 'group/stack'), (False, 'images')]
)
def test_browse(qtbot, monkeypatch, h5_path, accepted, expected):
    def handler(dialog):
        tree = dialog.findChild(QSearchableTreeWidget).tree
        assert tree.headerItem().text(0) == 'Dataset'
        tree.setCurrentItem(
            tree.findItems('group/stack', Qt.MatchFlag.MatchExactly)[0]
        )
        return accepted

    fake_exec(monkeypatch, handler)
    edit = QLineEdit('images')
    qtbot.addWidget(edit)

    _browse(h5_path, edit)

    assert edit.text() == expected


def test_browse_double_click_accepts(qtbot, monkeypatch, h5_path):
    def handler(dialog):
        tree = dialog.findChild(QSearchableTreeWidget).tree
        item = tree.findItems('group/stack', Qt.MatchFlag.MatchExactly)[0]
        tree.setCurrentItem(item)
        tree.itemDoubleClicked.emit(item, 0)
        return dialog.result() == QDialog.DialogCode.Accepted

    fake_exec(monkeypatch, handler)
    edit = QLineEdit('images')
    qtbot.addWidget(edit)

    _browse(h5_path, edit)

    assert edit.text() == 'group/stack'


def test_browse_button_opens_browser(qtbot, monkeypatch, h5_path):
    def handler(dialog):
        if dialog.windowTitle() == 'Browse datasets':
            tree = dialog.findChild(QSearchableTreeWidget).tree
            tree.setCurrentItem(
                tree.findItems('group/stack', Qt.MatchFlag.MatchExactly)[0]
            )
            return True
        click(dialog, 'Browse...')
        return True

    fake_exec(monkeypatch, handler)

    assert ask_dset_name(h5_path) == 'group/stack'
