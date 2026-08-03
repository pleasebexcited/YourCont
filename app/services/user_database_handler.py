"""
app/services/user_database_handler.py: Saves and finds user accounts in the database

SQL for the YourCont users table lives in this class.
The Rds name matches my class diagram and the plan to point the same code at AWS RDS later.
For now it uses local Postgres through DATABASE_URL and app/db.py.
AuthLogicHandler calls these methods during sign up and log in.
"""

from app.db import get_connection
from app.models.user import User


class UserDatabaseHandlerRds:

    """
    Reads and writes YourCont account rows in Postgres.
    """

    def insert_user(self, first_name, last_name, email, password_hash):

        """
        Inserts a new account and returns it as a User.

        RETURNING gives me the new row straight after sign up so I do not need a second query.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s,
                    %s) RETURNING user_id, first_name, last_name, email, password_hash;
                    """,
                    (first_name, last_name, email, password_hash),
                )
                row = cursor.fetchone()
            connection.commit()

        return User.from_row(row)

    def select_user_by_email(self, email):

        """
        Finds one account by email for log in and for duplicate sign up checks.

        lower() on both sides means Jane@Example.com and jane@example.com match the same row.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id, first_name, last_name, email,
                    password_hash FROM users WHERE lower(email) = lower(%s);
                    """,
                    (email,),
                )
                row = cursor.fetchone()

        if not row:
            return None

        return User.from_row(row)

    def select_user_by_id(self, user_id):

        """
        Finds one account by primary key when I already know the session user id.

        Contact ownership already uses contacts.user_id in the contacts queries.
        I keep this method for looking up an account by id, for example if I later re check that the signed in user still exists in Postgres.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id, first_name, last_name, email, password_hash FROM users WHERE user_id = %s;
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()

        if not row:
            return None

        return User.from_row(row)
