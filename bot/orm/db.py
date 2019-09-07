import datetime
import json

import peewee
import sys
import os

'''
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    with open(os.path.join(BASE_DIR, 'orm', 'db_credentials.json'), 'r') as f:
        credentials = json.load(f)
except FileNotFoundError:
    print('Database credentials file not found (\'orm/db_credentials.json\')')
    sys.exit(1)

db = peewee.PostgresqlDatabase(
    credentials['name'],
    user=credentials['user'],
    password=credentials['password'],
    host=credentials['host'],
    port=credentials['port']
)
'''

# Uncomment the line below if you wish to use Sqlite instead of Postgres for the bot's database
db = peewee.SqliteDatabase('bot.db')
