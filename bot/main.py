<<<<<<< HEAD
import os
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from bson import ObjectId
import httpx
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "OGW")
ADMINS_COLLECTION = "admins"
ORDERS_COLLECTION = "orders"
USERS_COLLECTION = "users"

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Состояния для FSM
class AdminActions(StatesGroup):
    ADD_ADMIN = State()
    REMOVE_ADMIN = State()

async def ensure_superadmin_exists():
    """Проверяет и добавляет супер-админа из .env при старте"""
    superadmin_id = int(os.getenv("SUPERADMIN_ID", 0))
    if not superadmin_id:
        print("⚠️ SUPERADMIN_ID не указан в .env")
        return

    existing_admin = await db[ADMINS_COLLECTION].find_one({"user_id": superadmin_id})
    if not existing_admin:
        await db[ADMINS_COLLECTION].insert_one({
            "user_id": superadmin_id,
            "is_superadmin": True,
            "added_at": datetime.now(),
            "username": "superadmin"
        })
        print(f"✅ Супер-админ {superadmin_id} добавлен в базу")

async def get_admin_username(user_id: int) -> str:
    """Получаем username администратора"""
    try:
        admin = await db[ADMINS_COLLECTION].find_one({"user_id": user_id})
        return admin.get("username", f"ID{user_id}")
    except Exception:
        return f"ID{user_id}"
    
async def notify_admins_about_order(order_data: dict):
    """Отправляет уведомление всем администраторам о новом заказе"""
    admins = await db[ADMINS_COLLECTION].find().to_list(None)
    
    for admin in admins:
        try:
            # Формируем сообщение с информацией о заказе
            message = (
                "🛒 *Новый заказ!*\n\n"
                f"🔹 *Номер заказа:* `{order_data['_id']}`\n"
                f"🔹 *Клиент:* {order_data['customer']['first_name']} {order_data['customer']['last_name']}\n"
                f"🔹 *Телефон:* `{order_data['customer']['phone']}`\n"
                f"🔹 *Сумма:* {order_data['total']} ₽\n"
                f"🔹 *Способ оплаты:* {order_data['payment_method']}\n"
                f"🔹 *Доставка:* {order_data['delivery_method']}\n"
            )
            
            # Добавляем информацию о пользователе Telegram, если есть
            if order_data.get('user_info'):
                user_info = order_data['user_info']
                message += (
                    f"\n*Информация о клиенте Telegram:*\n"
                    f"ID: {user_info.get('telegram_id', 'не указан')}\n"
                    f"Username: @{user_info.get('username', 'не указан')}\n"
                    f"Имя: {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
                )
            
            message += "\n*Товары:*\n"
            
            for item in order_data['items']:
                message += f"- {item['product_name']} × {item['quantity']} = {item['price'] * item['quantity']} ₽\n"
                
            await bot.send_message(
                chat_id=admin['user_id'],
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить уведомление админу {admin['user_id']}: {e}")
            

async def notify_all_admins(message: str, parse_mode: str = "HTML"):
    """Отправляет сообщение всем администраторам"""
    admins = await db[ADMINS_COLLECTION].find().to_list(None)
    print(admins)
    for admin in admins:
        print(admin['user_id'])
        try:
            await bot.send_message(
                chat_id=admin['user_id'],
                text=message,
                parse_mode=parse_mode
            )
        except Exception as e:
            print(f"Не удалось уведомить администратора {admin['user_id']}: {e}")

async def update_order_status(order_id: str, status: str, confirmed_by: int):
    """Обновляет статус заказа в базе данных"""
    try:
        result = await db[ORDERS_COLLECTION].update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "status": status,
                "confirmed_by": confirmed_by,
                "confirmed_at": datetime.now(),
                "updated_at": datetime.now()
            }}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Ошибка при обновлении статуса заказа: {e}")
        return False

