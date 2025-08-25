from fastapi import HTTPException
from starlette import status

from core.util.log_util import logger
from app.bagtionary.data.repository.base.base_mongo_repository import DefaultMongoRepository


class ProductViewCountRepository(DefaultMongoRepository):

    def __init__(self):
        super().__init__("product_view_count")

    async def add_count(self, raw_id: str):
        count = await self.count({"rawId": raw_id})
        if count is None:
            raise HTTPException(status_code=status.HTTP_500_UNAUTHORIZED)
        elif count <= 0:
            result = await self.collection.insert_one({"rawId": raw_id, "count": 1})
            logger.d(f"add_count created result: {result}")
            return 1
        else:
            added_count = count + 1
            result = await self.collection.update_one({"rawId": raw_id}, {"$inc": {"count": added_count}})
            logger.d(f"add_count updated result: {result}")
            return added_count
