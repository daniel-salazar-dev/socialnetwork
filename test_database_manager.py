"""
Testing suite for the database_manager
Patching the logger to avoid writing tests to the log file
"""

from unittest.mock import MagicMock, patch
from peewee import SqliteDatabase

import database_manager


def test_open_db_opens_when_closed():
    mock_db = MagicMock(spec=SqliteDatabase)
    mock_db.is_closed.return_value = True

    with patch("database_manager.logger") as mock_logger:
        database_manager.open_db(mock_db)
        mock_db.connect.assert_called_once()
        mock_logger.info.assert_called_once_with("Database connection opened.")


def test_open_db_skips_when_open():
    mock_db = MagicMock(spec=SqliteDatabase)
    mock_db.is_closed.return_value = False

    with patch("database_manager.logger") as mock_logger:
        database_manager.open_db(mock_db)
        mock_db.connect.assert_not_called()
        mock_logger.info.assert_not_called()


def test_close_db_closes_when_open():
    mock_db = MagicMock(spec=SqliteDatabase)
    mock_db.is_closed.return_value = False

    with patch("database_manager.logger") as mock_logger:
        database_manager.close_db(mock_db)
        mock_db.close.assert_called_once()
        mock_logger.info.assert_called_once_with("Database connection closed.")


def test_close_db_skips_when_closed():
    mock_db = MagicMock(spec=SqliteDatabase)
    mock_db.is_closed.return_value = True

    with patch("database_manager.logger") as mock_logger:
        database_manager.close_db(mock_db)
        mock_db.close.assert_not_called()
        mock_logger.info.assert_not_called()


def test_temp_db_is_sqlite_and_in_memory():
    assert isinstance(database_manager.temp_db, SqliteDatabase)
    assert database_manager.temp_db.database == ":memory:"


def test_main_db_is_sqlite_and_file_based():
    assert isinstance(database_manager.db, SqliteDatabase)
    assert database_manager.db.database == "socialnetwork.db"