@dp.callback_query(F.data.startswith("view_order_"))
async def view_order_details(callback: types.CallbackQuery):
    """Показывает детали заказа"""
    order_id = callback.data.split("_")[-1]
    
    try:
        order = await db[ORDERS_COLLECTION].find_one({"_id": ObjectId(order_id)})
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        message = (
            f"📋 *Детали заказа #{order_id}*\n\n"
            f"*Статус:* {order.get('status', 'Новый')}\n"
        )
        
        if order.get('status') == "Подтвержден":
            confirmed_by = await get_admin_username(order['confirmed_by'])
            confirmed_at = order['confirmed_at'].strftime("%d.%m.%Y %H:%M")
            message += f"*Подтвержден:* {confirmed_by} ({confirmed_at})\n\n"
        
        await callback.message.edit_text(
            text=message,
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer("Ошибка при загрузке заказа", show_alert=True)
        print(f"Ошибка при просмотре заказа: {e}")

@dp.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: types.CallbackQuery):
    """Обработка подтверждения заказа администратором"""
    order_id = callback.data.split("_")[-1]
    admin_id = callback.from_user.id
    
    try:
        # Проверяем текущий статус заказа
        order = await db[ORDERS_COLLECTION].find_one({"_id": ObjectId(order_id)})
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        if order.get('status') == "Подтвержден":
            confirmed_by = await get_admin_username(order['confirmed_by'])
            await callback.answer(
                f"Этот заказ уже имеет статус 'ПОДТВЕРЖДЕН'\nАдминистратором {confirmed_by}",
                show_alert=True
            )
            return
        
        # Обновляем статус заказа
        success = await update_order_status(order_id, "Подтвержден", admin_id)
        if not success:
            await callback.answer("Ошибка при подтверждении заказа", show_alert=True)
            return
        
        # Уведомляем администраторов
        admin_name = await get_admin_username(admin_id)
        await notify_all_admins(
            f"✅ *Заказ подтверждён*\n\n"
            f"🔹 *Номер заказа:* `{order_id}`\n"
            f"🔹 *Подтвердил:* {admin_name}\n"
            f"🔹 *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"*Статус:* Подтвержден",
            parse_mode="Markdown"
        )
        
        await callback.answer("Заказ успешно подтвержден!", show_alert=True)
    except Exception as e:
        await callback.answer("Ошибка при подтверждении заказа", show_alert=True)
        print(f"Ошибка при подтверждении заказа: {e}")

