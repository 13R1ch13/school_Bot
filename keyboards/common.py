
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Iterable, Mapping, Sequence

def start_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Розпочати")
    return kb.as_markup(resize_keyboard=True)

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Реєстрація дитини")
    kb.button(text="Замовлення")
    return kb.as_markup(resize_keyboard=True)

class ConfirmCB(CallbackData, prefix="cfm"):
    ok: int  # 1 - вірно✅, 0 - назад🔙

def confirm_kb():
    b = InlineKeyboardBuilder()
    b.button(text="вірно", callback_data=ConfirmCB(ok=1).pack())
    b.button(text="назад", callback_data=ConfirmCB(ok=0).pack())
    b.adjust(2)
    return b.as_markup()

class ClassCB(CallbackData, prefix="cls"):
    label: str

def class_list_kb():
    labels = ["1.1 клас","1.2 клас","2.1 клас","2.2 клас","3.1 клас","3.2 клас","4 клас",
              "5.1 клас","5.2 клас","6.1 клас","6.2 клас","7.1 клас","8.1 клас","8.2 клас",
              "9.1 клас","10 клас","11 клас"]
    b = InlineKeyboardBuilder()
    for l in labels:
        b.button(text=l, callback_data=ClassCB(label=l).pack())
    b.adjust(2)
    return b.as_markup()


class ChildCB(CallbackData, prefix="ch"):
    id: int


def children_kb(children: Iterable[Mapping]):
    """Construct inline keyboard with a list of children.

    The input items might be :class:`sqlite3.Row` objects or plain dictionaries.
    ``sqlite3.Row`` does not support membership testing for keys, so each item is
    converted to a ``dict`` and validated explicitly.  When more than one child is
    supplied, an additional button allows applying the same order to all children
    at once.
    """

    # ``children`` may be any iterable; convert to a list to be able to check its
    # length and iterate over it multiple times without exhausting it.
    child_list: Sequence[Mapping] = list(children)

    b = InlineKeyboardBuilder()
    for ch in child_list:
        # ``sqlite3.Row`` behaves like both a sequence and a mapping, but "in" checks
        # values rather than column names.  Convert the record to a plain ``dict``
        # and ensure the required fields are present before constructing the button.
        ch_dict = dict(ch)
        assert {"id", "full_name"}.issubset(ch_dict.keys()), (
            "child record must have id and full_name"
        )
        b.button(
            text=ch_dict["full_name"],
            callback_data=ChildCB(id=ch_dict["id"]).pack(),
        )

    if len(child_list) > 1:
        # ``id=-1`` acts as a sentinel meaning the order should apply to all children
        # registered for the parent.
        b.button(
            text="Однакове замовлення для всіх",
            callback_data=ChildCB(id=-1).pack(),
        )

    b.adjust(1)
    return b.as_markup()
