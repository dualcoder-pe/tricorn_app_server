import logging
import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Mongo:

    def __init__(self):
        load_dotenv()
        self.url = os.getenv("MONGO_URL")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    def connect(self):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(self.url)
        self.db = self.client["bag_admin"]

    def close(self):
        self.client.close()


mongo = Mongo()

logging.getLogger('pymongo.command').setLevel(logging.INFO)
logging.getLogger('pymongo.connection').setLevel(logging.INFO)
logging.getLogger('pymongo.serverSelection').setLevel(logging.INFO)
