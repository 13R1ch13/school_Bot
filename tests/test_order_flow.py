import pathlib
import sys
import types

import asyncio
import pytest

# Ensure project root on sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from handlers import order
from handlers.order import (
    OrderStates,
    child_chosen,
    week_chosen,
    day_chosen,
    meal_chosen,
    confirm_order,
)
from keyboards.common import ChildCB, ConfirmCB


class DummyMessage:
    def __init__(self):
        self.answers = []
        self.edits = []

    async def answer(self, text, reply_markup=None):
        self.answers.append(text)

    async def edit_text(self, text):
        self.edits.append(text)


class DummyCallbackQuery:
    def __init__(self, data, message):
        self.data = data
        self.message = message
        self.from_user = types.SimpleNamespace(id=123)
        self.answered = False

    async def answer(self):
        self.answered = True


class DummyFSM:
    def __init__(self):
        self.state = None
        self.data = {}

    async def set_state(self, state):
        self.state = state

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data

    async def clear(self):
        self.state = None
        self.data = {}


def test_order_state_transitions(monkeypatch):
    """Ensure the order handler transitions through all states."""

    async def scenario():
        fsm = DummyFSM()
        fsm.state = OrderStates.choose_child
        message = DummyMessage()

        monkeypatch.setattr(order, "get_parent", lambda user_id: {"id": 1})
        monkeypatch.setattr(order, "get_parent_children", lambda parent_id: [{"id": 5}])
        monkeypatch.setattr(
            order,
            "get_menu_for_week",
            lambda week: {"Понеділок": [{"meal": "A"}]},
        )
        monkeypatch.setattr(
            order,
            "get_meal_info",
            lambda week, day, meal: {"description": "d", "price": 1},
        )

        cb = DummyCallbackQuery("", message)
        await child_chosen(cb, ChildCB(id=5), fsm)
        assert fsm.state == OrderStates.choosing_week

        cb = DummyCallbackQuery("week_0", message)
        prev_len = len(message.answers)
        await week_chosen(cb, fsm)
        assert message.answers[prev_len].startswith("Меню на тиждень")
        assert fsm.state == OrderStates.choosing_day

        cb = DummyCallbackQuery("day_0", message)
        await day_chosen(cb, fsm)
        assert fsm.state == OrderStates.choosing_meal

        cb = DummyCallbackQuery("meal_0", message)
        await meal_chosen(cb, fsm)
        assert fsm.state == OrderStates.confirming

    asyncio.run(scenario())


def test_confirmation_text(monkeypatch):
    """The summary message should include week, day and meal."""

    async def scenario():
        fsm = DummyFSM()
        fsm.state = OrderStates.choose_child
        message = DummyMessage()

        monkeypatch.setattr(order, "get_parent", lambda user_id: {"id": 1})
        monkeypatch.setattr(order, "get_parent_children", lambda parent_id: [{"id": 5}])
        monkeypatch.setattr(order, "get_menu_for_week", lambda week: {})
        monkeypatch.setattr(
            order,
            "get_meal_info",
            lambda week, day, meal: {"description": "Desc", "price": 5},
        )

        cb = DummyCallbackQuery("", message)
        await child_chosen(cb, ChildCB(id=5), fsm)
        cb = DummyCallbackQuery("week_0", message)
        await week_chosen(cb, fsm)
        cb = DummyCallbackQuery("day_0", message)
        await day_chosen(cb, fsm)
        cb = DummyCallbackQuery("meal_0", message)
        await meal_chosen(cb, fsm)

        assert (
            message.answers[-1]
            == f"<b>{order.WEEKS[0][0]}</b>\\n{order.DAYS[0]} — {order.MEALS[0]}\n\nDesc\nЦіна: 5 грн"
        )

    asyncio.run(scenario())


def test_add_order_called(monkeypatch):

    async def scenario():
        fsm = DummyFSM()
        await fsm.update_data(child_ids=[1, 2], week="W1", day="D1", meal="M1")
        fsm.state = OrderStates.confirming
        message = DummyMessage()

        captured = []

        monkeypatch.setattr(order, "get_parent", lambda user_id: {"id": 10})

        def fake_add(parent_id, child_id, week, day, meal):
            captured.append((parent_id, child_id, week, day, meal))

        monkeypatch.setattr(order, "add_order", fake_add)

        cb = DummyCallbackQuery("", message)
        await confirm_order(cb, ConfirmCB(ok=1), fsm)

        assert captured == [
            (10, 1, "W1", "D1", "M1"),
            (10, 2, "W1", "D1", "M1"),
        ]

    asyncio.run(scenario())

