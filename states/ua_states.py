
from aiogram.fsm.state import StatesGroup, State

class ParentReg(StatesGroup):
    waiting_parent_name = State()
    confirm_parent = State()

class ChildReg(StatesGroup):
    waiting_child_name = State()
    confirm_child_name = State()
    choose_class = State()
    confirm_child_all = State()
