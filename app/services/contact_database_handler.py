"""
app/services/contact_database_handler.py: Saves and finds contacts in the database

SQL for the YourCont contacts table lives in this class.
The Rds name matches my class diagram and the plan to point the same code at AWS RDS later.
For now it uses my local Postgres through DATABASE_URL and app/db.py.
Every query includes user_id so one account only sees and changes its own contacts.
ContactLogicHandler calls these methods during create, list, view, update, and delete.
"""

from app.db import get_connection
from app.models.contact import Contact


class ContactDatabaseHandlerRds:

    """
    Reads and writes YourCont contact rows in Postgres for one owning user at a time.
    """

    def insert_contact(
        self,
        user_id,
        first_name,
        last_name,
        email,
        phone,
        address,
        birthday,
        relationship,
        notes,
        profile_image_key=None,
    ):

        """
        Inserts a new contact owned by user_id and returns it as a Contact.

        RETURNING gives me the new row straight away so ContactRequestHandler can redirect or flash without a second query.
        profile_image_key stores the private S3 object key when a photo was uploaded.
        I save the key instead of a full website link so the photo can stay private in S3,
        and YourCont can build a short lived URL later whenever someone opens the contact.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO contacts (
                        user_id, first_name, last_name, email, phone, address,
                        birthday, relationship, notes, profile_image_key
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING contact_id, user_id, first_name, last_name, email, phone,
                              address, birthday, relationship, notes, profile_image_key;
                    """,
                    (
                        user_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        address,
                        birthday,
                        relationship,
                        notes,
                        profile_image_key,
                    ),
                )
                row = cursor.fetchone()
            connection.commit()

        return Contact.from_row(row)

    def select_contacts_for_user(self, user_id):

        """
        Returns every contact owned by user_id, newest first for a simple list order.

        The WHERE user_id filter is what keeps another person's contacts off this list.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT contact_id, user_id, first_name, last_name, email, phone,
                           address, birthday, relationship, notes, profile_image_key
                    FROM contacts
                    WHERE user_id = %s
                    ORDER BY contact_id DESC;
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()

        return [Contact.from_row(row) for row in rows]

    def select_contact_for_user(self, contact_id, user_id):

        """
        Finds one contact by id only when it belongs to user_id.

        A miss returns None so the handler can treat missing and other people's contacts the same way.
        That stops a guessed /contacts/1 style URL from showing data owned by someone else.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT contact_id, user_id, first_name, last_name, email, phone,
                           address, birthday, relationship, notes, profile_image_key
                    FROM contacts
                    WHERE contact_id = %s AND user_id = %s;
                    """,
                    (contact_id, user_id),
                )
                row = cursor.fetchone()

        if not row:
            return None

        return Contact.from_row(row)

    def update_contact_for_user(
        self,
        contact_id,
        user_id,
        first_name,
        last_name,
        email,
        phone,
        address,
        birthday,
        relationship,
        notes,
        profile_image_key=None,
    ):

        """
        Updates one owned contact and returns the fresh Contact,
        or None when the row is not found for that user.

        The WHERE clause needs both contact id and user id,
        so an edit post cannot change another account's row.
        profile_image_key is updated when ContactLogicHandler replaces or keeps the S3 photo key so an edit with a new photo points at the new file,
        and an edit with no new photo keeps the same picture on the contact.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE contacts
                    SET first_name = %s,
                        last_name = %s,
                        email = %s,
                        phone = %s,
                        address = %s,
                        birthday = %s,
                        relationship = %s,
                        notes = %s,
                        profile_image_key = %s
                    WHERE contact_id = %s AND user_id = %s
                    RETURNING contact_id, user_id, first_name, last_name, email, phone,
                              address, birthday, relationship, notes, profile_image_key;
                    """,
                    (
                        first_name,
                        last_name,
                        email,
                        phone,
                        address,
                        birthday,
                        relationship,
                        notes,
                        profile_image_key,
                        contact_id,
                        user_id,
                    ),
                )
                row = cursor.fetchone()
            connection.commit()

        if not row:
            return None

        return Contact.from_row(row)

    def delete_contact_for_user(self, contact_id, user_id):

        """
        Deletes one owned contact.

        Returns True when a row was removed, False when nothing matched that user.
        Both ids must match before Postgres deletes anything.
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM contacts
                    WHERE contact_id = %s AND user_id = %s
                    RETURNING contact_id;
                    """,
                    (contact_id, user_id),
                )
                row = cursor.fetchone()
            connection.commit()

        return row is not None
