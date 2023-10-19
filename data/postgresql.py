import psycopg2
import json

with open('config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

try:
    connection = psycopg2.connect(
        host=cfg['PostgresSQL']['host'],
        user=cfg['PostgresSQL']['user'],
        password=cfg['PostgresSQL']['password'],
        database=cfg['PostgresSQL']['database'])

    pcursor = connection.cursor()
    connection.autocommit = True
    
    print(F"[POSTGRESQL] [INFO] CONNECT SUCCESSFULLY")
except psycopg2.Error as e:
    print(F"[POSTGRESQL] [ERROR] CODE {e}")