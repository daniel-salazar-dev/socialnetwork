"""
Provides a basic frontend
"""

import atexit
import sys

import database_manager as dbm
import database_utils
import main

# Assign database connection from database manager
active_database = dbm.db
# Initialize fresh user_collection at startup
user_collection = main.init_user_collection()
# Initialize fresh status_collection at startup
status_collection = main.init_status_collection()
# Register close_db to be called when program exits to prevent hanging database connections
atexit.register(lambda: dbm.close_db(active_database))


def load_users():
    """
    Loads user records from a file into the database
    """
    filename = input("\nEnter filename of user file: ").strip()
    while True:
        verify = (
            input(f"Are you sure that you want to import {filename}? (y/n): ")
            .strip()
            .lower()
        )

        if verify in ("y", "yes"):
            new_count, skipped_count = main.load_users(filename, user_collection)
            if new_count == 0 and skipped_count == 0:
                message = f"File '{filename}' not found."
            else:
                message = (
                    f"{filename} imported into the database. {new_count} users loaded."
                )
                # Conditionally include information about skipped users
                if skipped_count > 0:
                    message += f" {skipped_count} users skipped."
            print(message)
            break
        elif verify in ("n", "no"):
            print("Import aborted.")
            break
        else:
            print("Invalid input. Please enter 'y' (yes) or 'n' (no).")


def add_user():
    """
    Adds a new user record to the database
    """
    user_id = input("\nUser ID: ").strip()
    email = input("User email: ").strip()
    user_name = input("User name: ").strip()
    user_last_name = input("User last name: ").strip()
    if not main.add_user(user_id, email, user_name, user_last_name, user_collection):
        print("\nAn error occurred while trying to add new user")
    else:
        print("\nUser was successfully added")


def update_user():
    """
    Updates an existing user record in the database
    """
    user_id = input("\nUser ID: ").strip()
    email = input("User email: ").strip()
    user_name = input("User name: ").strip()
    user_last_name = input("User last name: ").strip()
    if not main.update_user(user_id, email, user_name, user_last_name, user_collection):
        print("An error occurred while trying to update user")
    else:
        print("User was successfully updated")


def search_user():
    """
    Searches for a user record in the database
    """
    user_id = input("\nEnter user ID to search: ").strip()
    result = main.search_user(user_id, True, user_collection)
    if not result.user_name:
        print("ERROR: User does not exist")
    else:
        print(f"User ID: {result.user_id}")
        print(f"Email: {result.user_email}")
        print(f"Name: {result.user_name}")
        print(f"Last name: {result.user_last_name}")


def delete_user():
    """
    Deletes a user record from the database
    """
    user_id = input("\nUser ID: ").strip()
    if not main.delete_user(user_id, user_collection):
        print("An error occurred while trying to delete user")
    else:
        print("User was successfully deleted")


def load_status_updates():
    """
    Loads user status records from a file into the database
    """
    filename = input("\nEnter filename for status file: ").strip()
    while True:
        verify = (
            input(f"Are you sure that you want to import {filename}? (y/n): ")
            .strip()
            .lower()
        )

        if verify in ("y", "yes"):
            new_count, skipped_count = main.load_status_updates(
                filename, status_collection
            )
            if new_count == 0 and skipped_count == 0:
                message = f"File '{filename}' not found."
            else:
                message = f"{new_count} statuses loaded from {filename} successfully."
                # Conditionally include information about skipped statuses
                if skipped_count > 0:
                    message += f" {skipped_count} statuses skipped."
            print(message)
            break
        elif verify in ("n", "no"):
            print("Import aborted.")
            break
        else:
            print("Invalid input. Please enter 'y' (yes) or 'n' (no).")


def add_status():
    """
    Adds a new user status record to the database
    """
    user_id = input("\nUser ID: ").strip()
    status_id = input("Status ID: ").strip()
    status_text = input("Status text: ").strip()
    if not main.add_status(
        status_id, user_id, status_text, status_collection, user_collection
    ):
        print("An error occurred while trying to add new status")
    else:
        print("New status was successfully added")


def update_status():
    """
    Updates an existing user status record in the database
    """
    status_id = input("\nStatus ID: ").strip()
    status_text = input("Status text: ").strip()
    if not main.update_status(status_id, status_text, status_collection):
        print("An error occurred while trying to update status")
    else:
        print("Status was successfully updated")


def search_status():
    """
    Searches for a user status record in the database
    """
    status_id = input("\nEnter status ID to search: ").strip()
    result = main.search_status(status_id, True, status_collection)
    if not result.status_id:
        print("ERROR: Status does not exist")
    else:
        print(f"User ID: {result.user_id}")
        print(f"Status ID: {result.status_id}")
        print(f"Status text: {result.status_text}")


def delete_status():
    """
    Deletes a user status record from the database
    """
    status_id = input("\nStatus ID: ").strip()
    if not main.delete_status(status_id, status_collection):
        print("An error occurred while trying to delete status")
    else:
        print("Status was successfully deleted")


def quit_program():
    """
    Quits program
    """
    sys.exit()


if __name__ == "__main__":
    # Connect to database, verify tables exist, disconnect
    print("\nVerifying database...")
    database_utils.ensure_tables(active_database)
    dbm.close_db(active_database)
    print("Database verified!")

    # Use dictionary to map user input to functions
    menu_options = {
        "A": load_users,
        "B": add_user,
        "C": update_user,
        "D": search_user,
        "E": delete_user,
        "F": load_status_updates,
        "G": add_status,
        "H": update_status,
        "I": search_status,
        "J": delete_status,
        "Q": quit_program,
    }
    # Use 'while True' to keep the menu open until the user makes a selection or chooses to exit
    while True:
        user_selection = input(
            """
                            A: Load user file into database
                            B: Add user
                            C: Update user
                            D: Search user
                            E: Delete user
                            F: Load status file into database
                            G: Add status
                            H: Update status
                            I: Search status
                            J: Delete status
                            Q: Quit

                            Please enter your choice: """
        ).upper()
        if user_selection in menu_options:
            # Open database connection and execute user selection
            dbm.open_db(active_database)
            menu_options[user_selection]()
        else:
            print("Invalid option")

        # Disconnect from database after the selected option is finished
        dbm.close_db(active_database)
