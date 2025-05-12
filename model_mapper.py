from enum import Enum


# Class for mapping UsersTable to accounts.csv
class AccountFields(Enum):
    USER_ID = "user_id"
    EMAIL = "email"
    USER_NAME = "name"
    USER_LAST_NAME = "lastname"


# Class for mapping UserStatusTable to status_updates.csv
class StatusFields(Enum):
    STATUS_ID = "status_id"
    USER_ID = "user_id"
    STATUS_TEXT = "status_text"
