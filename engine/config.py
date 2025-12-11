import os
from peewee import SqliteDatabase

# Database Configuration
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

# Use a higher timeout to prevent "database is locked" errors
# Enable WAL (Write-Ahead Logging) mode for better concurrency
db = SqliteDatabase(DB_NAME, pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 1
}, timeout=10) # 10 seconds timeout

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
