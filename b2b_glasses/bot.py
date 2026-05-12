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
from aiogram.client.session.aiohttp import AiohttpSession
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

print("[DEBUG] bot_loader.py (v4.9): Запускаю настройку Django...")
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b2b_glasses.settings')

try:
    django.setup()
    print("[DEBUG] bot_loader.py (v4.9): Настройка Django завершена.")
except Exception as e:
    print(
        f"[DEBUG] bot_loader.py (v4.9): КРИТИЧЕСКАЯ ОШИБКА. Не удалось настроить Django: {e}")
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


# --- 2. FSM СОСТОЯНИЯ ---


class RegistrationFSM(StatesGroup):
    waiting_for_phone = State()
    waiting_for_password = State()


class LensFilterFSM(StatesGroup):
    # ПОРЯДОК: SPH -> CYL -> Сразу результат
    waiting_for_sph = State()
    waiting_for_cyl = State()

    # Эти состояния оставляем на всякий случай, но логически мы их пропускаем
    waiting_for_dia = State()
    waiting_for_material = State()

    waiting_for_search_query = State()

    # Состояния для добавления в корзину
    # waiting_for_add_id - БОЛЬШЕ НЕ ИСПОЛЬЗУЕТСЯ (убрали копирование)
    waiting_for_add_qty = State()


class CustomOrderFSM(StatesGroup):
    waiting_for_design = State()
    waiting_for_photochrom = State()


class CartEditFSM(StatesGroup):
    waiting_for_item_select = State()
    waiting_for_new_qty = State()


# --- 3. НАСТРОЙКИ И API-КЛИЕНТ ---
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
WEBSITE_URL = settings.WEBSITE_URL
PRESCRIPTION_ORDER_URL = settings.PRESCRIPTION_ORDER_URL
LENS_PAGE_SIZE = settings.REST_FRAMEWORK.get('PAGE_SIZE', 5)
MANAGER_USERNAME = settings.MANAGER_USERNAME

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
CUSTOM_ORDER_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/custom/create/"
CART_ITEM_UPDATE_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/cart/items/"
HISTORY_URL = f"{settings.DJANGO_BASE_URL}/api/v1/orders/history/"

logger = logging.getLogger(__name__)
dp = Dispatcher(storage=MemoryStorage())

# ---
# 4. ВСЕ ФУНКЦИИ API
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


async def get_lens_filter_options(telegram_id: int, extra_params: dict = None) -> dict | None:
    params = {"telegram_id": telegram_id}
    if extra_params:
        params.update(extra_params)

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


async def create_custom_order_api(auth_token: str, payload: dict) -> bool:
    headers = {"Authorization": f"Token {auth_token}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(CUSTOM_ORDER_URL, headers=headers, json=payload) as response:
                if response.status == 201:
                    return True
                logger.error(f"Ошибка создания Custom Order: {response.status} - {await response.text()}")
                return False
    except Exception as e:
        logger.error(f"Ошибка create_custom_order_api: {e}")
        return False


async def update_cart_item(auth_token: str, item_id: int, quantity: int) -> bool:
    headers = {"Authorization": f"Token {auth_token}"}
    url = f"{CART_ITEM_UPDATE_URL}{item_id}/update/"
    payload = {"quantity": quantity}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=payload) as response:
                return response.status in [200, 204]
    except Exception as e:
        logger.error(f"Ошибка update_cart_item: {e}")
        return False


async def delete_cart_item(auth_token: str, item_id: int) -> bool:
    headers = {"Authorization": f"Token {auth_token}"}
    url = f"{CART_ITEM_UPDATE_URL}{item_id}/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                return response.status == 204
    except Exception as e:
        logger.error(f"Ошибка delete_cart_item: {e}")
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
# 5. ВСЕ ФУНКЦИИ КЛАВИАТУР
# ---

BUTTONS_PER_PAGE = 8


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Оправы", url=WEBSITE_URL))
    builder.row(InlineKeyboardButton(
        text="Линзы", callback_data="start_lens_filter"))

    builder.row(InlineKeyboardButton(
        text="Рецептурный заказ", url=PRESCRIPTION_ORDER_URL))

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


