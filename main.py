import asyncio
import aiosqlite
from pyrogram import Client
import config

app = Client("piar", api_id=config.tg_api_id, api_hash=config.tg_api_hash)

async def fetch_posts():
    """Извлекает все посты из базы данных."""
    async with aiosqlite.connect(config.db_path) as db:
        cursor = await db.execute("SELECT group_id, text, time_sec, image FROM posts")
        posts = await cursor.fetchall()
        await cursor.close()
    return posts

async def send_message(group_id, text, image_path):
    """Отправляет сообщение в группу."""
    try:
        if image_path:
            await app.send_photo(chat_id=group_id, photo=image_path, caption=text)
        else:
            await app.send_message(chat_id=group_id, text=text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в {group_id}: {e}")

async def schedule_post(group_id, text, time_sec, image_path):
    """Планирует отправку сообщения с повторением."""
    while True:
        await send_message(group_id, text, image_path)
        await asyncio.sleep(time_sec)

async def post_manager():
    """Управляет задачами постов и добавляет новые при их появлении."""
    active_tasks = {}

    while True:
        posts = await fetch_posts()
        for post in posts:
            group_id, text, time_sec, image_path = post

            # Если задача для этого group_id еще не запущена, создаем ее
            if group_id not in active_tasks:
                task = asyncio.create_task(schedule_post(group_id, text, time_sec, image_path))
                active_tasks[group_id] = task

        # Проверяем на завершенные задачи и удаляем их из active_tasks
        completed = [group_id for group_id, task in active_tasks.items() if task.done()]
        for group_id in completed:
            del active_tasks[group_id]

        await asyncio.sleep(10)  # Проверяем обновления каждые 10 секунд

async def main():
    """Основная точка входа."""
    await app.start()
    try:
        await post_manager()
    finally:
        await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()