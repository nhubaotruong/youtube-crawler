import sqlite3

connection = sqlite3.connect('database.db')

cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                  id integer PRIMARY KEY,
                  title text NOT NULL,
                  description text NOT NULL,
                  duration text NOT NULL,
                  published_date text NOT NULL,
                  views integer NOT NULL,
                  url text NOT NULL
                  )''')


def insert_videos_info(videos_info):
    cursor.executemany('''INSERT INTO videos (title, description, duration, published_date, views, url) 
                          VALUES (?, ?, ?, ?, ?, ?)''', videos_info)
    connection.commit()


def close_connection():
    if connection is not None:
        connection.close()