def build_filter_buttons(items: list, prefix: str, page: int = 1, show_back_button: bool = False, back_callback: str = "filter_cancel") -> InlineKeyboardBuilder:
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

    nav_row = []
    if show_back_button:
        nav_row.append(InlineKeyboardButton(
            text="↩️ Назад", callback_data=back_callback))
    nav_row.append(InlineKeyboardButton(
        text="❌ Отмена", callback_data="filter_cancel"))
    builder.row(*nav_row)
    return builder


def build_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page_") -> InlineKeyboardBuilder:
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

    # Кнопки навигации по страницам
    builder.row(*row)

    # Кнопка отмены
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть", callback_data="filter_cancel"))
    return builder


def get_cart_keyboard(cart_is_empty: bool) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if not cart_is_empty:
        builder.row(InlineKeyboardButton(
            text="✅ Оформить заказ", callback_data="cart_checkout"))
        builder.row(InlineKeyboardButton(
            text="✏️ Управление товарами", callback_data="cart_manage_items"))
        builder.row(InlineKeyboardButton(
            text="🗑 Очистить корзину", callback_data="cart_clear"))
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть", callback_data="filter_cancel"))
    return builder.as_markup()


def get_no_results_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👨‍💻 Написать менеджеру", url=f"https://t.me/{MANAGER_USERNAME}"))

    builder.row(InlineKeyboardButton(
        text="📝 Рецептурный заказ", url=PRESCRIPTION_ORDER_URL))

    builder.row(InlineKeyboardButton(
        text="↩️ В меню", callback_data="filter_cancel"))
    return builder.as_markup()

# ---
# 6. ВСЕ ХЭНДЛЕРЫ БОТА
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

# --- Логика Фильтра ---


async def update_filter_message(bot: Bot, chat_id: int, message_id: int, state: FSMContext, page: int = 1):
    data = await state.get_data()

    text = "<b>--- Фильтр Линз ---</b>\n"
    text += f"1. SPH: {html.quote(data.get('sph', '...'))}\n"
    text += f"2. CYL: {html.quote(data.get('cyl', '...'))}\n"
    text += "--------------------\n"

    current_fsm_state = await state.get_state()
    keyboard_builder = InlineKeyboardBuilder()

    # ШАГ 1: SPH
    if current_fsm_state == LensFilterFSM.waiting_for_sph:
        text += "<b>Шаг 1 из 2: Введите Сферу (SPH)</b>\n\n<i>(Например: <b>-2.5</b>)</i>"
        keyboard_builder.row(
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="filter_cancel")
        )

    # ШАГ 2: CYL
    elif current_fsm_state == LensFilterFSM.waiting_for_cyl:
        text += "<b>Шаг 2 из 2: Введите Цилиндр (CYL)</b>\n\n<i>(Например: <b>-0.75</b> или <b>0</b>)</i>"
        keyboard_builder.row(
            InlineKeyboardButton(
                text="↩️ Назад", callback_data="filter_back_to_sph"),
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="filter_cancel")
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


