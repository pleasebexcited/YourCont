"""
app/models/user.py: Holds one user account in memory

User holds the details for one YourCont account in memory (user id, names, email, and password hash).
These values come from the users table in Postgres Database.
I use a User class instead of a loose dictionary so the rest of the app can read clear names like user.email.
UserDatabaseHandlerRds builds a User after a database queryy.
AuthLogicHandler then uses that User when checking a log in or creating a session.
This file only stores account fields.
It does not talk to the browser or run SQL itself.
This keeps account data separate from a single web request, which matches the models layer on my class diagram.
"""

class User:
    """
    One account as used when registering, signing in, or reading the users table.
    """

    def __init__(self, user_id, first_name, last_name, email, password_hash):
        """
        Holds the fields that match a users table row.
        """

        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        # Only the hash is kept here. The original password is never stored on this object.
        self.password_hash = password_hash

    @classmethod
    def from_row(cls, row):
        """
        Builds a User from a Postgres dictionary row returned by app/db.py.
        """

        return cls(
            user_id=row["user_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            password_hash=row["password_hash"],
        )
