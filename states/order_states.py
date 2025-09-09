from aiogram.fsm.state import StatesGroup, State


class OrderStates(StatesGroup):
    choose_child = State()
    choosing_week = State()
    choosing_day_meal = State()
    confirming = State()