async def watch_orders():
    """Функция для отслеживания новых заказов"""
    last_order_id = None
    
    while True:
        try:
            # Ищем самый свежий заказ
            latest_order = await db[ORDERS_COLLECTION].find_one(
                {},
                sort=[('created_at', -1)]
            )
            print(latest_order.get('status'))
            if latest_order and latest_order['_id'] != last_order_id:
                last_order_id = latest_order['_id']
                # Убедимся, что это действительно новый заказ (статус "Новый")
                if latest_order.get('status') == "new":
                    print(latest_order.get('status'))
                    await notify_admins_about_order(latest_order)
                
        except Exception as e:
            print(f"Ошибка при проверке заказов: {e}")
        
        await asyncio.sleep(10)  # Проверяем каждые 10 секунд

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка команды /start"""
    user_permissions = await check_user_permissions(message.from_user.id)
    
    builder = InlineKeyboardBuilder()
    
    if user_permissions["is_admin"]:
        builder.row(
            types.InlineKeyboardButton(
                text="🛍️ Магазин",
                web_app=WebAppInfo(url="https://9b6aaa759924.ngrok-free.app/frontend")
            )
        )
        builder.row(
            types.InlineKeyboardButton(
                text="🛍️Админ-панель",
                web_app=WebAppInfo(url="https://9b6aaa759924.ngrok-free.app/frontend/admin_panel.html")
            )
        )
        
        builder.row(
            types.InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="stats"
            )
        )
        
        if user_permissions["is_superadmin"]:
            builder.row(
                types.InlineKeyboardButton(
                    text="⚙️ Управление администраторами",
                    callback_data="admin_menu"
                )
            )
        
        await message.answer(
            "👨‍💻 Панель администратора",
            reply_markup=builder.as_markup()
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text="🛍️ Открыть магазин",
                web_app=WebAppInfo(url="https://9b6aaa759924.ngrok-free.app/frontend")
            )
        )
        
        await message.answer(
            "Добро пожаловать в наш магазин!",
            reply_markup=builder.as_markup()
        )

async def check_user_permissions(user_id: int) -> dict:
    """Проверяет права пользователя"""
    admin_data = await db[ADMINS_COLLECTION].find_one({"user_id": user_id})
    if admin_data:
        return {
            "is_admin": True,
            "is_superadmin": admin_data.get("is_superadmin", False)
        }
    return {"is_admin": False, "is_superadmin": False}

@dp.callback_query(F.data == "admin_menu")
async def admin_management(callback: types.CallbackQuery, state: FSMContext):
    """Меню управления администраторами"""
    user_permissions = await check_user_permissions(callback.from_user.id)
    if not user_permissions["is_superadmin"]:
        await callback.answer("❌ У вас нет прав для этой команды", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin")],
        [InlineKeyboardButton(text="➖ Удалить администратора", callback_data="remove_admin")],
        [InlineKeyboardButton(text="📋 Список администраторов", callback_data="list_admins")]
    ])
    await callback.message.edit_text("⚙️ Управление администраторами:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "add_admin")
async def add_admin_start(callback: types.CallbackQuery, state: FSMContext):
    """Запрос ID нового администратора"""
    await callback.message.answer("Введите Telegram ID пользователя, которого хотите сделать администратором:")
    await state.set_state(AdminActions.ADD_ADMIN)
    await callback.answer()

@dp.message(AdminActions.ADD_ADMIN)
async def add_admin_finish(message: types.Message, state: FSMContext):
    """Добавление нового администратора"""
    try:
        new_admin_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный формат ID. Введите числовой Telegram ID.")
        return

    if await db[ADMINS_COLLECTION].find_one({"user_id": new_admin_id}):
        await message.answer("⚠️ Этот пользователь уже является администратором.")
        await state.clear()
        return

    await db[ADMINS_COLLECTION].insert_one({
        "user_id": new_admin_id,
        "is_superadmin": False,
        "added_by": message.from_user.id,
        "added_at": datetime.now(),
        "username": message.from_user.username or f"ID{new_admin_id}"
    })

    # Уведомление нового администратора
    try:
        await bot.send_message(
            chat_id=new_admin_id,
            text="🎉 Вас назначили администратором бота!\nТеперь вы будете получать уведомления о новых заказах."
        )
    except Exception as e:
        print(f"❌ Не удалось уведомить нового администратора: {e}")

    # Уведомление супер-админов
    admin_name = await get_admin_username(message.from_user.id)
    await notify_all_admins(
        f"🛠 Администратор <b>{admin_name}</b> добавил нового администратора: ID {new_admin_id}"
    )

    await message.answer(f"✅ Пользователь {new_admin_id} успешно добавлен как администратор!")
    await state.clear()

@dp.callback_query(F.data == "remove_admin")
async def remove_admin_start(callback: types.CallbackQuery, state: FSMContext):
    """Запрос ID администратора для удаления"""
    admins = await db[ADMINS_COLLECTION].find({"is_superadmin": False}).to_list(None)
    if not admins:
        await callback.message.answer("❌ Нет администраторов для удаления.")
        await callback.answer()
        return

    keyboard = InlineKeyboardBuilder()
    for admin in admins:
        keyboard.row(InlineKeyboardButton(
            text=f"ID {admin['user_id']} ({admin.get('username', '')})",
            callback_data=f"remove_admin_{admin['user_id']}"
        ))

    await callback.message.edit_text(
        "Выберите администратора для удаления:",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("remove_admin_"))
async def remove_admin_finish(callback: types.CallbackQuery):
    """Удаление администратора"""
    admin_id = int(callback.data.split("_")[-1])
    if admin_id == int(os.getenv("SUPERADMIN_ID")):
        await callback.answer("❌ Нельзя удалить супер-админа!", show_alert=True)
        return

    result = await db[ADMINS_COLLECTION].delete_one({"user_id": admin_id})
    if result.deleted_count > 0:
        # Уведомление удаленного администратора
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="ℹ️ Ваши права администратора были отозваны."
            )
        except Exception as e:
            print(f"❌ Не удалось уведомить удаленного администратора: {e}")

        # Уведомление супер-админов
        admin_name = await get_admin_username(callback.from_user.id)
        removed_admin = await get_admin_username(admin_id)
        await notify_all_admins(
            f"🛠 Администратор <b>{admin_name}</b> удалил администратора: {removed_admin} (ID {admin_id})"
        )

        await callback.message.edit_text(f"✅ Администратор ID {admin_id} удалён.")
    else:
        await callback.message.edit_text("❌ Администратор не найден.")
    await callback.answer()

@dp.callback_query(F.data == "list_admins")
async def list_admins(callback: types.CallbackQuery):
    """Показать список администраторов"""
    admins = await db[ADMINS_COLLECTION].find().sort("is_superadmin", -1).to_list(None)
    if not admins:
        await callback.message.answer("❌ Нет администраторов в базе.")
        await callback.answer()
        return

    message = ["👥 <b>Список администраторов:</b>\n"]
    for admin in admins:
        status = " (супер-админ)" if admin.get("is_superadmin") else ""
        added_at = admin.get("added_at", datetime.now()).strftime("%d.%m.%Y")
        username = admin.get("username", "")
        message.append(f"• <code>{admin['user_id']}</code> {username}{status} - добавлен {added_at}")

    await callback.message.answer("\n".join(message), parse_mode="HTML")
    await callback.answer()

async def on_startup():
    """Действия при запуске бота"""
    # Создаем индексы
    await db[ADMINS_COLLECTION].create_index([("user_id", 1)], unique=True)
    await db[ORDERS_COLLECTION].create_index([("status", 1)])
    await db[ORDERS_COLLECTION].create_index([("created_at", -1)])
    
    # Добавляем супер-админа из .env
    await ensure_superadmin_exists()
    
    # Уведомляем администраторов о запуске
    await notify_all_admins("🤖 Бот для уведомлений о заказах запущен и готов к работе!")
    
    # Запускаем отслеживание заказов
    asyncio.create_task(watch_orders())

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
=======
import os
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from bson import ObjectId
import httpx
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "OGW")
ADMINS_COLLECTION = "admins"
ORDERS_COLLECTION = "orders"
USERS_COLLECTION = "users"

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Состояния для FSM
class AdminActions(StatesGroup):
    ADD_ADMIN = State()
    REMOVE_ADMIN = State()

async def ensure_superadmin_exists():
    """Проверяет и добавляет супер-админа из .env при старте"""
    superadmin_id = int(os.getenv("SUPERADMIN_ID", 0))
    if not superadmin_id:
        print("⚠️ SUPERADMIN_ID не указан в .env")
        return

    existing_admin = await db[ADMINS_COLLECTION].find_one({"user_id": superadmin_id})
    if not existing_admin:
        await db[ADMINS_COLLECTION].insert_one({
            "user_id": superadmin_id,
            "is_superadmin": True,
            "added_at": datetime.now(),
            "username": "superadmin"
        })
        print(f"✅ Супер-админ {superadmin_id} добавлен в базу")

async def get_admin_username(user_id: int) -> str:
    """Получаем username администратора"""
    try:
        admin = await db[ADMINS_COLLECTION].find_one({"user_id": user_id})
        return admin.get("username", f"ID{user_id}")
    except Exception:
        return f"ID{user_id}"
    
async def notify_admins_about_order(order_data: dict):
    """Отправляет уведомление всем администраторам о новом заказе"""
    admins = await db[ADMINS_COLLECTION].find().to_list(None)
    
    for admin in admins:
        try:
            # Формируем сообщение с информацией о заказе
            message = (
                "🛒 *Новый заказ!*\n\n"
                f"🔹 *Номер заказа:* `{order_data['_id']}`\n"
                f"🔹 *Клиент:* {order_data['customer']['first_name']} {order_data['customer']['last_name']}\n"
                f"🔹 *Телефон:* `{order_data['customer']['phone']}`\n"
                f"🔹 *Сумма:* {order_data['total']} ₽\n"
                f"🔹 *Способ оплаты:* {order_data['payment_method']}\n"
                f"🔹 *Доставка:* {order_data['delivery_method']}\n"
            )
            
            # Добавляем информацию о пользователе Telegram, если есть
            if order_data.get('user_info'):
                user_info = order_data['user_info']
                message += (
                    f"\n*Информация о клиенте Telegram:*\n"
                    f"ID: {user_info.get('telegram_id', 'не указан')}\n"
                    f"Username: @{user_info.get('username', 'не указан')}\n"
                    f"Имя: {user_info.get('first_name', '')} {user_info.get('last_name', '')}\n"
                )
            
            message += "\n*Товары:*\n"
            
            for item in order_data['items']:
                message += f"- {item['product_name']} × {item['quantity']} = {item['price'] * item['quantity']} ₽\n"
                
            await bot.send_message(
                chat_id=admin['user_id'],
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить уведомление админу {admin['user_id']}: {e}")
            

async def notify_all_admins(message: str, parse_mode: str = "HTML"):
    """Отправляет сообщение всем администраторам"""
    admins = await db[ADMINS_COLLECTION].find().to_list(None)
    print(admins)
    for admin in admins:
        print(admin['user_id'])
        try:
            await bot.send_message(
                chat_id=admin['user_id'],
                text=message,
                parse_mode=parse_mode
            )
        except Exception as e:
            print(f"Не удалось уведомить администратора {admin['user_id']}: {e}")

async def update_order_status(order_id: str, status: str, confirmed_by: int):
    """Обновляет статус заказа в базе данных"""
    try:
        result = await db[ORDERS_COLLECTION].update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "status": status,
                "confirmed_by": confirmed_by,
                "confirmed_at": datetime.now(),
                "updated_at": datetime.now()
            }}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Ошибка при обновлении статуса заказа: {e}")
        return False

@dp.callback_query(F.data.startswith("view_order_"))
async def view_order_details(callback: types.CallbackQuery):
    """Показывает детали заказа"""
    order_id = callback.data.split("_")[-1]
    
    try:
        order = await db[ORDERS_COLLECTION].find_one({"_id": ObjectId(order_id)})
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        message = (
            f"📋 *Детали заказа #{order_id}*\n\n"
            f"*Статус:* {order.get('status', 'Новый')}\n"
        )
        
        if order.get('status') == "Подтвержден":
            confirmed_by = await get_admin_username(order['confirmed_by'])
            confirmed_at = order['confirmed_at'].strftime("%d.%m.%Y %H:%M")
            message += f"*Подтвержден:* {confirmed_by} ({confirmed_at})\n\n"
        
        await callback.message.edit_text(
            text=message,
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer("Ошибка при загрузке заказа", show_alert=True)
        print(f"Ошибка при просмотре заказа: {e}")

@dp.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: types.CallbackQuery):
    """Обработка подтверждения заказа администратором"""
    order_id = callback.data.split("_")[-1]
    admin_id = callback.from_user.id
    
    try:
        # Проверяем текущий статус заказа
        order = await db[ORDERS_COLLECTION].find_one({"_id": ObjectId(order_id)})
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        
        if order.get('status') == "Подтвержден":
            confirmed_by = await get_admin_username(order['confirmed_by'])
            await callback.answer(
                f"Этот заказ уже имеет статус 'ПОДТВЕРЖДЕН'\nАдминистратором {confirmed_by}",
                show_alert=True
            )
            return
        
        # Обновляем статус заказа
        success = await update_order_status(order_id, "Подтвержден", admin_id)
        if not success:
            await callback.answer("Ошибка при подтверждении заказа", show_alert=True)
            return
        
        # Уведомляем администраторов
        admin_name = await get_admin_username(admin_id)
        await notify_all_admins(
            f"✅ *Заказ подтверждён*\n\n"
            f"🔹 *Номер заказа:* `{order_id}`\n"
            f"🔹 *Подтвердил:* {admin_name}\n"
            f"🔹 *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"*Статус:* Подтвержден",
            parse_mode="Markdown"
        )
        
        await callback.answer("Заказ успешно подтвержден!", show_alert=True)
    except Exception as e:
        await callback.answer("Ошибка при подтверждении заказа", show_alert=True)
        print(f"Ошибка при подтверждении заказа: {e}")

async def watch_orders():
    """Функция для отслеживания новых заказов"""
    last_order_id = None
    
    while True:
        try:
            # Ищем самый свежий заказ
            latest_order = await db[ORDERS_COLLECTION].find_one(
                {},
                sort=[('created_at', -1)]
            )
            print(latest_order.get('status'))
            if latest_order and latest_order['_id'] != last_order_id:
                last_order_id = latest_order['_id']
                # Убедимся, что это действительно новый заказ (статус "Новый")
                if latest_order.get('status') == "new":
                    print(latest_order.get('status'))
                    await notify_admins_about_order(latest_order)
                
        except Exception as e:
            print(f"Ошибка при проверке заказов: {e}")
        
        await asyncio.sleep(10)  # Проверяем каждые 10 секунд

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка команды /start"""
    user_permissions = await check_user_permissions(message.from_user.id)
    
    builder = InlineKeyboardBuilder()
    
    if user_permissions["is_admin"]:
        builder.row(
            types.InlineKeyboardButton(
                text="🛍️ Магазин",
                web_app=WebAppInfo(url="https://9b6aaa759924.ngrok-free.app/frontend")
            )
        )
        builder.row(
            types.InlineKeyboardButton(
                text="🛍️Админ-панель",
                web_app=WebAppInfo(url="https://9b6aaa759924.ngrok-free.app/frontend/admin_panel.html")
            )
        )
        
        builder.row(
            types.InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="stats"
            )
        )
        
        if user_permissions["is_superadmin"]:
            builder.row(
                types.InlineKeyboardButton(
                    text="⚙️ Управление администраторами",
                    callback_data="admin_menu"
                )
            )
        
        await message.answer(
            "👨‍💻 Панель администратора",
            reply_markup=builder.as_markup()
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text="🛍️ Открыть магазин",
                web_app=WebAppInfo(url="https://9b6aaa759924.ngrok-free.app/frontend")
            )
        )
        
        await message.answer(
            "Добро пожаловать в наш магазин!",
            reply_markup=builder.as_markup()
        )

