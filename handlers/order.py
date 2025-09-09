from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import WEEKS
from db.database import (
    get_parent,
    get_parent_children,
    add_order,
)
from keyboards.common import (
    children_kb,
    ChildCB,
    confirm_kb,
    ConfirmCB,
)

router = Router()


class OrderStates(StatesGroup):
    choose_child = State()
    choosing_week = State()
    choosing_day = State()
    choosing_meal = State()
    confirming = State()

DAYS = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]

MEALS = ["Сніданок солоний", "Сніданок солодкий", "Обід", "Полуденок"]


@router.message(F.text.casefold() == "замовлення")
async def start_order(message: Message, state: FSMContext):
    parent = get_parent(message.from_user.id)
    if not parent or not parent["verified"]:
        await message.answer("Спочатку завершіть реєстрацію батьків (кнопка «Розпочати»).")
        return
    children = get_parent_children(parent["id"])
    if not children:
        await message.answer("Спочатку зареєструйте дитину.")
        return
    if len(children) == 1:
        await state.update_data(child_ids=[children[0]["id"]])
        await _ask_week(message, state)
    else:
        await state.set_state(OrderStates.choose_child)
        await message.answer("Оберіть дитину:", reply_markup=children_kb(children))


@router.callback_query(ChildCB.filter(), OrderStates.choose_child)
async def child_chosen(call: CallbackQuery, callback_data: ChildCB, state: FSMContext):
    parent = get_parent(call.from_user.id)
    children = get_parent_children(parent["id"]) if parent else []
    if callback_data.id == -1:
        ids = [ch["id"] for ch in children]
    else:
        ids = [callback_data.id]
    await state.update_data(child_ids=ids)
    await _ask_week(call.message, state)
    await call.answer()


async def _ask_week(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    for i, (label, _) in enumerate(WEEKS):
        builder.button(text=label, callback_data=f"week_{i}")
    builder.adjust(2)
    await state.set_state(OrderStates.choosing_week)
    await message.answer("📆 Оберіть тиждень:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("week_"), OrderStates.choosing_week)
async def week_chosen(callback: CallbackQuery, state: FSMContext):
    week_index = int(callback.data.split("_")[1])
    await state.update_data(week=WEEKS[week_index][0])
    builder = InlineKeyboardBuilder()
    for i, label in enumerate(DAYS):
        builder.button(text=label, callback_data=f"day_{i}")
    builder.adjust(2)
    await state.set_state(OrderStates.choosing_day)
    await callback.message.answer("🗓 Оберіть день:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("day_"), OrderStates.choosing_day)
async def day_chosen(callback: CallbackQuery, state: FSMContext):
    day_index = int(callback.data.split("_")[1])
    await state.update_data(day=DAYS[day_index])
    builder = InlineKeyboardBuilder()
    for i, label in enumerate(MEALS):
        builder.button(text=label, callback_data=f"meal_{i}")
    builder.adjust(1)
    await state.set_state(OrderStates.choosing_meal)
    await callback.message.answer("🍽 Оберіть прийом їжі:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("meal_"), OrderStates.choosing_meal)
async def meal_chosen(callback: CallbackQuery, state: FSMContext):
    meal_index = int(callback.data.split("_")[1])
    await state.update_data(meal=MEALS[meal_index])
    data = await state.get_data()
    summary = f"<b>{data.get('week')}</b>\\n{data.get('day')} — {data.get('meal')}"
    await state.set_state(OrderStates.confirming)
    await callback.message.answer(summary, reply_markup=confirm_kb())
    await callback.answer()


@router.callback_query(ConfirmCB.filter(), OrderStates.confirming)
async def confirm_order(callback: CallbackQuery, callback_data: ConfirmCB, state: FSMContext):
    if callback_data.ok == 1:
        parent = get_parent(callback.from_user.id)
        data = await state.get_data()
        for child_id in data.get("child_ids", []):
            add_order(parent["id"], child_id, data.get("week"), data.get("day"), data.get("meal"))
        await callback.message.edit_text("Замовлення збережено!✅")
        await state.clear()
    else:
        await callback.message.edit_text("Скасовано.")
        await state.clear()
    await callback.answer()
