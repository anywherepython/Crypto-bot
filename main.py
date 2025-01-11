import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import (
    Message,
    CallbackQuery,
)
from .config import (
    CURRENCY_LIST,
    CRYPTO_SYMBOLS,
    TOKEN,
)
from .buttons import (
    generate_main_menu,
    generate_currency_keyboard,
    generate_crypto_keyboard,
)
from .functions import (
    get_currency_rate,
    calculate_currency_amount,
    calculate_crypto_amount,
    get_crypto_compare_price,
)


bot = Bot(
    token=TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


SUBSCRIBE_CHANNELS = {}


async def check_user_subscription(user_id: int) -> list:
    not_subscribed = []
    for channel_id, url in SUBSCRIBE_CHANNELS.items():
        try:
            user_status = await bot.get_chat_member(channel_id, user_id)
            if user_status.status not in ["creator", "administrator", "member"]:
                not_subscribed.append(url)
        except Exception:
            not_subscribed.append(url)
    return not_subscribed


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    not_subscribed = await check_user_subscription(message.from_user.id)
    if not not_subscribed:
        main_menu = generate_main_menu()
        await message.answer(
            f"👋 Salom, {html.bold(message.from_user.full_name)}! Nima qilamiz?",
            reply_markup=main_menu,
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Obuna bo'lish", url=url)]
                for url in not_subscribed
            ]
            + [
                [
                    InlineKeyboardButton(
                        text="Obunani tekshirish", callback_data="check_subscription"
                    )
                ]
            ]
        )
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
            reply_markup=keyboard,
        )


@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription_callback(callback_query: CallbackQuery):
    not_subscribed = await check_user_subscription(callback_query.from_user.id)
    if not not_subscribed:
        main_menu = generate_main_menu()
        await callback_query.message.delete()
        await callback_query.message.answer(
            "🎉 Obuna muvaffaqiyatli tasdiqlandi!", reply_markup=main_menu
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Obuna bo'lish", url=url)]
                for url in not_subscribed
            ]
            + [
                [
                    InlineKeyboardButton(
                        text="Obunani tekshirish", callback_data="check_subscription"
                    )
                ]
            ]
        )
        await callback_query.message.delete()
        await callback_query.message.answer(
            "🚫 Siz hali quyidagi kanallarga obuna bo'lmadingiz:",
            reply_markup=keyboard,
        )


selected_currency = {}


