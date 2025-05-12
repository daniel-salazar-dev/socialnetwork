"""
Testing suite for the main backend file
Patching the logger to avoid writing tests to the log file
"""

# pylint: disable=E1101,W0212,W0621

import tempfile
import csv
import os
from unittest.mock import patch

import pytest

from database_manager import temp_db
from main import (
    init_user_collection,
    init_status_collection,
    load_users,
    load_status_updates,
    add_user,
    update_user,
    delete_user,
    search_user,
    add_status,
    update_status,
    delete_status,
    search_status,
)
from socialnetwork_model import UsersTable, UserStatusTable


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    UsersTable._meta.database = temp_db
    UserStatusTable._meta.database = temp_db
    temp_db.bind([UsersTable, UserStatusTable], bind_refs=False, bind_backrefs=False)
    temp_db.connect()
    temp_db.create_tables([UsersTable, UserStatusTable])
    yield
    temp_db.drop_tables([UsersTable, UserStatusTable])
    temp_db.close()


@pytest.fixture
def user_collection():
    return init_user_collection()


@pytest.fixture
def status_collection():
    return init_status_collection()


def create_temp_csv(headers, rows):
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as tmp:
        writer = csv.DictWriter(tmp, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_load_users_success(user_collection):
    path = create_temp_csv(
        ["USER_ID", "NAME", "LASTNAME", "EMAIL"],
        [
            {
                "USER_ID": "u1",
                "NAME": "First",
                "LASTNAME": "Last",
                "EMAIL": "e@test.com",
            }
        ],
    )
    result = load_users(path, user_collection)
    assert result == (1, 0)
    os.remove(path)


def test_load_users_failure(user_collection):
    path = create_temp_csv(
        ["COLUMN1", "COLUMN2", "COLUMN3", "COLUMN4"],
        [
            {
                "COLUMN1": "u1",
                "COLUMN2": "First",
                "COLUMN3": "Last",
                "COLUMN4": "e@test.com",
            }
        ],
    )
    with patch("users.logger.error"):
        result = load_users(path, user_collection)
        assert result is None
        os.remove(path)


def test_add_update_delete_user(user_collection):
    with patch("users.logger.info"):
        assert add_user("u1", "e@test.com", "First", "Last", user_collection) is True
        assert update_user("u1", "new@test.com", "F", "L", user_collection) is True
        assert delete_user("u1", user_collection) is True


def test_search_user(user_collection):
    with patch("users.logger.info"):
        add_user("u1", "e@test.com", "First", "Last", user_collection)
        result = search_user("u1", False, user_collection)
        assert result.user_id == "u1"


def test_load_status_updates_success(user_collection, status_collection):
    with patch("users.logger.info"):
        add_user("u1", "e@test.com", "First", "Last", user_collection)
        path = create_temp_csv(
            ["COLUMN1", "COLUMN2", "COLUMN3"],
            [{"COLUMN1": "s1", "COLUMN2": "u1", "COLUMN3": "hello"}],
        )
        result = load_status_updates(path, status_collection)
        assert result is None
        os.remove(path)


def test_load_status_updates_failure(user_collection, status_collection):
    with patch("users.logger"):
        add_user("u1", "e@test.com", "First", "Last", user_collection)
        path = create_temp_csv(
            ["COLUMN1", "COLUMN2", "COLUMN3"],
            [{"COLUMN1": "s1", "COLUMN2": "u1", "COLUMN3": "hello"}],
        )
        result = load_status_updates(path, status_collection)
        assert result is None
        os.remove(path)


def test_add_update_delete_status(user_collection, status_collection):
    with patch("users.logger.info"):
        add_user("u1", "e@test.com", "First", "Last", user_collection)
        assert (
            add_status("s1", "u1", "hello", status_collection, user_collection) is True
        )
        assert update_status("s1", "updated", status_collection) is True
        assert delete_status("s1", status_collection) is True


def test_search_status(user_collection, status_collection):
    with patch("users.logger.info"):
        add_user("u1", "e@test.com", "First", "Last", user_collection)
        add_status("s1", "u1", "hello", status_collection, user_collection)
        result = search_status("s1", False, status_collection)
        assert result.status_id == "s1"
