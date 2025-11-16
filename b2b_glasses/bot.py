# --- 1. ЗАГРУЗЧИК ---
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Tuple, List, Dict, Any
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, WebAppInfo, InlineKeyboardButton, BotCommand,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    CallbackQuery
)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, html, F
from django.conf import settings
from decimal import Decimal, InvalidOperation
import math
import json
import aiohttp
import asyncio
import os
import django
import sys
import logging
import logging.handlers
from pathlib import Path

print("[DEBUG] bot_loader.py (v4.3): Запускаю настройку Django...")
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b2b_glasses.settings')

try:
    django.setup()
    print("[DEBUG] bot_loader.py (v4.3): Настройка Django завершена.")
except Exception as e:
    print(
        f"[DEBUG] bot_loader.py (v4.3): КРИТИЧЕСКАЯ ОШИБКА. Не удалось настроить Django: {e}")
    raise


def setup_bot_logging():
    log_dir = PROJECT_ROOT / "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = log_dir / "bot.log"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024 * 1024 * 5, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.getLogger("aiogram.client").setLevel(logging.WARNING)
    logger.info("--- Логгирование бота успешно настроено ---")


setup_bot_logging()
# --- КОНЕЦ ЗАГРУЗЧИКА ---


# --- 2. ВСЕ ИМПОРТЫ ---


# --- 3. FSM СОСТОЯНИЯ ---


class RegistrationFSM(StatesGroup):
    waiting_for_phone = State()
    waiting_for_password = State()


class LensFilterFSM(StatesGroup):
    waiting_for_series = State()
    waiting_for_sph = State()
    waiting_for_cyl = State()
    waiting_for_dia = State()
    waiting_for_search_query = State()
    waiting_for_add_id = State()
    waiting_for_add_qty = State()


# --- 4. НАСТРОЙКИ И API-КЛИЕНТ ---
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
WEBSITE_URL = settings.WEBSITE_URL
LENS_PAGE_SIZE = settings.REST_FRAMEWORK.get('PAGE_SIZE', 5)

# URL'ы
DJANGO_REG_URL = settings.DJANGO_REG_URL
CHECK_STATUS_URL = settings.CHECK_STATUS_URL
LENS_OPTIONS_URL = settings.LENS_OPTIONS_URL
LENS_LIST_URL = settings.LENS_LIST_URL
# Секрет
BOT_API_SECRET = settings.BOT_API_SECRET
BOT_AUTH_HEADER = {"X-Bot-Token": BOT_API_SECRET}

# URL Заказов
CART_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/cart/"
CART_ADD_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/cart/add/"
CART_CLEAR_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/cart/clear/"
CART_CHECKOUT_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/cart/checkout/"
HISTORY_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/history/"

logger = logging.getLogger(__name__)
dp = Dispatcher(storage=MemoryStorage())

# ---
# 5. ВСЕ ФУНКЦИИ API
# ---


async def check_user_status(telegram_id: int) -> bool:
    params = {"telegram_id": telegram_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CHECK_STATUS_URL, headers=BOT_AUTH_HEADER, params=params) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"Критическая ошибка проверки статуса: {e}")
        return False


async def register_user(payload: dict) -> Tuple[bool, str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DJANGO_REG_URL, json=payload) as response:
                if response.status == 200:
                    return True, "Успех"
                error_message = "Неизвестная ошибка"
                try:
                    response_json = await response.json()
                    errors = []
                    if 'error' in response_json:
                        errors.append(response_json['error'])
                    else:
                        for field, messages in response_json.items():
                            errors.append(
                                f"{field}: {', '.join(messages) if isinstance(messages, list) else messages}")
                    if errors:
                        error_message = "\n".join(errors)
                except Exception:
                    error_message = f"Ошибка сервера ({response.status})."
                logger.warning(
                    f"Ошибка регистрации (Django): {response.status} - {error_message}")
                return False, error_message
    except Exception as e:
        logger.error(f"Критическая ошибка регистрации (aiohttp): {e}")
        return False, "Ошибка: не удалось подключиться к серверу."


