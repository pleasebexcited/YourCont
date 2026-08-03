"""
app/services/contact_validator.py: Checks contact form fields before saving

Simple field checks for YourCont contact forms.
ContactLogicHandler calls validate_fields before insert or update so bad or empty required values do not reach Postgres.
I only require first name for MVP, which matches the rule I locked in the plan.
Image checks stay for a later milestone when S3 upload is wired.
"""


class ContactValidator:

    """
    Validates contact form values for create and update.
    """

    def validate_fields(self, first_name, last_name, email, phone, address, birthday, relationship, notes):

        """
        Checks the posted contact fields for YourCont.

        First name is required for MVP.
        Other fields may be blank.
        Birthday must look like a real year month day value when it is provided,
        because the contacts table stores it as a date.
        Returns True with cleaned values, or False with an error message the page can flash.
        """

        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        email = (email or "").strip()
        phone = (phone or "").strip()
        address = (address or "").strip()
        birthday = (birthday or "").strip()
        relationship = (relationship or "").strip()
        notes = (notes or "").strip()

        if not first_name:
            return False, "Please enter a first name.", None

        # Empty birthday stays None in Postgres instead of an empty string.

        birthday_value = birthday or None

        if birthday_value:
            parts = birthday_value.split("-")

            if len(parts) != 3:
                return False, "Please enter a valid birthday.", None

            try:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
            except ValueError:
                return False, "Please enter a valid birthday.", None

            if year < 1900 or month < 1 or month > 12 or day < 1 or day > 31:
                return False, "Please enter a valid birthday.", None

        cleaned = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "birthday": birthday_value,
            "relationship": relationship,
            "notes": notes,
        }

        return True, None, cleaned

    def validate_image(self, image_file):

        """
        Placeholder for contact photo checks once S3 upload is built.
        Image upload is not wired yet, so this always passes.
        """

        return True, None