# 1. Запуск: Загружаем опции, но сразу просим SPH
@dp.callback_query(F.data == "start_lens_filter")
async def filter_start(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("Загружаю опции фильтра...")
    options = await get_lens_filter_options(query.from_user.id)
    if options is None:
        await query.message.edit_text("❌ Ошибка: не удалось загрузить опции фильтра.")
        return
    await state.update_data(
        options=options,
        active_message_id=query.message.message_id,
        chat_id=query.message.chat.id,
        telegram_id=query.from_user.id
    )
    # Сразу идем на SPH
    await state.set_state(LensFilterFSM.waiting_for_sph)
    await update_filter_message(query.bot, query.message.chat.id, query.message.message_id, state, page=1)


# 2. Обработка SPH
@dp.message(LensFilterFSM.waiting_for_sph, F.text, ~F.text.startswith('/'))
async def handler_sph_input(message: Message, state: FSMContext):
    try:
        sph_value = Decimal(message.text.replace(',', '.'))
        sph_str = f"{sph_value:.2f}"
    except InvalidOperation:
        await message.answer("❌ Неверный формат. Пожалуйста, введите число (напр. -1.25 или 3.0)")
        return
    await state.update_data(sph=sph_str)
    # Следующий шаг: CYL
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


# 3. Обработка CYL -> СРАЗУ РЕЗУЛЬТАТ
@dp.message(LensFilterFSM.waiting_for_cyl, F.text, ~F.text.startswith('/'))
async def handler_cyl_input(message: Message, state: FSMContext):
    try:
        cyl_value = Decimal(message.text.replace(',', '.'))
        cyl_str = f"{cyl_value:.2f}"
    except InvalidOperation:
        await message.answer("❌ Неверный формат. Пожалуйста, введите число (напр. -0.75 или 0)")
        return

    # Сохраняем CYL
    await state.update_data(cyl=cyl_str)

    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    active_message_id = data.get('active_message_id')
    chat_id = data.get('chat_id')

    if not active_message_id or not chat_id:
        msg = await message.answer("Ищу линзы...")
        active_message_id = msg.message_id
        chat_id = msg.chat.id
        await state.update_data(active_message_id=active_message_id, chat_id=chat_id)
    else:
        try:
            await message.bot.edit_message_text("Ищу линзы по вашим параметрам...", chat_id=chat_id, message_id=active_message_id)
        except Exception:
            pass

    # Параметры запроса
    params = {
        'sph': data.get('sph'),
        'cyl': cyl_str,
        'stock__gt': 0, 'page': 1,
        'telegram_id': data.get('telegram_id')
    }
    await state.update_data(last_params=params)

    # Вызываем функцию отображения (она теперь возвращает клавиатуру с товарами)
    text, keyboard = await show_lens_results(params)

    await message.bot.edit_message_text(text, chat_id=chat_id, message_id=active_message_id, reply_markup=keyboard)


# --- Логика Пагинации и Поиска (С КНОПКАМИ ТОВАРОВ) ---


async def show_lens_results(params: dict) -> Tuple[str, InlineKeyboardBuilder]:
    response_data = await get_lens_results(params)
    if response_data is None:
        return "❌ Ошибка: не удалось загрузить товары (возможно, доступ деактивирован).", None
    results = response_data.get('results', [])
    count = response_data.get('count', 0)

    if count == 0:
        return (
            "😕 <b>По вашему запросу ничего не найдено.</b>\n\n"
            "Вы можете обратиться к менеджеру для уточнения наличия "
            "или оформить рецептурный заказ на сайте.",
            get_no_results_keyboard()
        )

    total_pages = math.ceil(count / LENS_PAGE_SIZE)
    current_page = params.get('page', 1)

    # Формируем текст
    text_result = f"✅ Найдено товаров: {count} (Стр. {current_page} из {total_pages})\n"
    text_result += "Выберите товар, нажав кнопку ниже:\n\n"

    # Создаем билдер для кнопок товаров
    item_builder = InlineKeyboardBuilder()

    for lens in results:
        # Добавляем описание в текст
        # (ID мы теперь скрываем для чистоты, так как есть кнопка)
        text_result += (
            f"🔹 <b>{lens['series']} (DIA {lens['dia']})</b>\n"
            f"   SPH: {lens['sph']}, CYL: {lens['cyl']}\n"
            f"   Остаток: {lens['stock']} шт.\n"
            "--------------------\n"
        )

        # ДОБАВЛЕНИЕ КНОПКИ ТОВАРА
        # Формат кнопки: "🛒 Серия (Остаток)"
        btn_text = f"🛒 {lens['series']} ({lens['stock']} шт.)"
        # Ограничиваем длину текста кнопки на всякий случай
        if len(btn_text) > 40:
            btn_text = btn_text[:37] + "..."

        # ИСПОЛЬЗУЕМ ВНУТРЕННИЙ ID (lens['id']), чтобы избежать BUTTON_DATA_INVALID
        # id_1c может быть слишком длинным для callback_data (макс 64 байта)
        item_builder.row(InlineKeyboardButton(
            text=btn_text,
            callback_data=f"add_item_{lens['id']}"
        ))

    # Добавляем кнопки пагинации к кнопкам товаров
    pagination_keyboard = build_pagination_keyboard(current_page, total_pages)

    # Объединяем кнопки товаров и навигации
    # Метод attach добавляет кнопки из другого билдера
    item_builder.attach(pagination_keyboard)

    return text_result, item_builder.as_markup()


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

    await message.bot.edit_message_text(
        text, chat_id=chat_id, message_id=message_to_edit_id, reply_markup=keyboard
    )

# ---
# 7. ЛОГИКА КАСТОМНОГО ЗАКАЗА
# ---
# (Код оставлен для совместимости, хотя вызов в меню заменен на ссылку)


@dp.callback_query(F.data == "custom_order_start")
async def custom_order_step_1_design(query: CallbackQuery, state: FSMContext):
    await state.set_state(CustomOrderFSM.waiting_for_design)
    await query.message.edit_text(
        "<b>Оформление специального заказа (Шаг 1 из 2)</b>\n\n"
        "Пожалуйста, введите желаемый <b>Дизайн</b> линзы:",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="filter_cancel")
        ).as_markup()
    )


