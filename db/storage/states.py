import logging
from typing import List
from dataclasses import dataclass
from aiogram.fsm.state import State, StatesGroup

from db.db import DB


class Survey(StatesGroup):
    name = State()
    phone = State()
    email = State()
    address = State()
    furniture_type = State()
    design_interest = State()
    budget = State()
    delivery = State()
    company_name = State()
    cooperation = State()


logger = logging.getLogger(__name__)


@dataclass
class Data_responses:
    id: int
    user_id: int
    name: str
    phone: int
    email: str
    address: str
    furniture_type: str
    design_interest: str
    budget: str
    delivery: str
    company_name: str
    cooperation: str
    created_at: str


class SurveyResponses:
    __table = "survey_responses"

    def __init__(self, db: DB):
        self._db = db

    async def init(self):
        logger.debug(f'Инициализация таблицы {self.__table}')
        await self._db.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.__table} (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL,
                furniture_type TEXT,
                design_interest TEXT,
                budget TEXT,
                delivery TEXT,
                company_name TEXT,
                cooperation TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """
        )

    async def save_survey(self, data: dict):
        query = """
        INSERT INTO survey_responses (
            user_id, name, phone, email, address, furniture_type, design_interest, 
            budget, delivery, company_name, cooperation, created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW()
        )
        """
        await self._db.execute(query,
                               data["user_id"],
                               data["name"],
                               data["phone"],
                               data["email"],
                               data["address"],
                               data.get("furniture_type", None),
                               data.get("design_interest", None),
                               data.get("budget", None),
                               data.get("delivery", None),
                               data.get("company_name", None),
                               data.get("cooperation", None)
                               )

    async def update_survey(self, user_id: int, data: dict):
        query = """
        UPDATE survey_responses
        SET 
            name = COALESCE($2, name),
            phone = COALESCE($3, phone),
            email = COALESCE($4, email),
            address = COALESCE($5, address),
            furniture_type = COALESCE($6, furniture_type),
            design_interest = COALESCE($7, design_interest),
            budget = COALESCE($8, budget),
            delivery = COALESCE($9, delivery),
            company_name = COALESCE($10, company_name),
            cooperation = COALESCE($11, cooperation),
            created_at = NOW()
        WHERE user_id = $1;
        """
        await self._db.execute(query, user_id,
                               data.get("name"), data.get("phone"), data.get("email"),
                               data.get("address"), data.get("furniture_type"),
                               data.get("design_interest"), data.get("budget"),
                               data.get("delivery"), data.get("company_name"),
                               data.get("cooperation"))

    async def get_by_id(self, chat_id: int) -> Data_responses | None:
        data = await self._db.fetchrow(
            f"SELECT * FROM {self.__table} WHERE user_id = '{chat_id}'"
        )
        print("data_BD", data)
        if data is None:
            return None
        return Data_responses(
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            data[6],
            data[7],
            data[8],
            data[9],
            data[10],
            data[11],
            data[12]
        )

    async def get_user_by_id(self, chat_id: int):
        data = await self._db.fetch(
            f"SELECT user_id FROM {self.__table} WHERE user_id = '{chat_id}'"
        )
        print("data_BD", data)
        if data is None:
            return None
        return data
