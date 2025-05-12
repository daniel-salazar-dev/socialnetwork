"""
Data models for local database
Using peewee for a simple, lightweight database library
Modeling documentation available at: https://docs.peewee-orm.com/en/latest/peewee/models.html
"""

from peewee import Model, CharField, ForeignKeyField

from database_manager import db


# Create base scaffolding for tables to inherit from
class BaseModel(Model):
    class Meta:
        database = db


class UsersTable(BaseModel):
    user_email = CharField(max_length=1000)
    user_id = CharField(primary_key=True, max_length=30)
    user_last_name = CharField(max_length=100)
    user_name = CharField(max_length=30)


class UserStatusTable(BaseModel):
    status_id = CharField(primary_key=True)
    status_text = CharField(max_length=1000)
    user_id = ForeignKeyField(
        UsersTable, backref="statuses", column_name="user_id", on_delete="CASCADE"
    )
