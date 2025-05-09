import time
time.sleep(5)

import pandas as pd
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("postgresql+psycopg2://stud:stud@db/archdb", echo = True)

with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS reports CASCADE;"))
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    connection.commit()

time.sleep(2)
try:
    with engine.connect() as connection:
        connection.execute(text("CREATE TABLE users (id SERIAL PRIMARY KEY, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, role VARCHAR(50) NOT NULL, password VARCHAR(255) NOT NULL, email VARCHAR(255) UNIQUE NOT NULL);"))
        connection.execute(text("CREATE INDEX idx_users_id ON users(id);"))
        connection.execute(text("CREATE TABLE reports (id SERIAL PRIMARY KEY, title VARCHAR(255) NOT NULL, author_first_name VARCHAR(100) NOT NULL, author_last_name VARCHAR(100) NOT NULL, author_email VARCHAR(255) UNIQUE NOT NULL, status VARCHAR(50) NOT NULL);"))
        connection.execute(text("CREATE INDEX idx_reports_id ON reports(id);"))
        connection.commit()
except Exception as e:
    print(f"Ошибка при создании таблиц. Опять: {e}")

df = pd.read_json("users.json")
#df.insert(0, "id", range(1, len(df) + 1))  
df['password'] = df['password'].apply(lambda password: pwd_context.hash(password))
df.to_sql("users", con=engine, if_exists = 'append', index=False) 

df = pd.read_json("reports.json")
#df.insert(0, "id", range(1, len(df) + 1))  
df.to_sql("reports", con=engine, if_exists = 'append', index=False)


# Добавим уникальный идентификатор
# ALTER TABLE "users" ADD COLUMN id SERIAL PRIMARY KEY
# UPDATE "users" SET login=email
# explain select * from users where first_name='Alan';
# create index fn on users(first_name);
