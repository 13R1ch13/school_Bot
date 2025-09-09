
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

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
