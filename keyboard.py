from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton, )


menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Записать задачу"),
         KeyboardButton(text="📋 Все задачи")],
        [KeyboardButton(text="🗑 Удалить задачу"),
         KeyboardButton(text="✏️ Редактировать задачу")]
    ], resize_keyboard=True
)

