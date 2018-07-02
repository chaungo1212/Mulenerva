"""Tests for the Catalog library. Includes both DB-backed and file-backed."""

from pathlib import Path
from unittest import TestCase
from uuid import uuid4

from bson import ObjectId
from bson.json_util import loads
from pymongo import MongoClient

from catalog_server import Catalog
from catalog_server.metadata_utils import SAMPLE_1, SAMPLE_2


class DatabaseBackedCatalogTests(TestCase):
    """Tests for Catalog library when backed by a MongoDB database."""

    def setUp(self):
        """Create a test database environment with no values."""
        self.db_url = 'mongodb://localhost:27017/'
        self.db_name = str(uuid4())

        self.catalog = {}
        self.inserted_id = {}

    def tearDown(self):
        """Delete the test environment."""
        db_client = MongoClient(self.db_url)
        db_client.drop_database(self.db_name)

    def test_init(self):
        """Verify that the DB-backed Catalog initializes correctly."""
        self.catalog = Catalog(db_url=self.db_url, db_name=self.db_name)

    def test_metadata_add(self):
        """Verify that the DB-backed Catalog adds metadata without failing."""
        self.test_init()
        self.inserted_id = self.catalog.apply_change(metadata=SAMPLE_1)
        self.assertIsNotNone(self.inserted_id, "Inserted ID was None.")

    def test_metadata_get(self):
        """Verify that the DB-backed Catalog gets metadata correctly."""
        self.test_metadata_add()
        metadata = self.catalog.get_metadata(self.inserted_id)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['title'], SAMPLE_1['title'], "Returned content title incorrect.")

    def test_metadata_get_deleted(self):
        """Verify that the DB-backed Catalog does not return deleted metadata."""
        self.test_metadata_delete()
        metadata = self.catalog.get_metadata(self.inserted_id)
        self.assertEqual(metadata, {}, "Catalog returned entry which was supposed to be deleted.")

    def test_metadata_get_invalid(self):
        """Verify that the DB-backed Catalog does not return metadata that does not exist."""
        self.test_init()
        metadata = self.catalog.get_metadata(ObjectId()) # generated ID
        self.assertEqual(metadata, {}, "Catalog found entry that was not put there.")

    def test_metadata_get_modified(self):
        """Verify that the DB-backed Catalog gets metadata correctly."""
        self.test_metadata_modify()
        metadata = self.catalog.get_metadata(self.inserted_id)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['title'], SAMPLE_2['title'], "Returned content title incorrect.")

    def test_metadata_modify(self):
        """Verify that the DB-backed Catalog updates existing metadata correctly."""
        self.test_metadata_get()
        new_id = self.catalog.apply_change(content_id=self.inserted_id, metadata=SAMPLE_2)
        self.assertEqual(new_id, self.inserted_id, "Updating an entry resulted in a new ID.")

    def test_metadata_delete(self):
        """Verify that the DB-backed Catalog deletes existing metadata correctly."""
        self.test_metadata_add()
        self.catalog.apply_change(content_id=self.inserted_id)

    def test_changes_get(self):
        """Verify that the DB-backed Catalog can return changes correctly."""
        self.test_metadata_modify()
        change_list = self.catalog.get_changes(0)

        self.assertEqual(change_list[0]['timestamp'], 1, "First change ID was not correct.")
        self.assertEqual(change_list[1]['timestamp'], 2, "Second change ID was not correct.")

        title1 = change_list[0]['metadata']['title']
        title2 = change_list[1]['metadata']['title']
        self.assertEqual(title1, SAMPLE_1['title'], "First content title was not correct.")
        self.assertEqual(title2, SAMPLE_2['title'], "Second content title was not correct.")

    def test_changes_get_invalid(self):
        """Verify that the DB-backed Catalog does not return changes that do not exist."""
        self.test_init()
        change_list = self.catalog.get_changes(0)
        self.assertEqual(len(change_list), 0, "Changes were found which should not exist.")

    def test_changes_get_json(self):
        """Verify that the DB-backed Catalog can return change JSON correctly."""
        self.test_metadata_add()
        change_list = self.catalog.get_changes_json(0)
        self.assertIsNotNone(change_list, "No changes were returned.")
        loads(change_list)

class FileBackedCatalogTests(TestCase):
    """Tests for Catalog library when backed by an on-disk changelog file."""

    def setUp(self):
        """Create a test folder environment with empty changelog."""
        self.folder_path = '/tmp/mvtest-' + str(uuid4()) + '/'
        self.changelog = self.folder_path + 'changelog'
        Path(self.folder_path).mkdir()
        Path(self.changelog).touch()
        self.catalog = {}

    def tearDown(self):
        """Delete the test environment."""
        Path(self.changelog).unlink()
        Path(self.folder_path).rmdir()

    def test_init(self):
        """Verify that the file-backed Catalog initializes correctly."""
        self.catalog = Catalog(change_file=self.changelog)

    def test_changes_add(self):
        """Verify that the file-backed Catalog adds changes without failing."""
        self.test_init()
        self.catalog.apply_change(metadata=SAMPLE_1, timestamp=1)
        self.catalog.apply_change(metadata=SAMPLE_2, timestamp=2)

    def test_changes_get(self, populate_metadata_first=True):
        """Verify that the file-backed Catalog can return changes correctly."""
        if populate_metadata_first:
            self.test_changes_add()

        change_list = self.catalog.get_changes(0)

        self.assertEqual(change_list[0]['timestamp'], 1, "First change ID was not correct.")
        self.assertEqual(change_list[1]['timestamp'], 2, "Second change ID was not correct.")

        title1 = change_list[0]['metadata']['title']
        title2 = change_list[1]['metadata']['title']
        self.assertEqual(title1, SAMPLE_1['title'], "First content title was not correct.")
        self.assertEqual(title2, SAMPLE_2['title'], "Second content title was not correct.")

    def test_changes_get_invalid(self):
        """Verify that the file-backed Catalog does not return changes that do not exist."""
        self.test_init()
        change_list = self.catalog.get_changes(0)
        self.assertEqual(len(change_list), 0, "Changes were found which should not exist.")

    def test_changes_get_json(self):
        """Verify that the file-backed Catalog can return change JSON correctly."""
        self.test_changes_add()
        change_list = self.catalog.get_changes_json(0)
        self.assertIsNotNone(change_list, "No changes were returned.")
        loads(change_list)

    def test_flush_file(self):
        """Verify that the file-backed Catalog can flush changes to file correctly."""
        self.test_changes_add()
        self.catalog.flush_changelog()
        size = Path(self.changelog).stat().st_size
        self.assertNotEqual(size, 0, "Changelog was empty; should not have been.")

    def test_cache_file(self):
        """Verify that the file-backed Catalog can load changes from file correctly."""
        self.test_flush_file()
        self.test_init()
        self.test_changes_get(populate_metadata_first=False)
