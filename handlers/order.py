from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.ua_states import OrderStates

router = Router()

# 📆 Полный список недель (взятый из скрина)
WEEKS = [
    ("Тиждень 1", "01.09.2025 – 05.09.2025"),
    ("Тиждень 2", "08.09.2025 – 12.09.2025"),
    ("Тиждень 3", "15.09.2025 – 19.09.2025"),
    ("Тиждень 4", "22.09.2025 – 26.09.2025"),
    ("Тиждень 5", "29.09.2025 – 03.10.2025"),
    ("Тиждень 6", "06.10.2025 – 10.10.2025"),
    ("Тиждень 7", "13.10.2025 – 17.10.2025"),
    ("Тиждень 8", "20.10.2025 – 24.10.2025"),
    ("Тиждень 9", "27.10.2025 – 31.10.2025"),
    ("Тиждень 10", "03.11.2025 – 07.11.2025"),
    ("Тиждень 11", "10.11.2025 – 14.11.2025"),
    ("Тиждень 12", "17.11.2025 – 21.11.2025"),
    ("Тиждень 13", "24.11.2025 – 28.11.2025"),
    ("Тиждень 14", "01.12.2025 – 05.12.2025"),
    ("Тиждень 15", "08.12.2025 – 12.12.2025"),
    ("Тиждень 16", "15.12.2025 – 19.12.2025"),
    ("Тиждень 17", "22.12.2025 – 26.12.2025"),
    ("Тиждень 18", "29.12.2025 – 31.12.2025"),
]

DAYS = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]

MEALS = ["Сніданок солоний", "Сніданок солодкий", "Обід", "Полуденок"]


@router.message(F.text.casefold() == "замовлення")
async def start_order(message: Message, state: FSMContext):
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
    for i, day in enumerate(DAYS):
        builder.button(text=day, callback_data=f"day_{i}")
    builder.adjust(1)
    await state.set_state(OrderStates.choosing_day)
    await callback.message.edit_text(f"✅ Ви обрали: {WEEKS[week_index][0]}\nОберіть день:")
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("day_"), OrderStates.choosing_day)
async def day_chosen(callback: CallbackQuery, state: FSMContext):
    day_index = int(callback.data.split("_")[1])
    await state.update_data(day=DAYS[day_index])
    builder = InlineKeyboardBuilder()
    for i, meal in enumerate(MEALS):
        builder.button(text=meal, callback_data=f"meal_{i}")
    builder.adjust(1)
    await state.set_state(OrderStates.choosing_meal)
    await callback.message.edit_text(
        f"День: {DAYS[day_index]}\nОберіть прийом їжі:")
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("meal_"), OrderStates.choosing_meal)
async def meal_chosen(callback: CallbackQuery, state: FSMContext):
    meal_index = int(callback.data.split("_")[1])
    meal = MEALS[meal_index]
    await state.update_data(meal=meal)
    data = await state.get_data()
    builder = InlineKeyboardBuilder()
    builder.button(text="Так", callback_data="confirm_yes")
    builder.button(text="Ні", callback_data="confirm_no")
    builder.adjust(2)
    await state.set_state(OrderStates.confirming)
    await callback.message.edit_text(
        "\n".join([
            "Підтвердьте замовлення:",
            f"Тиждень: {data['week']}",
            f"День: {data['day']}",
            f"Харчування: {meal}",
        ])
    )
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_"), OrderStates.confirming)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm_yes":
        data = await state.get_data()
        await callback.message.edit_text(
            "\n".join([
                "✅ Замовлення підтверджено:",
                f"Тиждень: {data['week']}",
                f"День: {data['day']}",
                f"Харчування: {data['meal']}",
            ])
        )
    else:
        await callback.message.edit_text("❌ Замовлення скасовано.")
    await state.clear()
    await callback.answer()
