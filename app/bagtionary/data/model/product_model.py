from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from core.db.mysql import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_id = Column(String(100), name="rawId")
    product_id = Column(String(100), name="productId", nullable=True)
    brand = Column(String(10))
    type = Column(String(100))
    created_date = Column(BigInteger, name="createdDate")
    last_modified_date = Column(BigInteger, name="lastModifiedDate")
    image_url = Column(String, name="imageUrl")
    sub_image_url_list = Column(String, name="subImageUrlList")
    standardized_color_list = Column(String, name="standardizedColorList")


class Description(Base):
    __tablename__ = "description"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(5))
    name = Column(String(100))
    material = Column(String(50))
    description = Column(String)
    color_list = Column(String, name="colorList")
    spec = Column(String)


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(5))
    product_url = Column(String, name="productUrl")
    new_arrival_date = Column(BigInteger, name="newArrivalDate")
    launched_date = Column(BigInteger, name="launchedDate")
    latest_price = Column(Integer, ForeignKey("Price.id"), name="latestPrice")


class Price(Base):
    __tablename__ = "price"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)
    value = Column(Integer)
    display = Column(String(20))
    sales_id = Column(Integer, ForeignKey("sales.id"))

    sales = relationship("Sales", backref="price")