async def check_user_permissions(user_id: int) -> dict:
    """Проверяет права пользователя"""
    admin_data = await db[ADMINS_COLLECTION].find_one({"user_id": user_id})
    if admin_data:
        return {
            "is_admin": True,
            "is_superadmin": admin_data.get("is_superadmin", False)
        }
    return {"is_admin": False, "is_superadmin": False}

@dp.callback_query(F.data == "admin_menu")
async def admin_management(callback: types.CallbackQuery, state: FSMContext):
    """Меню управления администраторами"""
    user_permissions = await check_user_permissions(callback.from_user.id)
    if not user_permissions["is_superadmin"]:
        await callback.answer("❌ У вас нет прав для этой команды", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin")],
        [InlineKeyboardButton(text="➖ Удалить администратора", callback_data="remove_admin")],
        [InlineKeyboardButton(text="📋 Список администраторов", callback_data="list_admins")]
    ])
    await callback.message.edit_text("⚙️ Управление администраторами:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "add_admin")
async def add_admin_start(callback: types.CallbackQuery, state: FSMContext):
    """Запрос ID нового администратора"""
    await callback.message.answer("Введите Telegram ID пользователя, которого хотите сделать администратором:")
    await state.set_state(AdminActions.ADD_ADMIN)
    await callback.answer()

@dp.message(AdminActions.ADD_ADMIN)
async def add_admin_finish(message: types.Message, state: FSMContext):
    """Добавление нового администратора"""
    try:
        new_admin_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный формат ID. Введите числовой Telegram ID.")
        return

    if await db[ADMINS_COLLECTION].find_one({"user_id": new_admin_id}):
        await message.answer("⚠️ Этот пользователь уже является администратором.")
        await state.clear()
        return

    await db[ADMINS_COLLECTION].insert_one({
        "user_id": new_admin_id,
        "is_superadmin": False,
        "added_by": message.from_user.id,
        "added_at": datetime.now(),
        "username": message.from_user.username or f"ID{new_admin_id}"
    })

    # Уведомление нового администратора
    try:
        await bot.send_message(
            chat_id=new_admin_id,
            text="🎉 Вас назначили администратором бота!\nТеперь вы будете получать уведомления о новых заказах."
        )
    except Exception as e:
        print(f"❌ Не удалось уведомить нового администратора: {e}")

    # Уведомление супер-админов
    admin_name = await get_admin_username(message.from_user.id)
    await notify_all_admins(
        f"🛠 Администратор <b>{admin_name}</b> добавил нового администратора: ID {new_admin_id}"
    )

    await message.answer(f"✅ Пользователь {new_admin_id} успешно добавлен как администратор!")
    await state.clear()

@dp.callback_query(F.data == "remove_admin")
async def remove_admin_start(callback: types.CallbackQuery, state: FSMContext):
    """Запрос ID администратора для удаления"""
    admins = await db[ADMINS_COLLECTION].find({"is_superadmin": False}).to_list(None)
    if not admins:
        await callback.message.answer("❌ Нет администраторов для удаления.")
        await callback.answer()
        return

    keyboard = InlineKeyboardBuilder()
    for admin in admins:
        keyboard.row(InlineKeyboardButton(
            text=f"ID {admin['user_id']} ({admin.get('username', '')})",
            callback_data=f"remove_admin_{admin['user_id']}"
        ))

    await callback.message.edit_text(
        "Выберите администратора для удаления:",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("remove_admin_"))
async def remove_admin_finish(callback: types.CallbackQuery):
    """Удаление администратора"""
    admin_id = int(callback.data.split("_")[-1])
    if admin_id == int(os.getenv("SUPERADMIN_ID")):
        await callback.answer("❌ Нельзя удалить супер-админа!", show_alert=True)
        return

    result = await db[ADMINS_COLLECTION].delete_one({"user_id": admin_id})
    if result.deleted_count > 0:
        # Уведомление удаленного администратора
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="ℹ️ Ваши права администратора были отозваны."
            )
        except Exception as e:
            print(f"❌ Не удалось уведомить удаленного администратора: {e}")

        # Уведомление супер-админов
        admin_name = await get_admin_username(callback.from_user.id)
        removed_admin = await get_admin_username(admin_id)
        await notify_all_admins(
            f"🛠 Администратор <b>{admin_name}</b> удалил администратора: {removed_admin} (ID {admin_id})"
        )

        await callback.message.edit_text(f"✅ Администратор ID {admin_id} удалён.")
    else:
        await callback.message.edit_text("❌ Администратор не найден.")
    await callback.answer()

