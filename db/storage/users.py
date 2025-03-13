import asyncpg
import logging
from typing import List
from dataclasses import dataclass
from datetime import datetime

from db.db import DB

logger = logging.getLogger(__name__)


@dataclass
class User:

    id: int
    user_id: int
    username: str
    full_name: str
    category: str
    created_at: str


class UserStorage:
    __table = "users"

    def __init__(self, db: DB):
        self._db = db

    async def init(self):
        logger.debug(f'Инициализация таблицы {self.__table}')
        await self._db.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.__table} (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,  
                username TEXT,                   
                full_name TEXT,                  
                category TEXT CHECK (category IN ('Компания', 'Частное лицо')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    async def create(self, user_id: int, username: str, full_name: str, category: str):
        """Добавляет нового пользователя в БД"""
        try:
            await self._db.execute(
                f"""
                INSERT INTO {self.__table} (user_id, username, full_name, category) 
                VALUES ($1, $2, $3, $4) 
                ON CONFLICT (user_id) DO NOTHING
                """,
                user_id, username, full_name, category
            )
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")

    async def get_all_users(self) -> List[int]:
        query = "SELECT id FROM users;"
        result = await self._db.fetch(query)
        return [row[0] for row in result]

    async def get_by_id(self, id: int) -> User | None:
        data = await self._db.fetchrow(
            f"SELECT * FROM {self.__table} WHERE user_id = $1", id
        )

        if data is None:
            return None
        return User(
            data[0], data[1], data[2], data[3], data[4], data[5]
        )

    async def change_requests(self, user_id: int, delta: int):
        await self._db.execute(
            f"UPDATE {self.__table} SET requests = requests + {delta} WHERE id = {user_id}"
        )

    async def add_subscription(self, user_id, day_num):
        """Add subscription to existing one or from now. To add requests_num use self.change_requests."""

        query = f"""UPDATE {self.__table}
            SET subscription_end_utc = GREATEST(subscription_end_utc, NOW()) + INTERVAL '{day_num}' DAY
            WHERE id = {user_id};"""
        await self._db.execute(query)

    async def delete(self, user_id: int):
        await self._db.execute(
            f"""
            DELETE FROM {self.__table} WHERE id = {user_id}
        """
        )
