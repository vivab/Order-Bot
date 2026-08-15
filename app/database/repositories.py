from sqlalchemy import select

from app.database.db import async_session
from app.database.models import User


async def get_user(telegram_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()


async def get_or_create_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
):
    async with async_session() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if user:
            # Обновляем username, если он изменился
            user.username = username
            user.first_name = first_name

            await session.commit()

            return user, False

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user, True
