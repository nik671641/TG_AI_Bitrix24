import asyncpg
import logging
from typing import List, Any

logger = logging.getLogger(__name__)


class DB:
    def __init__(
        self,
        host: str,
        port: str,
        login: str,
        password: str,
        database: str,
        pool_size: int = 10,
    ):
        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self._database = database
        self._pool_size = pool_size
        self._pool = None

    async def create_pool(self):
        if not self._pool:
            logger.debug(f"creating connection pool")
            self._pool = await asyncpg.create_pool(
                f"postgres://{self._login}:{self._password}@{self._host}:{self._port}/{self._database}"
            )

    async def close_pool(self):
        if self._pool and not self._pool._closed:
            logger.debug(f"closing connection pool")
            await self._pool.close()


    async def execute(self, query, *params):
        logger.debug(f"execute query: {query}, params: {str(params)}")
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                return await conn.execute(query, *params)

    async def fetchrow(self, query, *params, **kwargs) -> List:
        logger.debug(f"fetchrow query: {query}")
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchrow(query, *params, **kwargs)

    async def fetch(self, query, *params) -> List[List]:
        logger.debug(f"fetch query: {query}")
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch(query, *params)

    async def fetchval(self, query, *params) -> Any:
        logger.debug(f"fetchval: {query}")
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchval(query, *params)


