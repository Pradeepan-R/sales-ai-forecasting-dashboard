from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class SalesRecord(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    product = Column(String, index=True)
    region = Column(String, index=True)
    store_type = Column(String)
    price = Column(Float)
    discount = Column(Float)
    marketing_spend = Column(Float)
    sales = Column(Float)
    units_sold = Column(Integer)
    season = Column(String)
