"""
Classes to manage the user status messages
"""

# Disabling some noisy linting for peewee UserStatusTable references
# pylint: disable=E1120

from peewee import DatabaseError, DoesNotExist

from log_helper import logger
from socialnetwork_model import UserStatusTable


class UserStatus:
    """
    Class to hold status message data
    """

    def __init__(self, status_id, user_id, status_text):
        self.status_id = status_id
        self.user_id = user_id
        self.status_text = status_text


class UserStatusCollection:
    """
    Collection of UserStatus messages
    """

    def __init__(self):
        self.database = {}

    def add_status(self, status_id: str, user_id: str, status_text: str) -> bool:
        """
        Add a new status message to the collection
        """
        # Lookup status and fail if status already exists
        lookup = self.search_status(status_id, False)
        if lookup.status_id:
            logger.error(f"Add status failed: status_id '{status_id}' already exists.")
            return False

        try:
            UserStatusTable.insert(
                status_id=status_id, status_text=status_text, user_id=user_id
            ).execute()
            return True
        except DatabaseError as e:
            logger.error(f"Failed to save status '{status_id}': {e}")
            return False

    def modify_status(self, status_id: str, status_text: str) -> bool:
        """
        Modifies a status message
        Do not allow statuses to move between users
        """
        # Lookup status and fail if no user is found
        lookup = self.search_status(status_id, False)
        if not lookup.status_id:
            logger.error(
                f"Modify status failed: status_id '{status_id}' does not exist."
            )
            return False

        try:
            UserStatusTable.update(status_text=status_text).where(
                UserStatusTable.status_id == status_id
            ).execute()
            logger.info(f"Status '{status_id}' modified successfully.")
            return True
        except DatabaseError as e:
            logger.error(f"Failed to update status '{status_id}': {e}")
            return False

    def delete_status(self, status_id: str) -> bool:
        """
        Deletes a status message
        """
        # Lookup status and fail if no user is found
        lookup = self.search_status(status_id, False)
        if not lookup.status_id:
            logger.error(
                f"Delete status failed: status_id '{status_id}' does not exist."
            )
            return False

        try:
            UserStatusTable.get(
                UserStatusTable.status_id == status_id
            ).delete_instance()
            logger.info(f"User '{status_id}' deleted successfully.")
            return True
        except DatabaseError as e:
            logger.error(f"Failed to delete user '{status_id}': {e}")
            return False

    def search_status(self, status_id: str, log: bool) -> UserStatus:
        """
        Find and return a status message by its status_id
        Returns an empty UserStatus object if status_id does not exist
        """
        try:
            result = UserStatusTable.get(UserStatusTable.status_id == status_id)
            if log:
                logger.info(f"Search status: status_id '{status_id}' found.")
            return UserStatus(result.status_id, result.user_id, result.status_text)
        except DoesNotExist:
            if log:
                logger.info(f"Search status: status_id '{status_id}' not found.")
            return UserStatus(None, None, None)
