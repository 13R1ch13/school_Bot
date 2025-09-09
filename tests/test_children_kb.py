import pathlib
import sys

import pytest

# Ensure the project root is on sys.path so that ``keyboards`` can be imported when
# the tests are executed from an arbitrary working directory.
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from keyboards.common import children_kb, ChildCB


def _collect_buttons(markup):
    return [btn for row in markup.inline_keyboard for btn in row]


def test_children_kb_adds_all_children_button():
    children = [
        {"id": 1, "full_name": "A"},
        {"id": 2, "full_name": "B"},
    ]
    markup = children_kb(children)
    buttons = _collect_buttons(markup)
    labels = [b.text for b in buttons]
    assert "Однакове замовлення для всіх" in labels
    cb_data = next(
        b.callback_data for b in buttons if b.text == "Однакове замовлення для всіх"
    )
    assert ChildCB.unpack(cb_data).id == -1


def test_children_kb_no_all_button_for_single_child():
    children = [{"id": 1, "full_name": "A"}]
    markup = children_kb(children)
    labels = [b.text for row in markup.inline_keyboard for b in row]
    assert "Однакове замовлення для всіх" not in labels
