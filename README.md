
# School Meals Bot UA — v2 (aiogram v3, SQLite)

Функції:
- Реєстрація батьків з підтвердженням ПІБ (прив’язка до Telegram ID)
- Реєстрація дитини: ПІБ ➜ вибір класу зі списку ➜ підтвердження
- Головне меню: «реєстрація дитини», «Замовлення»
- «Замовлення» відкриває Google-таблицю/форму (посилання в `.env`: ORDER_LINK)
- Тексти українською (як у твоєму ТЗ)

## Швидкий старт
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # заповни токен, ORDER_LINK, ADMIN_IDS за потреби
python bot.py
```

## .env
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ADMIN_IDS=448950529
TZ=Europe/Kyiv
ORDER_LINK=https://docs.google.com/...
```

## Команди / Кнопки
- /start або «Розпочати»: запуск і реєстрація батьків (ПІБ + підтвердження)
- «реєстрація дитини»: ПІБ дитини → підтвердження → вибір класу → підтвердження
- «Замовлення»: інструкція + відкриття Google-форми/таблиці
