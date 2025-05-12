"""
Handles database connection state.
Peewee uses lazy initialization to automatically open a database connection but does not automatically close the connection.
The database manager uses explicit open/close actions for cleaner context management.
"""

from peewee import SqliteDatabase

from log_helper import logger

# Define the database
# peewee will automatically create the database the first time a connection is made
# SQLite does not enable foreign keys by default
db = SqliteDatabase("socialnetwork.db", pragmas={"foreign_keys": 1})

# Create an in-memory testing database
temp_db = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})


def open_db(database: SqliteDatabase):
    """
    Connect to the database
    """
    if database.is_closed():
        database.connect()
        logger.info("Database connection opened.")


def close_db(database: SqliteDatabase):
    """
    Disconnect from the database
    """
    if not database.is_closed():
        database.close()
        logger.info("Database connection closed.")
