from aiogram import F, Router
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

import keyboard as kb
from states import Task, TaskState
from database.requests import add_task, get_tasks, delete_task_by_id, update_task_title


user = Router()

todo_list = {}

@user.message(CommandStart())
async def say_hello(message: Message):
    user_id = message.from_user.id

    if user_id not in todo_list:
        todo_list[user_id] = []

    await message.answer("Привет, этот бот поможет управлять списком задач", reply_markup=kb.menu)

@user.message(F.text == "➕ Записать задачу")
async def do_list(message: Message, state: FSMContext):
    await message.answer("✍️ Напишите задачу ниже:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Task.do_task)

@user.message(Task.do_task)
async def set_task(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in todo_list:
        todo_list[user_id] = []

    await add_task(user_id, message.text)
    await state.clear()
    await message.answer("✅ Задача успешно добавлена!", reply_markup=kb.menu)

@user.message(F.text == "📋 Все задачи")
async def all_tasks(message: Message):
    user_id = message.from_user.id
    page = 1
    per_page = 5
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    user_tasks = await get_tasks(user_id)

    if not user_tasks:
        await message.answer("📭 Список задач пуст!")
        return

    text_tasks = "📋 Твои задачи:\n\n"

    for index, task in enumerate(user_tasks[start_index:end_index], start_index + 1):
        text_tasks += f"{index}. {task.title}\n"

    builder = InlineKeyboardBuilder()

    if len(user_tasks) > end_index:
        builder.add(InlineKeyboardButton(text="➡️", callback_data="page_2"))

    await message.answer(text_tasks, reply_markup=builder.as_markup())

@user.callback_query(F.data.startswith("page_"))
async def turn_view_page(callback: CallbackQuery):
    current_page = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    per_page = 5
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page

    tasks = await get_tasks(user_id)

    text_task = f"📋 **Твои задачи (Страница {current_page}):**\n\n"
    for index, task in enumerate(tasks[start_index:end_index], start_index + 1):
        text_task += f"{index}. {task.title}\n"

    builder = InlineKeyboardBuilder()
    navigation_buttons = []

    if current_page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page_{current_page - 1}"))

    if len(tasks) > end_index:
        navigation_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{current_page + 1}"))

    if navigation_buttons:
        builder.row(*navigation_buttons)

    await callback.message.edit_text(text_task, reply_markup=builder.as_markup())
    await callback.answer()

@user.callback_query(F.data.startswith("delpage_"))
async def turn_page(callback: CallbackQuery):
    current_page = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    per_page = 5
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page

    tasks = await get_tasks(user_id)

    text_task = "📋 Твои задачи:\n\n"
    for index, task in enumerate(tasks[start_index:end_index], start_index + 1):
        text_task += f"{index}. {task.title}\n"

    builder = InlineKeyboardBuilder()

    for task in tasks[start_index:end_index]:
        task_num = tasks.index(task) + 1
        builder.add(InlineKeyboardButton(text=str(task_num), callback_data=f"del_{task.id}"))

    navigation_buttons = []

    if current_page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"delpage_{current_page - 1}"))

    if len(tasks) > end_index:
        navigation_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"delpage_{current_page + 1}"))

    if navigation_buttons:
        builder.row(*navigation_buttons)

    await callback.message.edit_text(   text_task, reply_markup=builder.as_markup())
    await callback.answer()


@user.message(F.text == "🗑 Удалить задачу")
async def start_delete(message: Message):
    user_id = message.from_user.id
    current_page = 1
    per_page = 5
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page

    tasks = await get_tasks(user_id)

    if not tasks:
        await message.answer("📭 Список задач пуст!")
        return

    builder = InlineKeyboardBuilder()

    text_task = "🗑 Выберите задачу для удаления (Страница 1):\n\n"
    for index, task in enumerate(tasks[start_index:end_index], start_index + 1):
        text_task += f"{index}. {task.title}\n"

    for task in tasks[start_index:end_index]:
        task_num = tasks.index(task) + 1
        builder.add(InlineKeyboardButton(text=str(task_num), callback_data=f"del_{task.id}"))

    delete_navigation = []

    if len(tasks) > end_index:
        delete_navigation.append(InlineKeyboardButton(text="➡️", callback_data="delpage_2"))

    if delete_navigation:
        builder.row(*delete_navigation)

    await message.answer(text_task, reply_markup=builder.as_markup())
@user.callback_query(F.data.startswith("del_"))
async def del_task(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_id = int(callback.data.split("_")[1])
    removed_task_text = await delete_task_by_id(task_id)

    await callback.message.edit_text(f"❌Задачу удалено\n\n 📌{removed_task_text}")
    await callback.answer(text="Задача успешно удалена!")

@user.message(F.text.endswith("Редактировать задачу"))
async def start_edit(message: Message):
    user_id = message.from_user.id
    current_page = 1
    per_page = 5
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page

    tasks = await get_tasks(user_id)

    if not tasks:
        await message.answer("📭 Список задач пуст!")
        return

    builder = InlineKeyboardBuilder()

    text_task = "✏️ **Выберите задачу для редактирования (Страница 1):**\n\n"
    for index, task in enumerate(tasks[start_index:end_index], start_index + 1):
        text_task += f"{index}. {task.title}\n"

    for task in tasks[start_index:end_index]:
        task_num = tasks.index(task) + 1
        builder.add(InlineKeyboardButton(
            text=str(task_num),
            callback_data=f"edit_{task.id}")
        )

    edit_navigation = []
    if len(tasks) > end_index:
        edit_navigation.append(InlineKeyboardButton(text="➡️", callback_data="editpage_2"))

    if edit_navigation:
        builder.row(*edit_navigation)

    await message.answer(text_task, reply_markup=builder.as_markup())


@user.callback_query(F.data.startswith("editpage_"))
async def turn_page_edit(callback: CallbackQuery):
    current_page = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    per_page = 5
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page

    tasks = await get_tasks(user_id)

    text_task = f"✏️ Выберите задачу для редактирования (Страница {current_page}):\n\n"
    for index, task in enumerate(tasks[start_index:end_index], start_index + 1):
        text_task += f"{index}. {task.title}\n"

    builder = InlineKeyboardBuilder()

    for task in tasks[start_index:end_index]:
        task_num = tasks.index(task) + 1
        builder.add(InlineKeyboardButton(text=str(task_num), callback_data=f"edit_{task.id}"))

    navigation_buttons = []

    if current_page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"editpage_{current_page - 1}"))

    if len(tasks) > end_index:
        navigation_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"editpage_{current_page + 1}"))

    if navigation_buttons:
        builder.row(*navigation_buttons)

    await callback.answer()
    await callback.message.edit_text(text_task, reply_markup=builder.as_markup())

@user.callback_query(F.data.startswith("edit_"))
async def process_edit_click(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])

    await state.update_data(edit_task_id=task_id)
    await state.set_state(TaskState.edit_title)

    await callback.answer()
    await callback.message.answer("📝 Введите новое название для этой задачи:")

@user.message(TaskState.edit_title)
async def save_new_task(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("edit_task_id")

    new_title = message.text
    await update_task_title(task_id, new_title)
    await state.clear()
    await message.answer(f"✅ Успешно! Название задачи изменено на:\n\n📌 {new_title}")