@dp.message(CustomOrderFSM.waiting_for_design, F.text)
async def custom_order_step_2_photochrom(message: Message, state: FSMContext):
    await state.update_data(custom_design=message.text)
    await state.set_state(CustomOrderFSM.waiting_for_photochrom)
    await message.answer(
        "<b>Оформление специального заказа (Шаг 2 из 2)</b>\n\n"
        "Пожалуйста, укажите параметры <b>Фотохрома</b>:",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="filter_cancel")
        ).as_markup()
    )


@dp.message(CustomOrderFSM.waiting_for_photochrom, F.text)
async def custom_order_finish(message: Message, state: FSMContext):
    await state.update_data(custom_photochrom=message.text)
    data = await state.get_data()

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=message.from_user.id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
    except User.DoesNotExist:
        await message.answer("❌ Ошибка: Пользователь не найден.")
        return

    payload = {
        "series": data.get("series_name", "Unknown"),
        "sph": data.get("sph", "0"),
        "cyl": data.get("cyl", "0"),
        "dia": data.get("dia", "Unknown"),
        "design": data.get("custom_design"),
        "photochrom": message.text
    }

    await message.answer("⏳ Отправляю заявку...")

    success = await create_custom_order_api(token.key, payload)

    if success:
        await message.answer(
            "✅ <b>Заявка принята!</b>\n\n"
            "Ваш индивидуальный заказ сохранен в системе. Менеджер увидит его и свяжется с вами.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при сохранении заявки. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )

    await state.clear()


# ---
# 8. ЛОГИКА КОРЗИНЫ (ОБНОВЛЕННАЯ: ВЫБОР ЧЕРЕЗ КНОПКИ)
# ---


# НОВЫЙ ХЕНДЛЕР: Обработка нажатия на кнопку товара (вместо ввода ID)
@dp.callback_query(F.data.startswith("add_item_"))
async def process_select_item_from_list(query: CallbackQuery, state: FSMContext):
    # Теперь здесь приходит внутренний ID (pk), а не id_1c
    product_pk = query.data.split("add_item_")[-1]
    await state.update_data(product_pk=product_pk)

    # Показываем выбор количества (1, 2, вручную)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="👁 1 шт. (На один глаз)", callback_data="qty_set_1"))
    builder.row(InlineKeyboardButton(
        text="👓 2 шт. (1 Пара)", callback_data="qty_set_2"))
    builder.row(InlineKeyboardButton(
        text="🔢 Ввести число вручную", callback_data="qty_manual"))
    builder.row(InlineKeyboardButton(text="❌ Отмена",
                callback_data="add_to_cart_cancel"))

    await query.message.answer(
        f"Выбран товар.\n"
        "Выберите количество для добавления в корзину:",
        reply_markup=builder.as_markup()
    )


# Этот хендлер больше не используется напрямую из меню, но оставляем на всякий случай
@dp.callback_query(F.data == "add_to_cart_start")
async def add_to_cart_step_1_id_legacy(query: CallbackQuery, state: FSMContext):
    await query.answer("Пожалуйста, выберите товар, нажав кнопку в списке выше.", show_alert=True)


@dp.callback_query(F.data.startswith("qty_set_"))
async def process_qty_button(query: CallbackQuery, state: FSMContext):
    qty = int(query.data.split('_')[-1])
    await process_add_to_cart_logic(query.message, state, qty, query.from_user.id)


@dp.callback_query(F.data == "qty_manual")
async def process_qty_manual_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(LensFilterFSM.waiting_for_add_qty)
    await query.message.edit_text("Введите количество (число):")


@dp.message(LensFilterFSM.waiting_for_add_qty, F.text, ~F.text.startswith('/'))
async def process_qty_manual_input(message: Message, state: FSMContext):
    try:
        qty = int(message.text)
        if qty <= 0:
            raise ValueError
    except (ValueError, TypeError):
        await message.answer("❌ Неверный формат. Введите число (напр. 4).")
        return
    await process_add_to_cart_logic(message, state, qty, message.from_user.id)


async def process_add_to_cart_logic(message: Message, state: FSMContext, quantity: int, telegram_id: int):
    if isinstance(message, Message):
        await message.answer(f"Добавляю в корзину ({quantity} шт)...")

    data = await state.get_data()
    # Теперь мы ожидаем product_pk (внутренний ID)
    product_pk = data.get('product_pk')

    from users.models import User
    from rest_framework.authtoken.models import Token
    try:
        user = await User.objects.aget(telegram_id=telegram_id, is_active=True)
        token, _ = await Token.objects.aget_or_create(user=user)
        auth_token = token.key
    except User.DoesNotExist:
        if isinstance(message, Message):
            await message.answer("❌ Ошибка: Ваш пользователь не найден в БД.")
        return

    from catalog.models import Lens
    try:
        if product_pk:
            # Ищем по PK (внутреннему ID)
            product = await Lens.objects.select_related('series').aget(pk=product_pk)
        else:
            # Fallback для старой логики, если вдруг остались старые данные
            product_id_1c = data.get('product_id_1c')
            if product_id_1c:
                product = await Lens.objects.select_related('series').aget(id_1c=product_id_1c)
            else:
                raise Lens.DoesNotExist

        product_db_id = product.pk
    except Lens.DoesNotExist:
        msg = "❌ Ошибка: Товар не найден."
        if isinstance(message, Message):
            await message.answer(msg)
        return

    success = await add_to_cart(auth_token, 'lens', product_db_id, quantity)

    if success:
        qty_text = f"{quantity} шт."
        if quantity % 2 == 0:
            pairs = quantity // 2
            qty_text += f" ({pairs} пара(ы))"

        text = f"✅ <b>{product.series.name}</b> добавлен в корзину.\nКол-во: {qty_text}"

        if isinstance(message, Message):
            await message.answer(text, reply_markup=get_main_menu_keyboard())
    else:
        if isinstance(message, Message):
            await message.answer(
                "❌ Ошибка: не удалось добавить товар в корзину.",
                reply_markup=get_main_menu_keyboard()
            )

    try:
        if isinstance(message, Message):
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

    for idx, item in enumerate(items, 1):
        qty = item['quantity']
        if qty % 2 == 0:
            pairs = qty // 2
            qty_display = f"{qty} шт. ({pairs} пара(ы))"
        else:
            qty_display = f"{qty} шт."

        text += f"<b>{idx}. {item['product']}</b>\n"
        text += f"  Кол-во: {qty_display}\n"
        text += "--------------------\n"
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

    await state.update_data(auth_token=token.key)

    cart_data = await get_cart(query.from_user.id, token.key)
    if cart_data is None:
        await query.message.edit_text("❌ Ошибка: не удалось загрузить корзину.")
        return

    await state.update_data(cart_items=cart_data.get('items', []))

    text, is_empty = await format_cart_text(cart_data)
    await query.message.edit_text(
        text,
        reply_markup=get_cart_keyboard(cart_is_empty=is_empty)
    )


@dp.callback_query(F.data == "cart_manage_items")
async def cart_manage_list(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('cart_items', [])

    if not items:
        await query.answer("Корзина пуста!")
        return

    builder = InlineKeyboardBuilder()
    for item in items:
        item_id = item.get('id')
        item_name = item.get('product')[:20]
        builder.row(InlineKeyboardButton(
            text=f"{item_name} ({item['quantity']} шт.)",
            callback_data=f"cart_edit_{item_id}"
        ))

    builder.row(InlineKeyboardButton(
        text="↩️ Назад в корзину", callback_data="view_cart"))

    await query.message.edit_text("Выберите товар для изменения:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("cart_edit_"))
async def cart_item_options(query: CallbackQuery, state: FSMContext):
    item_id = query.data.split('_')[-1]
    await state.update_data(selected_cart_item_id=item_id)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔢 Изменить количество", callback_data="cart_act_qty"))
    builder.row(InlineKeyboardButton(
        text="🗑 Удалить позицию", callback_data="cart_act_del"))
    builder.row(InlineKeyboardButton(text="↩️ Назад к списку",
                callback_data="cart_manage_items"))

    await query.message.edit_text(f"Что сделать с товаром (ID записи: {item_id})?", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "cart_act_del")
async def cart_item_delete_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_id = data.get('selected_cart_item_id')
    token = data.get('auth_token')

    if await delete_cart_item(token, item_id):
        await query.answer("Товар удален!", show_alert=True)
        await view_cart(query, state)
    else:
        await query.answer("Ошибка при удалении. Попробуйте позже.", show_alert=True)


@dp.callback_query(F.data == "cart_act_qty")
async def cart_item_qty_input(query: CallbackQuery, state: FSMContext):
    await state.set_state(CartEditFSM.waiting_for_new_qty)
    await query.message.edit_text(
        "Введите новое количество товара (число):",
        reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(text="❌ Отмена", callback_data="view_cart")
        ).as_markup()
    )


@dp.message(CartEditFSM.waiting_for_new_qty, F.text)
async def cart_item_qty_save(message: Message, state: FSMContext):
    try:
        qty = int(message.text)
        if qty <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное число > 0")
        return

    data = await state.get_data()
    item_id = data.get('selected_cart_item_id')
    token = data.get('auth_token')

    await message.answer("Обновляю количество...")

    if await update_cart_item(token, item_id, qty):
        await message.answer("✅ Количество обновлено!")
        cart_data = await get_cart(message.from_user.id, token)
        text, is_empty = await format_cart_text(cart_data)
        await message.answer(text, reply_markup=get_cart_keyboard(is_empty))
        await state.clear()
    else:
        await message.answer("❌ Ошибка обновления. Возможно, нет связи с сервером.", reply_markup=get_main_menu_keyboard())
        await state.clear()


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
            "Он отправлен на обработку.",
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
            f"  Товаров: {len(order['items'])}\n"
            "--------------------\n"
        )

    await query.message.edit_text(text, reply_markup=get_main_menu_keyboard())


# ---
# 9. ОБРАБОТЧИКИ ОТМЕНЫ
# ---
@dp.callback_query(F.data == "filter_cancel")
async def filter_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(
        "Действие отменено. Выберите, что вас интересует:",
        reply_markup=get_main_menu_keyboard()
    )


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
# 10. ЗАПУСК БОТА
# ---


async def set_main_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск / Перезагрузка"),
        BotCommand(command="cancel", description="Отменить текущее действие")
    ])


async def main() -> None:
    # Отключаем проверку SSL для работы в корпоративных сетях / через прокси
    session = AiohttpSession()
    bot = Bot(
        token=BOT_TOKEN, 
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await set_main_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("--- Запуск бота ---")
    asyncio.run(main())
