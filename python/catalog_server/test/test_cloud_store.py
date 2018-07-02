"""Tests for the CloudStore module."""

from pathlib import Path
from unittest import TestCase
from uuid import uuid4

from boto3 import client, resource

from catalog_server import CloudStore


class CloudStoreTests(TestCase):
    """Tests for Catalog library when backed by a MongoDB database."""

    def setUp(self):
        """Create a test folder environment and test S3 bucket."""
        self.testenv = 'mvtest-' + str(uuid4())
        self.upload_key = ''
        self.util = None

        self.folder_path = '/tmp/' + self.testenv + '/'
        Path(self.folder_path).mkdir()

        self.test_file = self.folder_path + 'rawr.txt'
        self.test_text = 'testing stuff'
        with open(self.test_file, 'w') as open_file:
            open_file.write(self.test_text)

        client('s3').create_bucket(Bucket=self.testenv)

    def tearDown(self):
        """Delete the test folder and test S3 bucket."""
        if Path(self.test_file).exists():
            Path(self.test_file).unlink()
        Path(self.folder_path).rmdir()

        resource('s3').Bucket(self.testenv).objects.all().delete()
        client('s3').delete_bucket(Bucket=self.testenv)

    def test_init(self):
        """Verify that the CloudStore object initializes correctly."""
        self.util = CloudStore(self.testenv)
        self.assertIsNotNone(self.util)

    def test_upload_no_error(self):
        """Verify that uploading does not generate an error."""
        self.test_init()
        self.upload_key = self.util.upload_and_delete(self.test_file)
        self.assertIsNotNone(self.upload_key, "Uplaod and delete did not complete successfully.")

    def test_upload_deletes_file(self):
        """Verify that uploading deletes the local file."""
        self.test_upload_no_error()
        self.assertFalse(Path(self.test_file).exists(), "Test file should no longer exist.")

    def test_download_to_file(self):
        """Verify that an uploaded file can be downloaded again to a file on-disk."""
        self.test_upload_deletes_file()
        self.util.download_to_file(self.upload_key, self.test_file)
        with open(self.test_file, 'r') as open_file:
            self.assertEqual(self.test_text, open_file.read(), "Text did not match after download.")
