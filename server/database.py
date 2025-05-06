from dotenv import load_dotenv
from os import getenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    database=getenv("db_name", "neighborhood"),
    user=getenv("db_user"),
    password=getenv("db_password"),
    host=getenv("db_host", "localhost"),
    port=getenv("db_port", 5342)
)
cur = conn.cursor()
conn.autocommit = True

if __name__ == "__main__":
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL, slack VARCHAR(20) NOT NULL, created_at TIMESTAMP DEFAULT NOW(), PRIMARY KEY(id));")
    cur.execute("CREATE TABLE IF NOT EXISTS users_settings (\"user\" int NOT NULL, username VARCHAR(64), timezone VARCHAR(255), PRIMARY KEY (\"user\"), FOREIGN KEY (\"user\") REFERENCES users(id));")
    cur.execute("CREATE TABLE IF NOT EXISTS articles (id SERIAL, author int NOT NULL, title VARCHAR(255) NOT NULL, body TEXT NOT NULL, created_at TIMESTAMP DEFAULT NOW(), modified_at TIMESTAMP DEFAULT NOW(), PRIMARY KEY (id), FOREIGN KEY (author) REFERENCES users(id));")
    print("Tables created")