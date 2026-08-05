"""
app/services/contact_validator.py: Checks contact form fields before saving

Simple field checks for YourCont contact forms.
ContactLogicHandler calls validate_fields before insert or update so bad or empty required values do not reach Postgres.
I only require first name for MVP, which matches the rule I locked in the plan.
Image checks allow JPEG or PNG files up to about 2 MB before S3 upload.
I chose that size limit in my plan so profile photos stay small enough for Elastic Beanstalk uploads
and so the app rejects oversized files before they reach S3.
"""


class ContactValidator:

    """
    Validates contact form values for create and update.
    """

    MAX_IMAGE_BYTES = 2 * 1024 * 1024
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

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
        Checks an optional contact photo before it goes to S3.

        I check the file type and size here first so a bad photo is stopped early,
        instead of uploading something that S3 or the page cannot use.

        No file means the contact can still be saved without a picture.
        JPEG and PNG only, with a 2 MB size limit to match the plan.
        """

        if image_file is None or not getattr(image_file, "filename", None):
            return True, None

        filename = image_file.filename.strip().lower()
        extension = ""

        if "." in filename:
            extension = "." + filename.rsplit(".", 1)[-1]

        content_type = (image_file.mimetype or "").lower()

        if (
            content_type not in self.ALLOWED_IMAGE_TYPES
            and extension not in self.ALLOWED_IMAGE_EXTENSIONS
        ):
            return False, "Please upload a JPEG or PNG photo."

        image_file.stream.seek(0, 2)
        size = image_file.stream.tell()
        image_file.stream.seek(0)

        if size <= 0:
            return False, "Please choose a photo file that is not empty."

        if size > self.MAX_IMAGE_BYTES:
            return False, "Please upload a photo smaller than 2 MB."

        return True, None