@dp.callback_query()
async def menu_callback_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    not_subscribed = await check_user_subscription(user_id)

    if not not_subscribed:
        data = callback_query.data

        if data == "currency_menu":
            keyboard = generate_currency_keyboard(page=0)
            await callback_query.message.delete()
            await callback_query.message.answer(
                "💱 Valyuta kurslarini tanlang:", reply_markup=keyboard
            )

        elif data == "crypto_menu":
            keyboard = generate_crypto_keyboard()
            await callback_query.message.delete()
            await callback_query.message.answer(
                "🪙 Kripto valyutani tanlang:", reply_markup=keyboard
            )

        elif data == "help":
            await callback_query.message.answer(
                "👋 Yordamga xush kelibsiz! Bu bot orqali valyuta va kripto valyuta kurslarini hisoblash mumkin. "
                "Foydalanish bo'yicha qo'llanma:\n"
                "1. 💵 Valyuta kurslari hisoblash tugmasini bosing.\n"
                "2. O'zingiz hisoblamoqchi bo'lgan valyutani tanlang.\n"
                "3. USD miqdorini kiriting.\n"
                "4. Hisoblangan valyuta miqdorini oling.\n\n"
                "Kripto valyuta hisoblash uchun 💰 Kripto valyuta hisoblash' tugmasini bosing va kerakli kripto valyutani tanlang.",
                reply_markup=generate_main_menu(),
            )

        elif data == "back_to_main":
            main_menu = generate_main_menu()
            await callback_query.message.delete()
            await callback_query.message.answer(
                "🏠 Asosiy menyu:", reply_markup=main_menu
            )

        elif data.startswith("next_") or data.startswith("prev_"):
            page = int(data.split("_")[1])
            keyboard = generate_currency_keyboard(page=page)
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)

        elif data == "calculate_currency":
            keyboard = generate_currency_keyboard(page=0)
            await callback_query.message.delete()
            await callback_query.message.answer(
                "💵 Qaysi valyutani hisoblashni xohlaysiz?", reply_markup=keyboard
            )

        elif data == "calculate_crypto":
            keyboard = generate_crypto_keyboard()
            await callback_query.message.delete()
            await callback_query.message.answer(
                "💰 Qaysi kripto valyutani hisoblashni xohlaysiz?",
                reply_markup=keyboard,
            )

        elif data.startswith("crypto_"):
            symbol = data.split("_")[1]
            selected_currency[callback_query.from_user.id] = symbol
            await callback_query.message.delete()
            await callback_query.message.answer(
                f"🔢 {symbol} tanlandi. Miqdorni kiriting:"
            )

        elif data in CURRENCY_LIST:
            selected_currency[callback_query.from_user.id] = data
            await callback_query.message.delete()
            await callback_query.message.answer(
                f"🔢 {data} tanlandi. USD miqdorini kiriting:"
            )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Obuna bo'lish", url=url)]
                for url in not_subscribed
            ]
            + [
                [
                    InlineKeyboardButton(
                        text="Obunani tekshirish", callback_data="check_subscription"
                    )
                ]
            ]
        )
        await callback_query.message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
            reply_markup=keyboard,
        )

    await callback_query.answer()


@dp.message()
async def amount_handler(message: Message):
    user_id = message.from_user.id
    not_subscribed = await check_user_subscription(user_id)

    if not_subscribed:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Obuna bo'lish", url=url)]
                for url in not_subscribed
            ]
            + [
                [
                    InlineKeyboardButton(
                        text="Obunani tekshirish", callback_data="check_subscription"
                    )
                ]
            ]
        )
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
            reply_markup=keyboard,
        )
    else:
        user_id = message.from_user.id
        if user_id in selected_currency:
            currency = selected_currency[user_id]
            try:
                amount = float(message.text.strip())

                if currency in CURRENCY_LIST:
                    rate = get_currency_rate(currency)
                    if rate:
                        result = calculate_currency_amount(amount, rate)
                        keyboard = generate_currency_keyboard(page=0)
                        await message.answer(
                            f"💵 <b>{amount} USD = {result:.2f} {currency}</b> 🌍\n\n"
                            f"🔄 <i>1 USD = {rate:.2f} {currency}</i> 📈",
                            reply_markup=keyboard,
                        )
                    else:
                        await message.answer(
                            f"😕 <b>Kechirasiz, {currency} valyutasi bo'yicha kurs topilmadi.</b> ❌"
                        )
                elif currency in CRYPTO_SYMBOLS:
                    prices = get_crypto_compare_price()
                    if prices and currency in prices:
                        crypto_price = prices[currency]["USD"]
                        result = calculate_crypto_amount(amount, crypto_price)
                        keyboard = generate_crypto_keyboard()
                        await message.answer(
                            f"🪙 <b>{amount} {currency} = {result} USD</b> 💰\n"
                            f"🔄 <i>1 {currency} = {crypto_price} USD</i> 🚀",
                            reply_markup=keyboard,
                        )
                    else:
                        await message.answer(
                            f"😕 <b>Kechirasiz, {currency} narxi topilmadi.</b> ❌"
                        )
            except ValueError:
                await message.answer("⚠️ <b>Miqdorni to'g'ri kiriting.</b> ❗️")
        else:
            await message.answer(
                "⚠️ <b>Avval valyuta yoki kripto valyutani tanlang.</b> 💡"
            )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
