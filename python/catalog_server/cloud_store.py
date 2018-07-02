"""Utility for uploading/downloading Catalog files with Amazon S3."""

from hashlib import md5
from os import remove as delete_file
from time import time as seconds_since_epoch

from boto3 import client, resource, session


class CloudStore:
    """Utility for uploading/downloading Catalog files with Amazon S3."""

    def __init__(self, bucket_name):
        """Constructor connects to S3 and sets up resources."""
        session_config = session.Config(signature_version='s3v4')
        self.client = client('s3', config=session_config)
        self.resource = resource('s3', config=session_config)
        self.bucket = self.resource.Bucket(bucket_name)

    def download(self, key):
        """Download the specified object and store it in-memory."""
        obj = self.resource.Object(self.bucket.name, key)
        return None if not obj else obj.get()['Body'].read()

    def download_to_file(self, key, local_file_path):
        """Download the specified object and save it to the specified path."""
        self.bucket.download_file(key, local_file_path)

    def get_temporary_link(self, key):
        """Get a temporary, public link to the object."""
        # TODO - make sure region stuff is right - I don't think this works
        obj = self.resource.Object(self.bucket.name, key)
        if not obj:
            return ''
        return self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket.name, 'Key': key}
        )

    def remove(self, key):
        """Remove a resource from S3 if it exists."""
        obj = self.resource.Object(self.bucket.name, key)
        if obj:
            obj.delete()

    def upload(self, file_name, file_data):
        """Upload the in-memory file to S3 and return the key."""
        file_ext = file_name.split('.')[-1] or ''
        timestamp = str(seconds_since_epoch())
        hash_string = md5(file_data).hexdigest()
        upload_key = '%s-%s.%s' % (hash_string, timestamp, file_ext)
        self.bucket.put_object(Key=upload_key, Body=file_data)
        return {'key': upload_key, 'size': len(file_data)}
