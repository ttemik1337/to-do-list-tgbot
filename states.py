from aiogram.fsm.state import StatesGroup, State

class Task(StatesGroup):
    do_task = State()

class TaskState(StatesGroup):
    edit_title = State()