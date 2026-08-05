"""
app/services/contact_logic_handler.py: Rules for creating and managing contacts

Contact create, list, view, update, and delete rules for YourCont live here so request handlers stay thin.
Every action takes the signed in user id so one account only works with its own contacts.
ContactValidator checks fields and photos, ContactDatabaseHandlerRds runs the SQL,
and ImageStorageHandler talks to S3 for profile images.
ContactRequestHandler turns the True or False results into page redirects and flash messages.
"""

from app.services.contact_database_handler import ContactDatabaseHandlerRds
from app.services.contact_validator import ContactValidator
from app.services.image_storage_handler import ImageStorageHandler


class ContactLogicHandler:

    """
    Contact rules used by ContactRequestHandler when someone manages their list.
    """

    def __init__(self, contact_db=None, validator=None, image_storage=None):

        """
        Attaches the contacts table helper, field checks, and S3 image helper.
        Different helpers can be passed in later for tests without needing a live database.
        """

        self.contact_db = contact_db or ContactDatabaseHandlerRds()
        self.validator = validator or ContactValidator()
        self.image_storage = image_storage or ImageStorageHandler()

    def _attach_image_url(self, contact):

        """
        Adds a short lived image URL onto a Contact for templates when a key exists.

        Postgres only stores our S3 key, so I build the temporary link here when the page needs to show the photo.
        This way the bucket can stay private and I do not need a permanent public link.
        """

        if not contact:
            return contact

        contact.profile_image_url = None

        if contact.profile_image_key:
            contact.profile_image_url = self.image_storage.get_presigned_url(
                contact.profile_image_key
            )

        return contact

    def process_create(self, user_id, form_data, image_file=None):

        """
        Validates and inserts a new contact owned by user_id.

        First name must pass ContactValidator.
        An optional photo is checked, then uploaded to S3,
        and the object key is stored in Postgres as profile_image_key.
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

        ok, message = self.validator.validate_image(image_file)

        if not ok:
            return False, message, None

        profile_image_key = None

        if image_file is not None and getattr(image_file, "filename", None):
            profile_image_key = self.image_storage.upload_image(user_id, image_file)

        contact = self.contact_db.insert_contact(
            user_id=user_id,
            profile_image_key=profile_image_key,
            **cleaned,
        )

        return True, "Contact Created", self._attach_image_url(contact)

    def process_list(self, user_id):

        """
        Returns the contact list for the signed in user only.

        Other accounts' rows never appear here because the database query filters on user_id.
        Each row gets a short lived image URL when a profile photo key is stored.
        """

        contacts = self.contact_db.select_contacts_for_user(user_id)

        return [self._attach_image_url(contact) for contact in contacts]

    def process_get(self, contact_id, user_id):

        """
        Returns one owned contact, or None when it is missing or belongs to someone else.

        Detail, edit, and delete all use this check before showing or changing a row.
        """

        contact = self.contact_db.select_contact_for_user(contact_id, user_id)

        return self._attach_image_url(contact)

    def process_update(self, contact_id, user_id, form_data, image_file=None):

        """
        Validates and updates one contact from this user's list.

        I first confirm the row belongs to this user,
        then run the same field checks as create.
        A new photo replaces the old S3 object and updates profile_image_key.
        Leaving the file blank keeps the existing photo.
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

        ok, message = self.validator.validate_image(image_file)

        if not ok:
            return False, message, None

        profile_image_key = existing.profile_image_key

        if image_file is not None and getattr(image_file, "filename", None):
            new_key = self.image_storage.upload_image(user_id, image_file)

            if existing.profile_image_key:
                self.image_storage.delete_image(existing.profile_image_key)

            profile_image_key = new_key

        contact = self.contact_db.update_contact_for_user(
            contact_id=contact_id,
            user_id=user_id,
            profile_image_key=profile_image_key,
            **cleaned,
        )

        if not contact:
            return False, "Contact not found.", None

        return True, "Contact Updated", self._attach_image_url(contact)

    def process_delete(self, contact_id, user_id):

        """
        Deletes one contact from this user's list.

        The SQL only removes a row when both contact id and user id match,
        so a guessed URL cannot delete someone else's contact.
        Any S3 photo for that contact is removed as well.
        """

        existing = self.contact_db.select_contact_for_user(contact_id, user_id)

        if not existing:
            return False, "Contact not found."

        if existing.profile_image_key:
            self.image_storage.delete_image(existing.profile_image_key)

        deleted = self.contact_db.delete_contact_for_user(contact_id, user_id)

        if not deleted:
            return False, "Contact not found."

        return True, "Contact Deleted"
