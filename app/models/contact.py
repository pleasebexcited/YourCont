"""
app/models/contact.py: Holds one contact in memory

Contact holds the details for one YourCont contact in memory.
These values come from the contacts table in Postgres.
I use a Contact class instead of a loose dictionary so templates and handlers can read clear names like contact.email.
ContactDatabaseHandlerRds builds a Contact after a database query.
ContactLogicHandler then uses that Contact when listing, viewing, updating, or deleting.
profile_image_key is stored ready for S3 in a later milestone.
This file only stores contact fields.
It does not talk to the browser or run SQL itself.
"""

from datetime import date, datetime


class Contact:

    """
    One contact as used when creating, listing, viewing, updating, or deleting rows.
    """

    def __init__(
        self,
        contact_id,
        user_id,
        first_name,
        last_name=None,
        email=None,
        phone=None,
        address=None,
        birthday=None,
        relationship=None,
        notes=None,
        profile_image_key=None,
    ):

        """
        Holds the fields that match a contacts table row.

        user_id is the owning YourCont account,
        which is how list and detail pages stay private to the signed in person.
        Empty optional text fields become blank strings so templates do not have to test for None everywhere.
        """

        self.contact_id = contact_id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name or ""
        self.email = email or ""
        self.phone = phone or ""
        self.address = address or ""
        self.birthday = birthday
        self.relationship = relationship or ""
        self.notes = notes or ""
        self.profile_image_key = profile_image_key

    @property
    def id(self):

        """
        Short name used by my templates, which already call contact.id.
        """

        return self.contact_id

    @property
    def birthday_display(self):

        """
        Formats birthday as day/month/year for NZ style reading on the detail screen.
        Empty when no birthday is set.
        """

        if not self.birthday:
            return ""

        if isinstance(self.birthday, datetime):
            return self.birthday.strftime("%d/%m/%Y")

        if isinstance(self.birthday, date):
            return self.birthday.strftime("%d/%m/%Y")

        return str(self.birthday)

    @property
    def birthday_input(self):

        """
        Formats birthday as year-month-day for the HTML date field on the edit form.
        """

        if not self.birthday:
            return ""

        if isinstance(self.birthday, datetime):
            return self.birthday.strftime("%Y-%m-%d")

        if isinstance(self.birthday, date):
            return self.birthday.strftime("%Y-%m-%d")

        return str(self.birthday)

    @classmethod
    def from_row(cls, row):

        """
        Builds a Contact from a Postgres dictionary row returned by app/db.py.

        That keeps SQL column names in one place and lets templates read contact.email style names.
        """

        return cls(
            contact_id=row["contact_id"],
            user_id=row["user_id"],
            first_name=row["first_name"],
            last_name=row.get("last_name"),
            email=row.get("email"),
            phone=row.get("phone"),
            address=row.get("address"),
            birthday=row.get("birthday"),
            relationship=row.get("relationship"),
            notes=row.get("notes"),
            profile_image_key=row.get("profile_image_key"),
        )
