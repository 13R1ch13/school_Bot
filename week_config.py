import os
from datetime import date, datetime, timedelta
from typing import List, Tuple

START_DATE = date(2025, 9, 1)


def build_weeks(count: int = 4) -> List[Tuple[str, str]]:
    weeks: List[Tuple[str, str]] = []
    for i in range(count):
        start = START_DATE + timedelta(weeks=i)
        end = start + timedelta(days=4)
        label = f"Тиждень {i + 1}"
        weeks.append((label, f"{start.strftime('%d.%m.%Y')} – {end.strftime('%d.%m.%Y')}"))
    return weeks


WEEKS = build_weeks()

WEEK_MENUS = {
    0: "Меню тижня 1: Страва A, Страва B",
    1: "Меню тижня 2: Страва C, Страва D",
    2: "Меню тижня 3: Страва E, Страва F",
    3: "Меню тижня 4: Страва G, Страва H",
}


def get_current_week(today: date | None = None) -> int:
    override = os.getenv("WEEK_OVERRIDE")
    if override and override.isdigit():
        idx = int(override)
        return max(0, min(idx, len(WEEKS) - 1))
    if today is None:
        today = date.today()
    for i, (_, rng) in enumerate(WEEKS):
        start_str, end_str = rng.split(" – ")
        start = datetime.strptime(start_str, "%d.%m.%Y").date()
        end = datetime.strptime(end_str, "%d.%m.%Y").date()
        if start <= today <= end:
            return i
    return 0


def get_week_menu(index: int) -> str:
    return WEEK_MENUS.get(index, "Меню недоступне")
