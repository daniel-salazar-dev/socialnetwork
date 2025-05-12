# Introduction

This started as a homework assignment for a course at the University of Washington. It is a simple program to allow you to upload a CSV file to a local SQLite database using the peewee library. The data modeling is meant to simulate a social media database (users post statuses that can be viewed, updated, deleted). I've included type hints even though they are not enforced in Python. They are very useful for static analysis tools, various IDE features, documentation, and readability. The functions and tests are written in a few different ways to illustrate some approaches that can be taken. Hopefully the notes and flow of the program make it easy for you to follow.

# Files

accounts.csv and status_updates.csv can be used to test the import process