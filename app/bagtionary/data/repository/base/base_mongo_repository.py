from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from core.db.mongo import mongo
from core.util.log_util import logger


class DefaultMongoRepository:
    collection: Optional[AsyncIOMotorCollection] = None

    def __init__(self, collection):
        self.collection = mongo.db[collection]

    async def is_empty(self) -> bool:
        return await self.count() <= 0

    async def count(self, filter: Optional[dict] = None, default=None) -> Optional[int]:
        if self.collection is not None:
            return await self.collection.count_documents(filter)
        return default

    async def paged_select(self, filter: Optional[dict] = None, projection: Optional[dict] = None, page: int = 0, size: int = 0,
                           sort: Optional[dict] = None) -> list:
        if self.collection is not None:
            # self.collection.find(filter=filter, projection=projection).skip(skip).limit(limit).sort(sort).to_list(limit)
            skip = page * size if page is not None and size is not None else 0
            limit = size if size is not None else 0
            cursor = self.collection.find(filter=filter, projection=projection, sort=sort, skip=skip, limit=limit)
            return await cursor.to_list(None)
        else:
            logger.w("collection is None")
        return []

    async def select(self, filter: Optional[dict] = None, projection: Optional[dict] = None, limit: int = 0, skip: int = 0,
                     sort: Optional[dict] = None) -> list:
        if self.collection is not None:
            # self.collection.find(filter=filter, projection=projection).skip(skip).limit(limit).sort(sort).to_list(limit)
            cursor = self.collection.find(filter=filter, projection=projection, sort=sort, skip=skip, limit=limit)
            return await cursor.to_list(None)
        else:
            logger.w("collection is None")
        return []

    async def aggregate(self, pipeline: list) -> list:
        if self.collection is not None:
            return await self.collection.aggregate(pipeline).to_list(None)
        return []

    async def insert(self, obj: dict = ()):
        if self.collection is not None:
            await self.collection.insert_one(obj)

    async def insert_many(self, objs: list = (), ordered=True):
        if self.collection is not None:
            await self.collection.insert_many(objs, ordered=ordered)

    async def insert_or_update(self, filter, update):
        if self.collection is not None:
            await self.collection.update_one(filter, update, upsert=True)

    async def update(self, filter, update):
        if self.collection is not None:
            result = await self.collection.update_one(filter, update)

    async def delete(self, filter):
        if self.collection is not None:
            result = await self.collection.delete_one(filter)
            logger.d(f'deleted {result.deleted_count}')

    async def delete_many(self, filter):
        if self.collection is not None:
            result = await self.collection.delete_many(filter)
            logger.d(f'deleted {result.deleted_count}')


def get_repository(collection: str) -> DefaultMongoRepository:
    return DefaultMongoRepository(collection)
