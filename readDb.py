import sqlite3
from sqlite3 import Error
from dateutil import parser
from re import search
import json

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def handle_data(conn):
    query = 'SELECT * FROM videos ORDER BY date(published_date) ASC'
    cur = conn.cursor()
    cur.execute(query)

    rows = cur.fetchall()

    the_list = []
    for row in rows:
        mon = dict()
        title = row[1]
        date = row[4]
        description = row[2]
        url = row[6]

        try:
            name = search('(.+)(l|\|)', title).group(1).strip()
            mon['name'] = name
            # print(name)
        except Exception:
            continue

        try:
            congthuc = search('((NGUYÊN LIỆU:? *\n*)|(Nguyên liệu:? *\n*)|\n\n)((.|\n)+?)(#|MÓN NGON|-----------|- W)', description).group()
            # .replace('#', '').replace('\n', chr(10))
            # print(congthuc)
        except Exception:
            congthuc = ''
        
        parsed_date = parser.parse(date).strftime('%d/%m/%Y')
        
        mon['date'] = parsed_date
        mon['url'] = url
        mon['nguyen_lieu'] = congthuc

        the_list.append(mon)
    
    with open('youtube.json', 'w', encoding='utf-8') as output:
        json.dump(the_list, output, ensure_ascii=False)

def main():
    db = 'database.db'

    conn = create_connection(db)
    with conn:
        handle_data(conn)


if __name__ == '__main__':
    main()
