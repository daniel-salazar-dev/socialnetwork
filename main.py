"""
Backend for a simple social network project
"""

# Disabling some noisy linting for peewee _meta references
# pylint: disable=W0212, E1101

import csv
from database_manager import db
from model_mapper import AccountFields, StatusFields
from log_helper import logger
from user_status import UserStatusCollection, UserStatus
from users import UserCollection, Users


# initialize a new UserCollection
def init_user_collection():
    return UserCollection()


# initialize a new UserStatusCollection
def init_status_collection():
    return UserStatusCollection()


def load_users(
    filename: str, user_collection: UserCollection
) -> tuple[int, int] | None:
    """
    Loads users from a csv file into an instance of user_collection
    """
    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            # Collect count of imported rows and skipped rows for logging/output
            new_count = 0
            skipped_count = 0
            # Use a transaction so that the entire batch will rollback if any fail
            with db.transaction():
                for row in reader:
                    row = {key.lower(): value for key, value in row.items()}

                    # Use AccountFields enum for mapping csv to data model columns
                    if not all(row.get(field.value) for field in AccountFields):
                        logger.error(f"Incomplete data in row: {row}")
                        return None

                    user_id = row[AccountFields.USER_ID.value]
                    email = row[AccountFields.EMAIL.value]
                    user_name = row[AccountFields.USER_NAME.value]
                    user_last_name = row[AccountFields.USER_LAST_NAME.value]

                    if user_collection.add_user(
                        user_id, email, user_name, user_last_name
                    ):
                        new_count += 1
                    else:
                        skipped_count += 1

        message = f"{new_count} users loaded from '{filename}' successfully."
        # Conditionally include information about skipped users
        if skipped_count > 0:
            message += f" {skipped_count} users skipped."
        logger.info(message)
        return new_count, skipped_count

    except FileNotFoundError:
        logger.error(f"File not found: '{filename}'")
        return 0, 0


def add_user(
    user_id: str,
    email: str,
    user_name: str,
    user_last_name: str,
    user_collection: UserCollection,
) -> bool:
    return user_collection.add_user(user_id, email, user_name, user_last_name)


def update_user(
    user_id: str,
    email: str,
    user_name: str,
    user_last_name: str,
    user_collection: UserCollection,
) -> bool:
    return user_collection.modify_user(user_id, email, user_name, user_last_name)


def delete_user(user_id: str, user_collection: UserCollection) -> bool:
    return user_collection.delete_user(user_id)


def search_user(user_id: str, log: bool, user_collection: UserCollection) -> Users:
    return user_collection.search_user(user_id, log)


def load_status_updates(
    filename: str, status_collection: UserStatusCollection
) -> tuple[int, int] | None:
    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            # Collect count of imported rows and skipped rows for logging/output
            new_count = 0
            skipped_count = 0
            # Use a transaction so that the entire batch will rollback if any fail
            with db.transaction():
                for row in reader:
                    row = {key.lower(): value for key, value in row.items()}

                    # Use StatusFields enum for mapping csv to data model columns
                    if not all(row.get(field.value) for field in StatusFields):
                        logger.error(f"Incomplete data in row: {row}")
                        return None

                    status_id = row[StatusFields.STATUS_ID.value]
                    user_id = row[StatusFields.USER_ID.value]
                    status_text = row[StatusFields.STATUS_TEXT.value]

                    if status_collection.add_status(status_id, user_id, status_text):
                        new_count += 1
                    else:
                        skipped_count += 1

        message = f"{new_count} statuses loaded from '{filename}' successfully."
        # Conditionally include information about skipped statuses
        if skipped_count > 0:
            message += f" {skipped_count} statuses skipped."
        logger.info(message)
        return new_count, skipped_count

    except FileNotFoundError:
        logger.error(f"File not found: '{filename}'")
        return 0, 0


def add_status(
    status_id: str,
    user_id: str,
    status_text: str,
    status_collection: UserStatusCollection,
    user_collection: UserCollection,
) -> bool:
    # Check if valid user was provided before attempting to add status
    user = search_user(user_id, False, user_collection)
    if not user.user_id:
        logger.error(f"Cannot add status because user '{user_id}' does not exist.")
        return False
    return status_collection.add_status(status_id, user_id, status_text)


def update_status(
    status_id: str,
    status_text: str,
    status_collection: UserStatusCollection,
) -> bool:
    return status_collection.modify_status(status_id, status_text)


def delete_status(status_id: str, status_collection: UserStatusCollection) -> bool:
    return status_collection.delete_status(status_id)


def search_status(
    status_id: str, log: bool, status_collection: UserStatusCollection
) -> UserStatus:
    return status_collection.search_status(status_id, log)
