from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from db.database import (
    upsert_parent,
    set_parent_name_and_verify,
    get_parent,
    add_child,
)
from keyboards.common import (
    start_menu,
    main_menu,
    confirm_kb,
    ConfirmCB,
    class_list_kb,
    ClassCB,
)
from states.ua_states import ParentReg, ChildReg


router = Router()


WELCOME = "\n".join(
    [
        "Напишіть ваше Ім'я та Прізвище (не дитини)",
        "Наприклад: <b>Атанасова Марiя</b>",
    ]
)


@router.message(CommandStart())
async def cmd_start(m: Message, state: FSMContext):
    upsert_parent(m.from_user.id)
    p = get_parent(m.from_user.id)
    if not p or not p["verified"]:
        await state.set_state(ParentReg.waiting_parent_name)
        await m.answer(WELCOME, reply_markup=start_menu())
    else:
        await m.answer("Головне меню:", reply_markup=main_menu())


@router.message(F.text.casefold() == "розпочати")
async def btn_start(m: Message, state: FSMContext):
    await cmd_start(m, state)


# --- Parent registration ---
@router.message(ParentReg.waiting_parent_name)
async def parent_name_entered(m: Message, state: FSMContext):
    full = m.text.strip()
    if len(full.split()) < 2:
        await m.answer(
            "Введіть, будь ласка, Прізвище та Ім'я повністю (напр.: <b>Атанасова Марiя</b>)."
        )
        return
    await state.update_data(parent_full=full)
    await state.set_state(ParentReg.confirm_parent)
    await m.answer(f"Вас звати <b>{full}</b>?", reply_markup=confirm_kb())


@router.callback_query(ConfirmCB.filter(), ParentReg.confirm_parent)
async def parent_confirm(call: CallbackQuery, callback_data: ConfirmCB, state: FSMContext):
    data = await state.get_data()
    full = data.get("parent_full", "")
    if callback_data.ok == 1:
        set_parent_name_and_verify(call.from_user.id, full, 1)
        await state.clear()
        await call.message.edit_text("Реєстрацію підтверджено.")
        await call.message.answer("Головне меню:", reply_markup=main_menu())
    else:
        await call.message.edit_text("Добре, введіть ПІБ ще раз:\nНапр.: <b>Супінський Річард</b>")
        await state.set_state(ParentReg.waiting_parent_name)


# --- Child registration ---
@router.message(F.text.casefold() == "реєстрація дитини")
async def child_reg_entry(m: Message, state: FSMContext):
    p = get_parent(m.from_user.id)
    if not p or not p["verified"]:
        await m.answer("Спочатку завершіть реєстрацію батьків (кнопка «Розпочати»).")
        return
    await state.set_state(ChildReg.waiting_child_name)
    await m.answer("Напишіть Прізвище та Ім'я дитини (напр.: <b>Атанасов Iван</b>):")


@router.message(ChildReg.waiting_child_name)
async def child_name_entered(m: Message, state: FSMContext):
    child = m.text.strip()
    await state.update_data(child_full=child)
    await state.set_state(ChildReg.confirm_child_name)
    await m.answer(f"Ім'я дитини (<b>{child}</b>) вірно?", reply_markup=confirm_kb())


@router.callback_query(ConfirmCB.filter(), ChildReg.confirm_child_name)
async def child_name_confirm(call: CallbackQuery, callback_data: ConfirmCB, state: FSMContext):
    if callback_data.ok == 1:
        await state.set_state(ChildReg.choose_class)
        data = await state.get_data()
        child = data.get("child_full", "")
        await call.message.edit_text(f"Оберіть у якому класі вчиться <b>{child}</b>:")
        await call.message.edit_reply_markup(reply_markup=class_list_kb())
    else:
        await call.message.edit_text("Вкажіть ПІБ дитини ще раз:")
        await state.set_state(ChildReg.waiting_child_name)


@router.callback_query(ClassCB.filter(), ChildReg.choose_class)
async def class_chosen(call: CallbackQuery, callback_data: ClassCB, state: FSMContext):
    await state.update_data(class_label=callback_data.label)
    data = await state.get_data()
    child = data.get("child_full", "")
    klass = data.get("class_label", "")
    await state.set_state(ChildReg.confirm_child_all)
    await call.message.edit_text(f"Підтвердьте: <b>{child}</b> — <b>{klass}</b>")
    await call.message.edit_reply_markup(reply_markup=confirm_kb())


@router.callback_query(ConfirmCB.filter(), ChildReg.confirm_child_all)
async def child_all_confirm(call: CallbackQuery, callback_data: ConfirmCB, state: FSMContext):
    if callback_data.ok == 1:
        p = get_parent(call.from_user.id)
        d = await state.get_data()
        if p:
            add_child(p["id"], d.get("child_full", ""), d.get("class_label", ""))
        await state.clear()
        await call.message.edit_text("Збережено!✅")
        await call.message.answer("Повертаємось у головне меню.", reply_markup=main_menu())
    else:
        await call.message.edit_text("Повертаємось до вибору класу:")
        await state.set_state(ChildReg.choose_class)
        await call.message.edit_reply_markup(reply_markup=class_list_kb())


