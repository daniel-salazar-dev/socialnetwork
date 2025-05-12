"""
Testing suite for the users file
Patching the logger to avoid writing tests to the log file
"""

# Disabling some noisy linting for peewee
# pylint: disable=E1101,R0801,W0212,W0621

from unittest.mock import patch, MagicMock
from peewee import DatabaseError
import pytest

from database_manager import temp_db
from socialnetwork_model import UsersTable
from users import Users, UserCollection


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """
    Sets up an in-memory database before each test and tears it down after.
    """
    # Bind the model to the test DB and create tables
    UsersTable._meta.database = temp_db
    temp_db.bind([UsersTable], bind_refs=False, bind_backrefs=False)
    temp_db.connect()
    temp_db.create_tables([UsersTable])

    yield  # Run the test

    temp_db.drop_tables([UsersTable])
    temp_db.close()


@pytest.fixture
def user_collection():
    """
    Provides a fresh UserCollection instance for each test.
    """
    return UserCollection()


def generate_test_user():
    """
    Generate a test user in the in-memory database.
    """
    UsersTable.create(
        user_id="u1",
        user_email="email@test.com",
        user_name="Fname",
        user_last_name="Lname",
    )


def test_add_user_success(user_collection):
    result = user_collection.add_user("u1", "email@test.com", "First", "Last")
    assert result is True

    user = UsersTable.get_by_id("u1")
    assert user.user_email == "email@test.com"


def test_add_user_duplicate(user_collection):
    generate_test_user()
    with patch("users.logger.error"):
        result = user_collection.add_user("u1", "email@example.com", "First", "Last")
        assert result is False


def test_add_user_failure(user_collection):
    with patch("users.UsersTable.insert") as mock_insert:
        # Mock the insert to force a DatabaseError
        mock_insert.return_value.execute.side_effect = DatabaseError("DB error")
        with patch(
            "users.UserCollection.search_user",
            return_value=Users(None, None, None, None),
        ):
            with patch("users.logger.error"):
                result = user_collection.add_user(
                    "u1", "email@example.com", "First", "Last"
                )
                assert result is False


@pytest.mark.parametrize(
    "should_find_user, expected, log_level",
    [(True, True, "info"), (False, False, "error")],
)
def test_modify_user(should_find_user, expected, log_level, user_collection):
    log = f"users.logger.{log_level}"
    # Only create a user if the test case expects to find one
    if should_find_user:
        generate_test_user()

    with patch(log):
        result = user_collection.modify_user("u1", "new@email.com", "New", "Name")
        assert result is expected
        if should_find_user:
            updated = UsersTable.get_by_id("u1")
            assert updated.user_email == "new@email.com"
            assert updated.user_name == "New"


def test_modify_user_failure(user_collection):
    generate_test_user()
    # Mock the update to force a DatabaseError
    with patch("users.UsersTable.update") as mock_update:
        mock_update.return_value.where.return_value.execute.side_effect = DatabaseError(
            "DB error"
        )
        with patch("users.logger.error"):
            result = user_collection.modify_user("u1", "new@email.com", "New", "Name")
            assert result is False


@pytest.mark.parametrize(
    "should_find_user, expected, log_level",
    [(True, True, "info"), (False, False, "error")],
)
def test_delete_user(should_find_user, expected, log_level, user_collection):
    log = f"users.logger.{log_level}"
    # Only create a user if the test case expects to find one
    if should_find_user:
        generate_test_user()

    with patch(log):
        result = user_collection.delete_user("u1")
        assert result is expected


def test_delete_user_failure(user_collection):
    with patch("users.UsersTable.get") as mock_get:
        # Simulate that get returns a mock user when called
        mock_user = MagicMock(spec=UsersTable)
        mock_user.user_id = "u1"
        mock_get.return_value = mock_user

        # Simulate DB error when calling delete_instance()
        mock_user.delete_instance.side_effect = DatabaseError("DB error")

        with patch("users.logger.error"):
            # Call the delete_user method and assert it returns False due to DB error
            result = user_collection.delete_user("u1")
            assert result is False


@pytest.mark.parametrize("should_find_user", (True, False))
def test_search_user(should_find_user, user_collection):
    # Only create a user if the test case expects to find one
    if should_find_user:
        generate_test_user()

    with patch("users.logger.info"):
        result = user_collection.search_user("u1", log=True)
        assert isinstance(result, Users)
        if should_find_user:
            assert result.user_id == "u1"
            assert result.user_email == "email@test.com"
            assert result.user_name == "Fname"
            assert result.user_last_name == "Lname"
        else:
            assert result.user_id is None
