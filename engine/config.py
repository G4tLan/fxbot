import os
from peewee import SqliteDatabase

# Database Configuration
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')
db = SqliteDatabase(DB_NAME)

# Global Configuration
config = {
    'app': {
        'debug': os.getenv('DEBUG', 'True').lower() == 'true',
    },
    'database': {
        'name': DB_NAME,
        'engine': 'sqlite'
    }
}