async def get_lens_filter_options(telegram_id: int) -> dict | None:
    params = {"telegram_id": telegram_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(LENS_OPTIONS_URL, headers=BOT_AUTH_HEADER, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(
                    f"Сервер опций НЕ ПУСТИЛ (TG ID: {telegram_id}, Status: {response.status})")
                return None
    except Exception as e:
        logger.error(f"Ошибка получения опций фильтра: {e}")
        return None


async def get_lens_results(params: dict) -> dict | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(LENS_LIST_URL, headers=BOT_AUTH_HEADER, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(
                    f"Сервер товаров НЕ ПУСТИЛ (Status: {response.status})")
                return None
    except Exception as e:
        logger.error(f"Ошибка получения списка линз: {e}")
        return None


async def get_cart(telegram_id: int, auth_token: str) -> dict | None:
    headers = {"Authorization": f"Token {auth_token}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CART_URL, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(
                    f"Не удалось получить корзину (TG ID: {telegram_id}): {response.status}")
                return None
    except Exception as e:
        logger.error(f"Ошибка get_cart: {e}")
        return None


async def add_to_cart(auth_token: str, product_type: str, product_id: int, quantity: int) -> bool:
    headers = {"Authorization": f"Token {auth_token}"}
    payload = {
        "product_type": product_type,
        "product_id": product_id,
        "quantity": quantity
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(CART_ADD_URL, headers=headers, json=payload) as response:
                return response.status == 201
    except Exception as e:
        logger.error(f"Ошибка add_to_cart: {e}")
        return False


async def clear_cart(auth_token: str) -> bool:
    headers = {"Authorization": f"Token {auth_token}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(CART_CLEAR_URL, headers=headers) as response:
                return response.status == 204
    except Exception as e:
        logger.error(f"Ошибка clear_cart: {e}")
        return False


async def checkout_cart(auth_token: str) -> dict | None:
    headers = {"Authorization": f"Token {auth_token}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(CART_CHECKOUT_URL, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Ошибка checkout_cart: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Ошибка checkout_cart: {e}")
        return None


async def get_history(auth_token: str, page: int = 1) -> dict | None:
    headers = {"Authorization": f"Token {auth_token}"}
    params = {"page": page, "page_size": 5}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(HISTORY_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Ошибка get_history: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Ошибка get_history: {e}")
        return None

# ---
# 6. ВСЕ ФУНКЦИИ КЛАВИАТУР
# ---

BUTTONS_PER_PAGE = 8


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Оправы (Перейти на сайт)", url=WEBSITE_URL))
    builder.row(InlineKeyboardButton(
        text="Линзы (Подобрать в боте)", callback_data="start_lens_filter"))
    builder.row(InlineKeyboardButton(
        text="Поиск Линз (по ID или Серии)", callback_data="start_lens_search"))
    builder.row(
        InlineKeyboardButton(text="🛒 Моя Корзина", callback_data="view_cart"),
        InlineKeyboardButton(text="📜 История Заказов",
                             callback_data="view_history")
    )
    return builder.as_markup()


def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поделиться номером телефона", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )


def build_filter_buttons(items: list, prefix: str, page: int = 1, show_back_button: bool = False) -> InlineKeyboardBuilder:
    """
    (v4.2) ВОЗВРАЩАЕТ BUILDER (а не as_markup())
    """
    builder = InlineKeyboardBuilder()
    total_items = len(items)
    total_pages = (total_items + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE
    start_index = (page - 1) * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    items_on_page = items[start_index:end_index]
    if items and isinstance(items[0], dict):
        for item in items_on_page:
            builder.row(InlineKeyboardButton(
                text=item['name'], callback_data=f"{prefix}_select_{item['id']}"))
    else:
        buttons = [InlineKeyboardButton(text=str(
            val), callback_data=f"{prefix}_select_{val}") for val in items_on_page]
        builder.row(*buttons, width=3)
    if total_pages > 1:
        row = []
        if page > 1:
            row.append(InlineKeyboardButton(
                text="<", callback_data=f"{prefix}_page_{page - 1}"))
        row.append(InlineKeyboardButton(
            text=f"{page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            row.append(InlineKeyboardButton(
                text=">", callback_data=f"{prefix}_page_{page + 1}"))
        builder.row(*row)
    back_button = []
    if show_back_button:
        # (Мы определяем 'назад' в update_filter_message)
        pass
    back_button.append(InlineKeyboardButton(
        text="❌ Отмена", callback_data="filter_cancel"))
    builder.row(*back_button)
    return builder  # <-- Возвращаем Builder


def build_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page_") -> InlineKeyboardBuilder:
    """
    (v4.2) ВОЗВРАЩАЕТ BUILDER (а не as_markup())
    """
    builder = InlineKeyboardBuilder()
    prev_page = InlineKeyboardButton(
        text="<", callback_data=f"{prefix}{current_page - 1}")
    next_page = InlineKeyboardButton(
        text=">", callback_data=f"{prefix}{current_page + 1}")
    page_info = InlineKeyboardButton(
        text=f"{current_page} / {total_pages}", callback_data="noop")
    row = []
    if current_page > 1:
        row.append(prev_page)
    row.append(page_info)
    if current_page < total_pages:
        row.append(next_page)
    builder.row(*row)
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть", callback_data="filter_cancel"))
    return builder  # <-- Возвращаем Builder


def get_cart_keyboard(cart_is_empty: bool) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if not cart_is_empty:
        builder.row(InlineKeyboardButton(
            text="✅ Оформить заказ", callback_data="cart_checkout"))
        builder.row(InlineKeyboardButton(
            text="🗑 Очистить корзину", callback_data="cart_clear"))
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть", callback_data="filter_cancel"))
    return builder.as_markup()

# ---
# 7. ВСЕ ХЭНДЛЕРЫ БОТА
# ---

# --- Регистрация ---


@dp.message(CommandStart(deep_link=True))
async def handler_start_with_token(message: Message, state: FSMContext):
    if await check_user_status(message.from_user.id):
        await message.answer("Вы уже зарегистрированы...", reply_markup=get_main_menu_keyboard())
        return
    try:
        token = message.text.split()[1]
    except IndexError:
        await message.answer("Ошибка: неверный формат ссылки...")
        return
    await state.update_data(token=token)
    await state.set_state(RegistrationFSM.waiting_for_phone)
    await message.answer(
        f"Здравствуйте, {html.bold(message.from_user.full_name)}!\n\n"
        "Для завершения регистрации, пожалуйста, поделитесь вашим номером телефона.",
        reply_markup=get_phone_keyboard()
    )


@dp.message(RegistrationFSM.waiting_for_phone, F.contact)
async def handler_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    await state.set_state(RegistrationFSM.waiting_for_password)
    await message.answer(
        "Спасибо! Теперь придумайте пароль. "
        "Этот пароль будет использоваться для входа на сайт.",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(RegistrationFSM.waiting_for_password, F.text, ~F.text.startswith('/'))
async def handler_password(message: Message, state: FSMContext):
    password = message.text
    try:
        await message.delete()
        await message.answer("Пароль получен. Регистрирую вас...")
    except Exception:
        await message.answer("Пароль получен. Регистрирую вас...")
    data = await state.get_data()
    payload = {
        "token": data.get('token'), "password": password,
        "phone_number": data.get('phone_number'),
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
    }
    logger.info(f"Попытка регистрации для TG ID: {message.from_user.id}")
    success, error_message = await register_user(payload)
    if success:
        logger.info(f"Успешная регистрация для TG ID: {message.from_user.id}")
        login_info_text = (
            f"✅ <b>Регистрация прошла успешно!</b>\n\n"
            f"Ваши данные для входа на сайт:\n"
            f"<b>Сайт:</b> {WEBSITE_URL}\n"
            f"<b>Логин:</b> {data.get('phone_number')}\n"
            f"<b>Пароль:</b> <tg-spoiler>{html.quote(password)}</tg-spoiler>"
        )
        sent_message = await message.answer(login_info_text)
        try:
            await message.bot.pin_chat_message(
                chat_id=message.chat.id, message_id=sent_message.message_id, disable_notification=True
            )
        except Exception as e:
            logger.warning(f"Не удалось закрепить сообщение: {e}")
        await message.answer(
            "Воспользуйтесь меню ниже, чтобы выбрать категорию.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    else:
        logger.warning(
            f"Ошибка регистрации для TG ID {message.from_user.id}: {error_message}")
        await message.answer(
            f"❌ Ошибка регистрации:\n{error_message}\n\n"
            "Попробуйте ввести пароль еще раз. (Или /cancel для отмены)"
        )
        await state.set_state(RegistrationFSM.waiting_for_password)
        return

# --- Главное меню ---


@dp.message(CommandStart())
async def handler_start_simple(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f"Пользователь {message.from_user.id} нажал /start")
    if await check_user_status(message.from_user.id):
        await message.answer(
            f"Здравствуйте, {html.bold(message.from_user.full_name)}! "
            "Выберите, что вас интересует:",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            f"Здравствуйте, {html.bold(message.from_user.full_name)}!\n\n"
            "Ваш аккаунт неактивен или еще не привязан."
        )

# --- Логика Фильтра (Чистый UI) ---


async def update_filter_message(bot: Bot, chat_id: int, message_id: int, state: FSMContext, page: int = 1):
    data = await state.get_data()
    options = data.get('options', {})
    text = "<b>--- Фильтр Линз ---</b>\n"
    text += f"1. Серия: {html.quote(data.get('series_name', '...'))}\n"
    text += f"2. SPH: {html.quote(data.get('sph', '...'))}\n"
    text += f"3. CYL: {html.quote(data.get('cyl', '...'))}\n"
    text += f"4. DIA: {html.quote(data.get('dia', '...'))}\n"
    text += "--------------------\n"
    current_fsm_state = await state.get_state()
    keyboard_builder = InlineKeyboardBuilder()
    if current_fsm_state == LensFilterFSM.waiting_for_series:
        text += f"<b>Шаг 1 из 4: Выберите серию линз (Стр. {page})</b>"
        keyboard_builder.attach(
            build_filter_buttons(options.get('series', []),
                                 "filter_series", page, show_back_button=False)
        )
    elif current_fsm_state == LensFilterFSM.waiting_for_sph:
        text += "<b>Шаг 2 из 4: Введите Сферу (SPH)</b>\n\n<i>(Например: <b>-2.5</b>)</i>"
        keyboard_builder.row(
            InlineKeyboardButton(
                text="↩️ Назад", callback_data="filter_back_to_series"),
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="filter_cancel")
        )
    elif current_fsm_state == LensFilterFSM.waiting_for_cyl:
        text += "<b>Шаг 3 из 4: Введите Цилиндр (CYL)</b>\n\n<i>(Например: <b>-0.75</b> или <b>0</b>)</i>"
        keyboard_builder.row(
            InlineKeyboardButton(
                text="↩️ Назад", callback_data="filter_back_to_sph"),
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="filter_cancel")
        )
    elif current_fsm_state == LensFilterFSM.waiting_for_dia:
        text += f"<b>Шаг 4 из 4: Выберите Диаметр (DIA) (Стр. {page})</b>"
        keyboard_builder.attach(
            build_filter_buttons(options.get('dia', []),
                                 "filter_dia", page, show_back_button=True)
        )
    try:
        await bot.edit_message_text(
            text=text, chat_id=chat_id, message_id=message_id,
            reply_markup=keyboard_builder.as_markup()
        )
    except Exception:
        new_msg = await bot.send_message(
            chat_id=chat_id, text=text,
            reply_markup=keyboard_builder.as_markup()
        )
        await state.update_data(active_message_id=new_msg.message_id)


@dp.callback_query(F.data == "start_lens_filter")
async def filter_step_1_series(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("Загружаю опции фильтра...")
    options = await get_lens_filter_options(query.from_user.id)
    if options is None or not options.get('series'):
        await query.message.edit_text("❌ Ошибка: не удалось загрузить опции фильтра.")
        return
    await state.update_data(
        options=options,
        active_message_id=query.message.message_id,
        chat_id=query.message.chat.id,
        telegram_id=query.from_user.id
    )
    await state.set_state(LensFilterFSM.waiting_for_series)
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=1)


@dp.callback_query(LensFilterFSM.waiting_for_series, F.data.startswith("filter_series_page_"))
async def filter_step_1_paging(query: CallbackQuery, state: FSMContext):
    page = int(query.data.split('_')[-1])
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=page)


@dp.callback_query(LensFilterFSM.waiting_for_series, F.data.startswith("filter_series_select_"))
async def filter_step_2_sph(query: CallbackQuery, state: FSMContext):
    series_id = query.data.split('_')[-1]
    data = await state.get_data()
    series_name = next((s['name'] for s in data.get('options', {}).get(
        'series', []) if str(s['id']) == series_id), "???")
    await state.update_data(series_id=series_id, series_name=series_name)
    await state.set_state(LensFilterFSM.waiting_for_sph)
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=1)


@dp.message(LensFilterFSM.waiting_for_sph, F.text, ~F.text.startswith('/'))
async def handler_sph_input(message: Message, state: FSMContext):
    try:
        sph_value = Decimal(message.text.replace(',', '.'))
        sph_str = f"{sph_value:.2f}"
    except InvalidOperation:
        await message.answer("❌ Неверный формат. Пожалуйста, введите число (напр. -1.25 или 3.0)")
        return
    await state.update_data(sph=sph_str)
    await state.set_state(LensFilterFSM.waiting_for_cyl)
    try:
        await message.delete()
    except Exception:
        pass
    data = await state.get_data()
    active_message_id = data.get('active_message_id')
    chat_id = data.get('chat_id')
    if active_message_id and chat_id:
        await update_filter_message(message.bot, chat_id, active_message_id, state)
    else:
        new_msg = await message.answer("...")
        await state.update_data(active_message_id=new_msg.message_id, chat_id=new_msg.chat.id)
        await update_filter_message(new_msg.bot, new_msg.chat.id, new_msg.message_id, state)


@dp.message(LensFilterFSM.waiting_for_cyl, F.text, ~F.text.startswith('/'))
async def handler_cyl_input(message: Message, state: FSMContext):
    try:
        cyl_value = Decimal(message.text.replace(',', '.'))
        cyl_str = f"{cyl_value:.2f}"
    except InvalidOperation:
        await message.answer("❌ Неверный формат. Пожалуйста, введите число (напр. -0.75 или 0)")
        return
    await state.update_data(cyl=cyl_str)
    await state.set_state(LensFilterFSM.waiting_for_dia)
    try:
        await message.delete()
    except Exception:
        pass
    data = await state.get_data()
    active_message_id = data.get('active_message_id')
    chat_id = data.get('chat_id')
    if active_message_id and chat_id:
        await update_filter_message(message.bot, chat_id, active_message_id, state, page=1)
    else:
        new_msg = await message.answer("...")
        await state.update_data(active_message_id=new_msg.message_id, chat_id=new_msg.chat.id)
        await update_filter_message(new_msg.bot, new_msg.chat.id, new_msg.message_id, state, page=1)


@dp.callback_query(LensFilterFSM.waiting_for_dia, F.data.startswith("filter_dia_page_"))
async def filter_step_4_paging(query: CallbackQuery, state: FSMContext):
    page = int(query.data.split('_')[-1])
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=page)


@dp.callback_query(LensFilterFSM.waiting_for_dia, F.data.startswith("filter_dia_select_"))
async def filter_final_result(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Ищу линзы по вашим параметрам...")
    dia_value = query.data.split('_')[-1]
    await state.update_data(dia=dia_value)
    data = await state.get_data()
    params = {
        'series': data.get('series_id'),
        'sph': data.get('sph'),
        'cyl': data.get('cyl'),
        'dia': data.get('dia'),
        'stock__gt': 0, 'page': 1,
        'telegram_id': data.get('telegram_id')
    }
    await state.update_data(last_params=params)

    text, keyboard = await show_lens_results(params)

    if keyboard:
        builder = InlineKeyboardBuilder.from_markup(keyboard)
        builder.row(
            InlineKeyboardButton(
                text="🛒 Добавить товар в корзину (по ID)",
                callback_data="add_to_cart_start"
            )
        )
        keyboard = builder.as_markup()

    await query.message.edit_text(text, reply_markup=keyboard)

# --- Логика Пагинации и Поиска ---


async def show_lens_results(params: dict) -> Tuple[str, InlineKeyboardBuilder]:
    response_data = await get_lens_results(params)
    if response_data is None:
        return "❌ Ошибка: не удалось загрузить товары (возможно, доступ деактивирован).", None
    results = response_data.get('results', [])
    count = response_data.get('count', 0)
    if count == 0:
        return "😕 По вашему запросу ничего не найдено.", get_main_menu_keyboard()
    total_pages = math.ceil(count / LENS_PAGE_SIZE)
    current_page = params.get('page', 1)
    text_result = f"✅ Найдено товаров: {count} (Стр. {current_page} из {total_pages})\n\n"
    for lens in results:
        text_result += (
            f"<b>{lens['series']}</b>\n"
            f"  SPH: {lens['sph']}, CYL: {lens['cyl']}, DIA: {lens['dia']}\n"
            f"  Цена: <b>{lens['price']} UZS</b> (Остаток: {lens['stock']} шт.)\n"
            f"  (ID: <code>{html.quote(lens['id_1c'])}</code>)\n"
            "--------------------\n"
        )

    # --- ИСПРАВЛЕНИЕ (v4.2): Возвращаем готовую клавиатуру ---
    keyboard = build_pagination_keyboard(current_page, total_pages)
    return text_result, keyboard.as_markup()
    # ---


@dp.callback_query(F.data.startswith("page_"))
async def handle_pagination(query: CallbackQuery, state: FSMContext):
    page = int(query.data.split('_')[-1])
    data = await state.get_data()
    params = data.get('last_params', {})
    if not params:
        await query.message.edit_text("Ошибка: состояние фильтра потеряно. Начните заново.")
        return
    params['page'] = page
    await query.message.edit_text("Загружаю страницу...")

    text, keyboard = await show_lens_results(params)

    if keyboard:
        builder = InlineKeyboardBuilder.from_markup(keyboard)
        builder.row(
            InlineKeyboardButton(
                text="🛒 Добавить товар в корзину (по ID)",
                callback_data="add_to_cart_start"
            )
        )
        keyboard = builder.as_markup()

    await query.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query(F.data == "start_lens_search")
async def search_step_1(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LensFilterFSM.waiting_for_search_query)
    await state.update_data(
        active_message_id=query.message.message_id,
        chat_id=query.message.chat.id,
        telegram_id=query.from_user.id
    )
    await query.message.edit_text("Введите ID или название Серии для поиска:")


@dp.message(LensFilterFSM.waiting_for_search_query, F.text, ~F.text.startswith('/'))
async def search_final_result(message: Message, state: FSMContext):
    data = await state.get_data()
    active_message_id = data.get('active_message_id')
    chat_id = data.get('chat_id')
    message_to_edit_id = None
    if active_message_id and chat_id:
        try:
            await message.bot.edit_message_text(
                "Ищу...", chat_id=chat_id, message_id=active_message_id
            )
            message_to_edit_id = active_message_id
        except Exception:
            pass
    if not message_to_edit_id:
        new_msg = await message.answer("Ищу...")
        message_to_edit_id = new_msg.message_id
        chat_id = new_msg.chat.id
    try:
        await message.delete()
    except Exception:
        pass
    params = {
        'search': message.text, 'stock__gt': 0, 'page': 1,
        'telegram_id': data.get('telegram_id')
    }
    await state.update_data(
        last_params=params,
        active_message_id=message_to_edit_id,
        chat_id=chat_id
    )
    text, keyboard = await show_lens_results(params)

    if keyboard:
        builder = InlineKeyboardBuilder.from_markup(keyboard)
        builder.row(
            InlineKeyboardButton(
                text="🛒 Добавить товар в корзину (по ID)",
                callback_data="add_to_cart_start"
            )
        )
        keyboard = builder.as_markup()

    await message.bot.edit_message_text(
        text, chat_id=chat_id, message_id=message_to_edit_id, reply_markup=keyboard
    )

# ---
# 5. ЛОГИКА КОРЗИНЫ
# ---


@dp.callback_query(F.data == "add_to_cart_start")
async def add_to_cart_step_1_id(query: CallbackQuery, state: FSMContext):
    await state.set_state(LensFilterFSM.waiting_for_add_id)
    await query.message.answer(
        "<b>Добавление в корзину:</b>\n"
        "Пожалуйста, отправьте ID товара (который можно скопировать из списка выше).",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="add_to_cart_cancel")
        ).as_markup()
    )


@dp.message(LensFilterFSM.waiting_for_add_id, F.text, ~F.text.startswith('/'))
async def add_to_cart_step_2_qty(message: Message, state: FSMContext):
    product_id_1c = message.text.strip()
    await state.update_data(product_id_1c=product_id_1c)
    await state.set_state(LensFilterFSM.waiting_for_add_qty)
    await message.answer(f"Товар (ID: <code>{html.quote(product_id_1c)}</code>). \nСколько штук (напр. '2')?")
    try:
        await message.delete()
    except Exception:
        pass


@dp.message(LensFilterFSM.waiting_for_add_qty, F.text, ~F.text.startswith('/'))
async def add_to_cart_final(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        await message.answer("❌ Неверный формат. Пожалуйста, введите число (напр. 2).")
        return

    await message.answer("Добавляю в корзину...")

    data = await state.get_data()
    product_id_1c = data.get('product_id_1c')
    telegram_id = data.get('telegram_id')

    if not telegram_id:
        telegram_id = message.from_user.id
        await state.update_data(telegram_id=telegram_id)

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=telegram_id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
        auth_token = token.key
    except User.DoesNotExist:
        await message.answer("❌ Ошибка: Ваш пользователь не найден в БД.")
        return

    from catalog.models import Lens
    try:
        # --- ИСПРАВЛЕНИЕ (v4.3 - SynchronousOnlyOperation) ---
        # Мы "пред-загружаем" .series, чтобы Django
        # не делал синхронный запрос в async-функции
        product = await Lens.objects.select_related('series').aget(id_1c=product_id_1c)
        product_db_id = product.pk
        # ---
    except Lens.DoesNotExist:
        await message.answer(f"❌ Ошибка: Товар с ID <code>{html.quote(product_id_1c)}</code> не найден в каталоге.")
        return

    # --- ИСПРАВЛЕНИЕ (v4.2): "lense" -> "lens" ---
    success = await add_to_cart(auth_token, 'lens', product_db_id, quantity)

    if success:
        await message.answer(
            f"✅ <b>{product.series.name} (x{quantity} шт)</b> добавлен в корзину.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            "❌ Ошибка: не удалось добавить товар в корзину.",
            reply_markup=get_main_menu_keyboard()
        )

    try:
        await message.delete()
    except Exception:
        pass
    await state.clear()


# --- Хэндлеры Корзины и Истории ---
async def format_cart_text(cart_data: dict) -> Tuple[str, bool]:
    text = "<b>🛒 Ваша Корзина</b>\n\n"
    items = cart_data.get('items', [])
    if not items:
        text += "<i>(Пусто)</i>"
        return text, True
    for item in items:
        text += f"<b>{item['product']}</b>\n"
        text += f"  Кол-во: {item['quantity']} шт.\n"
        text += f"  Цена: {item['price_at_order']} UZS\n"
        text += f"  <b>Итого: {item['total_price']} UZS</b>\n"
        text += "--------------------\n"
    text += f"\n<b>Общий Итог: {cart_data.get('total_price', 0)} UZS</b>"
    return text, False


@dp.callback_query(F.data == "view_cart")
async def view_cart(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("Загружаю корзину...")

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=query.from_user.id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
    except User.DoesNotExist:
        await query.message.edit_text("❌ Ошибка: Ваш пользователь не найден в БД.")
        return

    cart_data = await get_cart(query.from_user.id, token.key)
    if cart_data is None:
        await query.message.edit_text("❌ Ошибка: не удалось загрузить корзину.")
        return

    text, is_empty = await format_cart_text(cart_data)
    await query.message.edit_text(
        text,
        reply_markup=get_cart_keyboard(cart_is_empty=is_empty)
    )


@dp.callback_query(F.data == "cart_clear")
async def handle_clear_cart(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Очищаю корзину...")

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=query.from_user.id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
    except User.DoesNotExist:
        await query.message.edit_text("❌ Ошибка: Ваш пользователь не найден в БД.")
        return

    success = await clear_cart(token.key)
    if success:
        await query.message.edit_text("Корзина очищена.", reply_markup=get_cart_keyboard(cart_is_empty=True))
    else:
        await query.message.edit_text("❌ Ошибка: не удалось очистить корзину.")


@dp.callback_query(F.data == "cart_checkout")
async def handle_checkout(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Оформляю заказ...")

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=query.from_user.id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
    except User.DoesNotExist:
        await query.message.edit_text("❌ Ошибка: Ваш пользователь не найден в БД.")
        return

    result = await checkout_cart(token.key)
    if result and result.get('order_id'):
        await query.message.edit_text(
            f"✅ <b>Заказ #{result.get('order_id')} успешно оформлен!</b>\n\n"
            "Он отправлен на обработку и выгружен в 1С.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await query.message.edit_text("❌ Ошибка: не удалось оформить заказ (возможно, корзина пуста?).")


@dp.callback_query(F.data == "view_history")
async def view_history(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("Загружаю историю заказов (5 последних)...")

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=query.from_user.id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
    except User.DoesNotExist:
        await query.message.edit_text("❌ Ошибка: Ваш пользователь не найден в БД.")
        return

    history_data = await get_history(token.key, page=1)
    if history_data is None:
        await query.message.edit_text("❌ Ошибка: не удалось загрузить историю.")
        return

    orders = history_data.get('results', [])
    if not orders:
        await query.message.edit_text(
            "😕 У вас пока нет оформленных заказов.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    text = "<b>📜 Ваши последние 5 заказов:</b>\n\n"
    for order in orders:
        text += (
            f"<b>Заказ #{order['id']}</b> (Статус: {order['status']})\n"
            f"  Дата: {order['created_at'].split('T')[0]}\n"
            f"  Сумма: <b>{order['total_price']} UZS</b>\n"
            f"  Товаров: {len(order['items'])}\n"
            "--------------------\n"
        )

    await query.message.edit_text(text, reply_markup=get_main_menu_keyboard())


# ---
# 8. ОБРАБОТЧИКИ ОТМЕНЫ (с "Назад")
# ---
@dp.callback_query(F.data == "filter_cancel")
async def filter_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(
        "Действие отменено. Выберите, что вас интересует:",
        reply_markup=get_main_menu_keyboard()
    )


@dp.callback_query(F.data == "filter_back_to_series")
async def filter_back_to_series(query: CallbackQuery, state: FSMContext):
    await state.set_state(LensFilterFSM.waiting_for_series)
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=1)


@dp.callback_query(F.data == "filter_back_to_sph")
async def filter_back_to_sph(query: CallbackQuery, state: FSMContext):
    await state.set_state(LensFilterFSM.waiting_for_sph)
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=1)


@dp.callback_query(F.data == "add_to_cart_cancel")
async def add_to_cart_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(
        "Добавление в корзину отменено.",
        reply_markup=get_main_menu_keyboard()
    )


@dp.message(Command("cancel"), State("*"))
async def command_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(
            f"Пользователь {message.from_user.id} отменил состояние {current_state}")
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        "Выберите, что вас интересует:",
        reply_markup=get_main_menu_keyboard()
    )

# ---
# 9. ЗАПУСК БОТА
# ---


async def set_main_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск / Перезагрузка"),
        BotCommand(command="cancel", description="Отменить текущее действие")
    ])


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    await set_main_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("--- Запуск бота ---")
    asyncio.run(main())