@dp.callback_query(F.data == "list_admins")
async def list_admins(callback: types.CallbackQuery):
    """Показать список администраторов"""
    admins = await db[ADMINS_COLLECTION].find().sort("is_superadmin", -1).to_list(None)
    if not admins:
        await callback.message.answer("❌ Нет администраторов в базе.")
        await callback.answer()
        return

    message = ["👥 <b>Список администраторов:</b>\n"]
    for admin in admins:
        status = " (супер-админ)" if admin.get("is_superadmin") else ""
        added_at = admin.get("added_at", datetime.now()).strftime("%d.%m.%Y")
        username = admin.get("username", "")
        message.append(f"• <code>{admin['user_id']}</code> {username}{status} - добавлен {added_at}")

    await callback.message.answer("\n".join(message), parse_mode="HTML")
    await callback.answer()

async def on_startup():
    """Действия при запуске бота"""
    # Создаем индексы
    await db[ADMINS_COLLECTION].create_index([("user_id", 1)], unique=True)
    await db[ORDERS_COLLECTION].create_index([("status", 1)])
    await db[ORDERS_COLLECTION].create_index([("created_at", -1)])
    
    # Добавляем супер-админа из .env
    await ensure_superadmin_exists()
    
    # Уведомляем администраторов о запуске
    await notify_all_admins("🤖 Бот для уведомлений о заказах запущен и готов к работе!")
    
    # Запускаем отслеживание заказов
    asyncio.create_task(watch_orders())

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    asyncio.run(main())