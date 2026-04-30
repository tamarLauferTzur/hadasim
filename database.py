from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models import User


async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.school, document_models=[User])
