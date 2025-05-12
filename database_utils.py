"""
Handles database state
"""

from peewee import SqliteDatabase

# Disabling some noisy linting for peewee _meta references
# pylint: disable=W0212, E1101

from log_helper import logger
from socialnetwork_model import BaseModel


def current_tables(database: SqliteDatabase):
    """
    Returns list of existing tables in the database.
    """
    return database.get_tables()


def ensure_tables(database: SqliteDatabase):
    """
    Ensures tables exist
    """

    # Collect all existing tables
    existing_tables = current_tables(database)

    # Dynamically gather all models inheriting from BaseModel (the tables we expect to exist)
    models = BaseModel.__subclasses__()

    # If an expected table does not exist then append it to the list of tables to create
    tables_to_create = []
    for model in models:
        if model._meta.table_name not in existing_tables:
            tables_to_create.append(model)

    # If there are any tables missing then create them and log
    if tables_to_create:
        database.create_tables(tables_to_create, safe=True)
        logger.info(
            f"Created tables: {[model._meta.table_name for model in tables_to_create]}"
        )
    else:
        logger.info("All required tables already exist.")


def drop_tables(database: SqliteDatabase):
    """
    Drop all tables from the database
    """

    # Collect all existing tables
    existing_tables = current_tables(database)

    # Dynamically gather all models inheriting from BaseModel (the tables we expect to exist)
    models = BaseModel.__subclasses__()

    # Filter only those models whose tables currently exist in the database
    models_to_drop = [
        model for model in models if model._meta.table_name in existing_tables
    ]

    if models_to_drop:
        database.drop_tables(models_to_drop, safe=True)
        logger.info(
            f"Dropped tables: {[model._meta.table_name for model in models_to_drop]}"
        )
    else:
        logger.info("No tables to drop.")
