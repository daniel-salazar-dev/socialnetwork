"""
Classes for user information for the social network project
"""

# Disabling some noisy linting for peewee UserTable references
# pylint: disable=E1120

from peewee import DatabaseError, DoesNotExist

from log_helper import logger
from socialnetwork_model import UsersTable


class Users:
    """
    Contains user information
    """

    def __init__(self, user_id, email, user_name, user_last_name):
        self.user_id = user_id
        self.user_email = email
        self.user_name = user_name
        self.user_last_name = user_last_name


class UserCollection:
    """
    Contains a collection of Users objects
    """

    def add_user(
        self, user_id: str, email: str, user_name: str, user_last_name: str
    ) -> bool:
        """
        Adds a new user to the database
        """
        # Lookup user and fail if user already exists
        lookup = self.search_user(user_id, False)
        if lookup.user_id:
            logger.error(f"Add user failed: user_id '{user_id}' already exists.")
            return False

        try:
            UsersTable.insert(
                user_email=email,
                user_id=user_id,
                user_last_name=user_last_name,
                user_name=user_name,
            ).execute()
            return True
        except DatabaseError as e:
            logger.error(f"Failed to save user '{user_id}': {e}")
            return False

    def modify_user(
        self, user_id: str, email: str, user_name: str, user_last_name: str
    ) -> bool:
        """
        Modifies an existing user
        """
        # Lookup user and fail if no user is found
        lookup = self.search_user(user_id, False)
        if not lookup.user_id:
            logger.error(f"Modify user failed: user_id '{user_id}' does not exist.")
            return False

        try:
            UsersTable.update(
                user_email=email,
                user_last_name=user_last_name,
                user_name=user_name,
            ).where(UsersTable.user_id == user_id).execute()
            logger.info(f"User '{user_id}' modified successfully.")
            return True
        except DatabaseError as e:
            logger.error(f"Failed to update user '{user_id}': {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        Deletes an existing user
        """
        # Lookup user and fail if no user is found
        lookup = self.search_user(user_id, False)
        if not lookup.user_id:
            logger.error(f"Delete user failed: user_id '{user_id}' does not exist.")
            return False

        try:
            UsersTable.get(UsersTable.user_id == user_id).delete_instance()
            logger.info(f"User '{user_id}' deleted successfully.")
            return True
        except DatabaseError as e:
            logger.error(f"Failed to delete user '{user_id}': {e}")
            return False

    def search_user(self, user_id: str, log: bool) -> Users:
        """
        Searches for a user
        Returns an empty Users object if user_id does not exist
        """
        try:
            result = UsersTable.get(UsersTable.user_id == user_id)
            if log:
                logger.info(f"Search user: user_id '{user_id}' found.")
            return Users(
                result.user_id,
                result.user_email,
                result.user_name,
                result.user_last_name,
            )
        except DoesNotExist:
            if log:
                logger.info(f"Search user: user_id '{user_id}' not found.")
            return Users(None, None, None, None)
