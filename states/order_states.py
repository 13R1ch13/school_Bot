from aiogram.fsm.state import StatesGroup, State


class OrderStates(StatesGroup):
    choose_child = State()
    choosing_week = State()
    choosing_day = State()
    choosing_meal = State()
    confirming = State()
