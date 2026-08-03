"""
app/db.py: Opens the database connection for YourCont

Postgres access for YourCont is centralised here.
Handlers and scripts share one DATABASE_URL from .env and the same row format,
so when I move from local Postgres to AWS RDS I only change the connection string,
not every query class.
"""

import os

import psycopg
from psycopg.rows import dict_row


def get_connection():

    """
    Opens a Postgres connection using DATABASE_URL from my .env file.

    dict_row makes each result a dictionary keyed by column name, for example email or first_name,
    instead of a plain list of values.
    User.from_row can then read row["email"] clearly,
    which matches my users table and class diagram better than remembering column positions.
    UserDatabaseHandlerRds uses this connection for every account query.
    ContactDatabaseHandlerRds uses the same helper for every contact query.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:

        # Raising here gives a clear flash friendly message instead of a vague connection error later.

        raise RuntimeError(
            "DATABASE_URL is missing. Add your local Postgres URL to the .env file."
        )

    # row_factory=dict_row applies named columns to every query on this connection.

    return psycopg.connect(database_url, row_factory=dict_row)

def init_schema():

    """
    Creates the users and contacts tables if they are missing.

    scripts/init_db.py calls this after Postgres is installed so sign up and contact saves have somewhere to store rows.
    IF NOT EXISTS lets me rerun the script safely without wiping data.
    contacts.user_id links each contact to the account that owns it,
    so one person cannot see another person's list.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users ( user_id SERIAL PRIMARY KEY, first_name TEXT NOT NULL,
                last_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts ( contact_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, first_name TEXT NOT NULL,
                last_name TEXT, email TEXT, phone TEXT, address TEXT, birthday DATE, relationship TEXT, notes TEXT,
                profile_image_key TEXT );
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS contacts_user_id_idx ON contacts(user_id);
                """
            )
        connection.commit()
