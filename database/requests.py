from database.models import async_session
from database.models import Task
from sqlalchemy import select, delete


async def add_task(tg_id, text):
    async with async_session() as session:
        new_task = Task(title=text, user_tg_id=tg_id)
        session.add(new_task)
        await session.commit()

async def get_tasks(tg_id):
    async with async_session() as session:
        query = select(Task).where(Task.user_tg_id == tg_id)
        result = await session.execute(query)
        return result.scalars().all()


async def delete_task_by_id(task_id: int):
    async with async_session() as session:
        query_select = select(Task).where(Task.id == task_id)
        result = await session.execute(query_select)
        task = result.scalar()

        task_title = task.title if task else "Неизвестная задача"

        query_delete = delete(Task).where(Task.id == task_id)
        await session.execute(query_delete)
        await session.commit()

        return task_title

async def update_task_title(task_id: int, new_title: str):
    async with async_session() as session:
        query = select(Task).where(Task.id == task_id)
        result = await session.execute(query)
        task = result.scalar()

        if task:
            task.title = new_title
            await session.commit()