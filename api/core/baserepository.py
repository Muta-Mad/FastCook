from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db


class BaseRepository:
    """Базовый класс операций в базе данных"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, obj):
        """сохраняет объект в базе данных"""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)

    async def update(self, obj, **kwargs):
        """обновляет объект в базе данных"""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.save(obj)

async def get_repository(session: AsyncSession = Depends(get_db)):
    """создает зависимость для BaseRepository"""
    return BaseRepository(session)