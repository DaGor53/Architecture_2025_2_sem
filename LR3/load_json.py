import time
time.sleep(5)

import pandas as pd
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("postgresql+psycopg2://stud:stud@db/archdb", echo = True)

# Удаляем таблицу вручную, если существует
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS reports CASCADE;"))
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))

df = pd.read_json("users.json")
df.insert(0, "id", range(1, len(df) + 1))  # Добавляем id с 1
df['password'] = df['password'].apply(lambda password: pwd_context.hash(password))
df.to_sql("users", con=engine, if_exists = 'replace', index=False) #replace

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE users ALTER COLUMN id SET DATA TYPE SERIAL;"))

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE users ADD PRIMARY KEY (id);"))
    connection.execute(text("CREATE INDEX idx_users_id ON users(id);"))


df = pd.read_json("reports.json")
df.insert(0, "id", range(1, len(df) + 1))  # Добавляем id с 1
df.to_sql("reports", con=engine, if_exists = 'replace', index=False) #replace

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE reports ALTER COLUMN id SET DATA TYPE SERIAL;"))

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE reports ADD PRIMARY KEY (id);"))
    connection.execute(text("CREATE INDEX idx_reports_id ON reports(id);"))

# Добавим уникальный идентификатор
# ALTER TABLE "users" ADD COLUMN id SERIAL PRIMARY KEY
# UPDATE "users" SET login=email
# explain select * from users where first_name='Alan';
# create index fn on users(first_name);
