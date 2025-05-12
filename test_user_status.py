"""
Testing suite for the user_status file
Patching the logger to avoid writing tests to the log file
"""

# Disabling some noisy linting for peewee
# pylint: disable=E1101,,R0801,W0212,W0613,W0621

from unittest.mock import patch, MagicMock
from peewee import DatabaseError
import pytest

from database_manager import temp_db
from socialnetwork_model import UserStatusTable, UsersTable
from user_status import UserStatusCollection, UserStatus


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """
    Sets up an in-memory database before each test and tears it down after.
    """
    UsersTable._meta.database = temp_db
    UserStatusTable._meta.database = temp_db
    temp_db.bind([UsersTable, UserStatusTable], bind_refs=False, bind_backrefs=False)
    temp_db.connect()
    temp_db.create_tables([UsersTable, UserStatusTable])

    yield

    temp_db.drop_tables([UsersTable, UserStatusTable])
    temp_db.close()


@pytest.fixture
def user_status_collection():
    return UserStatusCollection()


def generate_test_user():
    UsersTable.create(
        user_id="u1",
        user_email="email@test.com",
        user_name="Fname",
        user_last_name="Lname",
    )


def generate_test_status():
    generate_test_user()
    UserStatusTable.create(status_id="s1", status_text="Hello", user_id="u1")


def test_add_status_success(user_status_collection):
    generate_test_user()
    result = user_status_collection.add_status("s1", "u1", "Status message")
    assert result is True

    saved = UserStatusTable.get_by_id("s1")
    assert saved.status_text == "Status message"
    # Foreign keys in peewee create a nested model object, UsersTable in this case
    assert saved.user_id == UsersTable.get_by_id("u1")


def test_add_status_duplicate(user_status_collection):
    generate_test_user()
    UserStatusTable.create(status_id="s1", user_id="u1", status_text="Old status")

    with patch("users.logger.error"):
        result = user_status_collection.add_status("s1", "u1", "New message")
        assert result is False


def test_add_status_failure(user_status_collection):
    with patch("user_status.UserStatusTable.insert") as mock_insert:
        mock_insert.return_value.execute.side_effect = DatabaseError("DB error")
        with patch("users.logger.error"):
            result = user_status_collection.add_status("s1", "u1", "Message")
            assert result is False


def test_modify_status_success(user_status_collection):
    generate_test_status()
    with patch("users.logger.info"):
        result = user_status_collection.modify_status("s1", "Updated message")
        assert result is True

        updated = UserStatusTable.get_by_id("s1")
        assert updated.status_text == "Updated message"


def test_modify_status_not_found(user_status_collection):
    with patch("users.logger.error"):
        result = user_status_collection.modify_status("s999", "Doesn't exist")
        assert result is False


def test_modify_status_failure(user_status_collection):
    generate_test_status()
    with patch("user_status.UserStatusTable.update") as mock_update:
        mock_update.return_value.where.return_value.execute.side_effect = DatabaseError(
            "DB error"
        )

        with patch("users.logger.error"):
            result = user_status_collection.modify_status("s1", "Failed")
            assert result is False


def test_delete_status_success(user_status_collection):
    generate_test_status()
    with patch("users.logger.info"):
        result = user_status_collection.delete_status("s1")
        assert result is True
        assert (
            UserStatusTable.select().where(UserStatusTable.status_id == "s1").count()
            == 0
        )


def test_delete_status_not_found(user_status_collection):
    with patch("users.logger.error"):
        result = user_status_collection.delete_status("missing")
        assert result is False


def test_delete_status_failure(user_status_collection):
    generate_test_status()
    with patch("user_status.UserStatusTable.get") as mock_get:
        # Simulate that get returns a mock status  when called
        mock_user = MagicMock(spec=UserStatusTable)
        mock_user.status_id = "s1"
        mock_get.return_value = mock_user

        # Simulate DB error when calling delete_instance()
        mock_user.delete_instance.side_effect = DatabaseError("DB error")

        with patch("users.logger.error"):
            # Call the delete_user method and assert it returns False due to DB error
            result = user_status_collection.delete_status("u1")
            assert result is False


def test_search_status_found(user_status_collection):
    generate_test_status()
    with patch("users.logger.info"):
        result = user_status_collection.search_status("s1", log=True)
        assert isinstance(result, UserStatus)
        assert result.status_id == "s1"
        assert result.status_text == "Hello"
        # Foreign keys in peewee create a nested model object, UsersTable in this case
        assert result.user_id == UsersTable.get_by_id("u1")


def test_search_status_not_found(user_status_collection):
    with patch("users.logger.info"):
        result = user_status_collection.search_status("missing", log=True)
        assert isinstance(result, UserStatus)
        assert result.status_id is None
