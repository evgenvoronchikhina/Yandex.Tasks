from dataclasses import dataclass, fields, asdict, astuple
from contextlib import contextmanager  
from abc import ABC, abstractclassmethod
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
import json
import sqlite3
import os
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime


load_dotenv('./app/config/.env')


class DataClassTableName(ABC):
    
    @abstractclassmethod
    def get_table_name(cls):
        pass

    
@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn # С конструкцией yield вы познакомитесь в следующем модуле 
                   # Пока воспринимайте её как return, после которого код может продолжить выполняться дальше
    # Даже если в процессе соединения произойдёт ошибка, блок finally всё равно его закроет
    finally:
        conn.close()

def extract_data_from_sqlite(conn, data_class: DataClassTableName):
    curs = conn.cursor()
    curs.execute(f"SELECT * FROM {data_class.get_table_name()};")
    cnt = 0
    while (len(data := curs.fetchmany(1000)) > 0):
        path_to_file = f'tmp_{data_class.get_table_name()}_{str(cnt := cnt + 1)}.json'
        Path(path_to_file).parent.mkdir(exist_ok=True, parents=True)
        with open(path_to_file, 'w') as tmp_tile:
            json.dump([dict(i) for i in data], tmp_tile)
        
    
def load_to_postgres(conn, data_class: DataClassTableName, trunc=False):
    # path_to_file = f'tmp_{data_class.get_table_name()}.json'
    for i, path_to_file in enumerate([i for i in Path('./').iterdir() if f'tmp_{data_class.get_table_name()}' in i.name]):
        with open(path_to_file) as f:
            data = json.load(f)
        with conn.cursor() as cursor:
            if trunc and i == 0:
                cursor.execute(f"""TRUNCATE content.{data_class.get_table_name()} CASCADE""")
            # column_names = [field.name for field in fields(data_class)]
            column_names_str = ', '.join([field.name for field in fields(data_class)])
            col_name_in_val = ', '.join([f'%({field.name})s' for field in fields(data_class)])
            # col_count = ', '.join(['%s'] * len(column_names))
            # for i in range(len(data) // 1000 + (len(data) % 1000 > 0)):
            #     args = ','.join(cursor.mogrify(f"({col_count})", astuple(data_class(**item))).decode('utf-8') 
            #                     for item in data[i*1000: (i+1)*1000])
            execute_batch(cursor, f"""INSERT INTO content.{data_class.get_table_name()} ({column_names_str})
                            VALUES(
                                {col_name_in_val}
                            );
                            """, [asdict(data_class(**item)) for item in data])
                # cursor.execute(f"""
                # INSERT INTO content.{data_class.get_table_name()} ({column_names_str})
                # VALUES {args}
                # ON CONFLICT (id) DO NOTHING
                # """)
        os.remove(path_to_file)

def sqlite_to_postgres(list_data_classes):
    db_path = '.\\app\\sqlite_to_postgres\\db.sqlite'
    dsn = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'options': '-c search_path=content',
    }
    for i in list_data_classes:
        with conn_context(db_path) as conn:
            extract_data_from_sqlite(conn, i)
        with psycopg2.connect(**dsn) as conn:
            load_to_postgres(conn, i, True)


@dataclass
class FilmWork(DataClassTableName):
    id: uuid4
    title: str
    description: str
    creation_date: str
    file_path: str
    rating: float
    type: str
    created_at: str
    updated_at: str
    
    @classmethod
    def get_table_name(cls):
        return 'film_work'


@dataclass
class Genre(DataClassTableName):
    id: uuid4
    name: str
    description: str
    created_at: str
    updated_at: str
    
    @classmethod
    def get_table_name(cls):
        return 'genre'
    

@dataclass
class Person(DataClassTableName):
    id: uuid4
    full_name: str
    created_at: str
    updated_at: str
    
    @classmethod
    def get_table_name(cls):
        return 'person'
    
    
@dataclass
class GenreFilmWork(DataClassTableName):
    id: uuid4
    genre_id: uuid4
    film_work_id: uuid4
    created_at: str
    
    @classmethod
    def get_table_name(cls):
        return 'genre_film_work'
    
    
@dataclass
class PersonFilmWork(DataClassTableName):
    id: uuid4
    film_work_id: uuid4
    person_id: uuid4
    role: str
    created_at: str
    
    @classmethod
    def get_table_name(cls):
        return 'person_film_work'
    

if __name__ == '__main__':
    a = datetime.now()
    sqlite_to_postgres([FilmWork, Genre, Person, GenreFilmWork, PersonFilmWork])
    print(datetime.now() - a)

