"""
app/services/image_storage_handler.py: Uploads contact photos to Amazon S3

S3 work for YourCont contact profile images lives in this class.
ContactLogicHandler calls it when someone adds or changes a photo,
and when a contact is deleted so the file does not stay behind in the bucket.
Objects stay private.
I return a short lived URL so the browser can show the image without making the bucket public.
Bucket name and region come from .env for local work,
and the same code can use an IAM role on Elastic Beanstalk later.
"""

import os
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class ImageStorageHandler:

    """
    Uploads, reads, and deletes contact profile images in my private S3 bucket.
    """

    def __init__(self, bucket_name=None, region_name=None):

        """
        Reads S3_BUCKET and AWS_REGION from the environment when no values are passed in.
        """

        self.bucket_name = bucket_name or os.getenv("S3_BUCKET")
        self.region_name = region_name or os.getenv("AWS_REGION") or "ap-southeast-2"
        self._client = None

    def _get_client(self):

        """
        Builds a boto3 S3 client the first time I need one.

        Local runs use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from .env.
        Elastic Beanstalk can supply credentials through an instance role instead.
        """

        if self._client is None:
            self._client = boto3.client("s3", region_name=self.region_name)

        return self._client

    def _require_bucket(self):

        """
        Stops with a clear message when S3_BUCKET is missing from .env.
        """

        if not self.bucket_name:
            raise RuntimeError(
                "S3_BUCKET is missing. Add your bucket name to the .env file."
            )

    def upload_image(self, user_id, image_file):

        """
        Uploads one contact photo for this user and returns the object key.

        The key is shaped as contacts/user_id/unique_id.ext so each file stays under the owning account.
        That matches profile_image_key in Postgres without needing a public URL stored in the table.
        """

        self._require_bucket()

        original_name = (image_file.filename or "photo").strip()
        extension = Path(original_name).suffix.lower() or ".jpg"

        if extension not in {".jpg", ".jpeg", ".png"}:
            extension = ".jpg"

        object_key = f"contacts/{user_id}/{uuid.uuid4().hex}{extension}"
        content_type = image_file.mimetype or "application/octet-stream"

        try:
            self._get_client().upload_fileobj(
                image_file.stream,
                self.bucket_name,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )
        except (BotoCoreError, ClientError) as error:
            raise RuntimeError("Could not upload the contact photo to S3.") from error

        return object_key

    def get_presigned_url(self, object_key, expires_in=3600):

        """
        Builds a short lived HTTPS link so templates can show a private S3 image.

        One hour is long enough for someone to view the page,
        but the link will not keep working if it is copied and shared later.
        """

        if not object_key:
            return None

        self._require_bucket()

        try:
            return self._get_client().generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except (BotoCoreError, ClientError):
            return None

    def delete_image(self, object_key):

        """
        Removes one object from the bucket when a contact photo is replaced or the contact is deleted.

        Missing keys are ignored so a second delete does not break the page flow.
        """

        if not object_key:
            return True

        self._require_bucket()

        try:
            self._get_client().delete_object(Bucket=self.bucket_name, Key=object_key)
        except (BotoCoreError, ClientError) as error:
            raise RuntimeError("Could not delete the contact photo from S3.") from error

        return True
