import sqlalchemy
import psycopg2
from sqlalchemy import create_engine

from data_collection import data_dict

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:pass@localhost:5432/COVID-19")
con = engine.connect()

print(engine)

for key, value in data_dict.items():
    value.to_sql(key, engine)