from psycopg2.extras import RealDictCursor
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
dictcur = conn.cursor(cursor_factory=RealDictCursor)
conn.autocommit = True

class User:
    def create_user(slack, username) -> int:
        cur.execute("INSERT INTO users (slack) VALUES (%s) RETURNING id;", (slack, ))
        id = cur.fetchone()[0]
        cur.execute("INSERT INTO users_settings (\"user\", username) VALUES (%s, %s);", (id, username, ))
        return id

    def update_settings(user, key, value):
        cur.execute(f"UPDATE users_settings SET {key}=%s WHERE \"user\"=%s;", (value, user, ))

    def get_slack(id):
        cur.execute("SELECT slack FROM users WHERE id=%s LIMIT 1", (id, ))
        return cur.fetchone()

    def get_usersettings_by_id(id):
        dictcur.execute("SELECT * FROM users_settings WHERE \"user\"=%s LIMIT 1", (id, ))
        return dictcur.fetchone()

    def get_userid_by_slack(slack):
        cur.execute("SELECT id FROM users WHERE slack=%s LIMIT 1", (slack, ))
        return cur.fetchone()
    
    def get_public_user(id):
        dictcur.execute("SELECT *, (SELECT slack FROM users WHERE id=%s) FROM users_settings WHERE \"user\"=%s LIMIT 1", (id, id, ))
        return dictcur.fetchone()

class Articles:
    def get_user_articles(id):
        dictcur.execute("SELECT * FROM articles WHERE author=%s ORDER BY created_at ASC", (id, ))
        return dictcur.fetchall()

    def get_latest(limit=10, offset=10):
        dictcur.execute("SELECT * FROM articles ORDER BY created_at LIMIT %s OFFSET %s;", (limit, offset, ))
        return dictcur.fetchmany(limit)

    def get_article(id):
        dictcur.execute("SELECT * FROM articles WHERE id=%s LIMIT 1;", (id, ))
        return dictcur.fetchone()

    def get_pretty_article(id):
        dictcur.execute("SELECT body, created_at, id, modified_at, title, author AS authorid, (SELECT \"username\" FROM users_settings WHERE \"user\"=author) AS author FROM articles WHERE id=%s LIMIT 1;", (id, ))
        return dictcur.fetchone()

    def post_article(author, title, body):
        cur.execute("INSERT INTO articles (author, title, body) VALUES (%s, %s, %s) RETURNING id;", (author, title, body, ))
        return cur.fetchone()[0]
    
    def delete_article(id):
        cur.execute("DELETE FROM articles WHERE id=%s", (id, ))
    
class Reviews:
    def post_review(article:int, author:int, comment:str, note:int) -> int:
        cur.execute("INSERT INTO reviews (author, article, comment, note) VALUES (%s, %s, %s, %s) RETURNING id;", (author, article, comment, note, ))
        return cur.fetchone()
    
    def get_avg_note(article) -> float:
        cur.execute("SELECT AVG(note) FROM reviews WHERE article=%s;", (article, ))
        return cur.fetchone()
    
    def get_reviews(article, offset:int=0, limit:int=10):
        dictcur.execute("SELECT author, comment, note FROM reviews WHERE article=%s LIMIT %s OFFSET %s;", (article, limit, offset, ))
        return dictcur.fetchall()
    
    def delete_review(id):
        cur.execute("DELETE FROM reviews WHERE id=%s;", (id, ))

    def get_user_reviews(user, offset:int=0, limit:int=10):
        cur.execute("SELECT * FROM reviews WHERE author=%s LIMIT %s OFFSET %s;", (user, offset, limit, ))
        return cur.fetchall()

if __name__ == "__main__":
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL, slack VARCHAR(20) UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT NOW(), PRIMARY KEY(id));")
    cur.execute("CREATE TABLE IF NOT EXISTS users_settings (\"user\" int NOT NULL UNIQUE, username VARCHAR(64), timezone VARCHAR(255), bio VARCHAR(255), github VARCHAR(255), PRIMARY KEY (\"user\"), FOREIGN KEY (\"user\") REFERENCES users(id));")
    cur.execute("CREATE TABLE IF NOT EXISTS articles (id SERIAL, author int NOT NULL, title VARCHAR(255) NOT NULL, body TEXT NOT NULL, created_at TIMESTAMP DEFAULT NOW(), modified_at TIMESTAMP DEFAULT NOW(), PRIMARY KEY (id), FOREIGN KEY (author) REFERENCES users(id));")
    cur.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL, author int NOT NULL, article int NOT NULL, comment VARCHAR(512), note INT NOT NULL, PRIMARY KEY (id), FOREIGN KEY (author) REFERENCES users(id), FOREIGN KEY (article) REFERENCES articles(id), UNIQUE (author, article))")
    print("Tables created")