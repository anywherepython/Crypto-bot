from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import CURRENCY_LIST, CRYPTO_SYMBOLS


def generate_crypto_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=symbol, callback_data=f"crypto_{symbol}")]
        for symbol in CRYPTO_SYMBOLS
    ]
    keyboard.append(
        [InlineKeyboardButton(text="🏠 Menyuga", callback_data="back_to_main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_currency_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    per_page = 12
    start = page * per_page
    end = start + per_page
    currencies_page = CURRENCY_LIST[start:end]

    keyboard = []
    for i in range(0, len(currencies_page), 3):
        row_buttons = [
            InlineKeyboardButton(text=f"USD to {curr}", callback_data=curr)
            for curr in currencies_page[i : i + 3]
        ]
        keyboard.append(row_buttons)

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prev_{page - 1}")
        )
    if end < len(CURRENCY_LIST):
        navigation_buttons.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"next_{page + 1}")
        )

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    keyboard.append(
        [InlineKeyboardButton(text="🏠 Menyuga", callback_data="back_to_main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💵 Valyuta kurslari hisoblash",
                    callback_data="calculate_currency",
                ),
                InlineKeyboardButton(
                    text="💰 Kripto valyuta hisoblash", callback_data="calculate_crypto"
                ),
            ],
            [InlineKeyboardButton(text="📩 Yordam", callback_data="help")],
            [
                InlineKeyboardButton(
                    text="👨‍💻 Yaratuvchi bilan bog'lanish",
                    url="https://t.me/THE_NO_NAME7",
                )
            ],
        ],
    )
