import sqlalchemy

from OLD.data_collection import data_dict

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:d@t@2020@localhost:5432/COVID-19")
con = engine.connect()

print(engine)

for key, value in data_dict.items():
    value.to_sql(key, engine, if_exists='replace')
