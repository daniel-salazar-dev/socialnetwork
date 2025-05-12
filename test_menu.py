"""
Testing suite for the menu
Using fixtures to simulate user input
Patching the logger to avoid writing tests to the log file
"""

# pylint: disable=W0621

from unittest import mock
from unittest.mock import patch

import pytest

import menu


@pytest.fixture
def mock_user_data():
    return ("u1", "user@example.com", "First", "Last")


@pytest.fixture
def mock_status_data():
    return ("s1", "u1", "Test status")


def test_add_user(monkeypatch, mock_user_data):
    inputs = iter(mock_user_data)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with mock.patch("main.add_user", return_value=True) as mock_add:
        with patch("users.logger.info"):
            menu.add_user()
            mock_add.assert_called_once_with(*mock_user_data, menu.user_collection)


def test_update_user(monkeypatch, mock_user_data):
    inputs = iter(mock_user_data)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with mock.patch("main.update_user", return_value=True) as mock_update:
        with patch("users.logger.info"):
            menu.update_user()
            mock_update.assert_called_once_with(*mock_user_data, menu.user_collection)


def test_delete_user(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "u1")
    with mock.patch("main.delete_user", return_value=True) as mock_delete:
        with patch("users.logger.info"):
            menu.delete_user()
            mock_delete.assert_called_once_with("u1", menu.user_collection)


def test_search_user_found(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "u1")
    mock_user = mock.Mock(
        user_id="u1", user_email="e", user_name="n", user_last_name="ln"
    )
    with mock.patch("main.search_user", return_value=mock_user):
        with patch("users.logger.info"):
            menu.search_user()


def test_search_user_not_found(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "u1")
    mock_user = mock.Mock(user_name="")
    with mock.patch("main.search_user", return_value=mock_user):
        with patch("users.logger.info"):
            menu.search_user()


def test_add_status(monkeypatch, mock_status_data):
    inputs = iter([mock_status_data[1], mock_status_data[0], mock_status_data[2]])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with mock.patch("main.add_status", return_value=True) as mock_add:
        with patch("users.logger.info"):
            menu.add_status()
            mock_add.assert_called_once_with(
                mock_status_data[0],
                mock_status_data[1],
                mock_status_data[2],
                menu.status_collection,
                menu.user_collection,
            )


def test_update_status(monkeypatch):
    inputs = iter(["s1", "new status text"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with mock.patch("main.update_status", return_value=True) as mock_update:
        with patch("users.logger.info"):
            menu.update_status()
            mock_update.assert_called_once_with(
                "s1", "new status text", menu.status_collection
            )


def test_delete_status(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "s1")
    with mock.patch("main.delete_status", return_value=True) as mock_delete:
        with patch("users.logger.info"):
            menu.delete_status()
            mock_delete.assert_called_once_with("s1", menu.status_collection)


def test_search_status_found(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "s1")
    mock_status = mock.Mock(status_id="s1", user_id="u1", status_text="Text")
    with mock.patch("main.search_status", return_value=mock_status):
        with patch("users.logger.info"):
            menu.search_status()


def test_search_status_not_found(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "s1")
    mock_status = mock.Mock(status_id="")
    with mock.patch("main.search_status", return_value=mock_status):
        with patch("users.logger.info"):
            menu.search_status()


def test_load_users_yes(monkeypatch):
    inputs = iter(["test.csv", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with mock.patch("main.load_users", return_value=(2, 1)):
        with patch("users.logger.info"):
            menu.load_users()


def test_load_users_no(monkeypatch):
    inputs = iter(["test.csv", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    menu.load_users()


def test_load_status_updates_yes(monkeypatch):
    inputs = iter(["status.csv", "yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with mock.patch("main.load_status_updates", return_value=(1, 0)):
        with patch("users.logger.info"):
            menu.load_status_updates()


def test_load_status_updates_no(monkeypatch):
    inputs = iter(["status.csv", "no"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    menu.load_status_updates()
