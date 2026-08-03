"""
app/services/contact_logic_handler.py: Rules for creating and managing contacts

Contact create, list, view, update, and delete rules for YourCont live here so request handlers stay thin.
Every action takes the signed in user id so one account only works with its own contacts.
ContactValidator checks fields, then ContactDatabaseHandlerRds runs the SQL.
ContactRequestHandler turns the True or False results into page redirects and flash messages.
"""

from app.services.contact_database_handler import ContactDatabaseHandlerRds
from app.services.contact_validator import ContactValidator


class ContactLogicHandler:

    """
    Contact rules used by ContactRequestHandler when someone manages their list.
    """

    def __init__(self, contact_db=None, validator=None):

        """
        Attaches the contacts table helper and field checks.
        Different helpers can be passed in later for tests without needing a live database.
        """

        self.contact_db = contact_db or ContactDatabaseHandlerRds()
        self.validator = validator or ContactValidator()

    def process_create(self, user_id, form_data):

        """
        Validates and inserts a new contact owned by user_id.

        First name must pass ContactValidator.
        The cleaned values then go into Postgres through ContactDatabaseHandlerRds.
        Returns True with the new Contact and a Contact Created message,
        or False with an error message when the form is not valid.
        """

        ok, message, cleaned = self.validator.validate_fields(
            first_name=form_data.get("first_name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            address=form_data.get("address"),
            birthday=form_data.get("birthday"),
            relationship=form_data.get("relationship"),
            notes=form_data.get("notes"),
        )

        if not ok:
            return False, message, None

        contact = self.contact_db.insert_contact(user_id=user_id, **cleaned)

        return True, "Contact Created", contact

    def process_list(self, user_id):

        """
        Returns the contact list for the signed in user only.

        Other accounts' rows never appear here because the database query filters on user_id.
        """

        return self.contact_db.select_contacts_for_user(user_id)

    def process_get(self, contact_id, user_id):

        """
        Returns one owned contact, or None when it is missing or belongs to someone else.

        Detail, edit, and delete all use this check before showing or changing a row.
        """

        return self.contact_db.select_contact_for_user(contact_id, user_id)

    def process_update(self, contact_id, user_id, form_data):

        """
        Validates and updates one contact from this user's list.

        I first confirm the row belongs to this user,
        then run the same field checks as create,
        then save through ContactDatabaseHandlerRds.
        Returns True with Contact Updated, or False when the form fails or the row is not found.
        """

        existing = self.contact_db.select_contact_for_user(contact_id, user_id)

        if not existing:
            return False, "Contact not found.", None

        ok, message, cleaned = self.validator.validate_fields(
            first_name=form_data.get("first_name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            address=form_data.get("address"),
            birthday=form_data.get("birthday"),
            relationship=form_data.get("relationship"),
            notes=form_data.get("notes"),
        )

        if not ok:
            return False, message, None

        contact = self.contact_db.update_contact_for_user(
            contact_id=contact_id,
            user_id=user_id,
            **cleaned,
        )

        if not contact:
            return False, "Contact not found.", None

        return True, "Contact Updated", contact

    def process_delete(self, contact_id, user_id):

        """
        Deletes one contact from this user's list.

        The SQL only removes a row when both contact id and user id match,
        so a guessed URL cannot delete someone else's contact.
        Returns True with Contact Deleted, or False when nothing matched that user.
        """

        deleted = self.contact_db.delete_contact_for_user(contact_id, user_id)

        if not deleted:
            return False, "Contact not found."

        return True, "Contact Deleted"
