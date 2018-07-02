"""Client for interacting with the material catalog and its changelog."""

from collections import OrderedDict

from bson import ObjectId
from bson.json_util import dumps, loads
from pymongo import MongoClient


class Catalog:
    """Client for interacting with the material catalog and its changelog."""

    def __init__(self, change_file=None, db_url=None, db_name=None):
        """Create a Catalog client, either file-backed or DB-backed."""
        if db_url:
            self.db_client = MongoClient(db_url)
            self.database = self.db_client[db_name]
            self.catalog_collection = self.database['catalog']
            self.changelog_collection = self.database['changes']
        else:
            self.db_client = None
            self.database = None
            self.catalog_collection = None
            self.changelog_collection = None

        if change_file and not db_url:
            self.changelog_filename = change_file
            self.cached_changes = OrderedDict()
            self.cache_changelog()
        else:
            self.changelog_filename = None

    def apply_change(self, content_id=None, metadata=None, timestamp=None):
        """Apply a change to the catalog/changelog: insert, update, or delete."""
        if not self.db_client and not self.changelog_filename:
            return ObjectId()

        if self.db_client:

            # handle deletes
            if content_id and not metadata:
                self.catalog_collection.delete_many({'_id':ObjectId(content_id)})
                content_key = content_id

            # handle "datastore" inserts
            if not content_id and metadata:
                result = self.catalog_collection.insert_one(metadata)
                content_key = result.inserted_id

            # handle updates and "local server" inserts
            if content_id and metadata:
                result = self.catalog_collection.replace_one(
                    {'_id': ObjectId(content_id)},
                    metadata,
                    upsert=True
                )
                content_key = result.upserted_id or content_id

            # then write to the changelog database
            change = {'content_id':content_key}
            change['metadata'] = None if not metadata else metadata
            change['timestamp'] = timestamp or (self.get_latest_timestamp() + 1)
            self.changelog_collection.insert_one(change)
            return content_key

        else:
            self.cached_changes[timestamp] = {
                'timestamp': timestamp,
                'content_id': content_id,
                'metadata': metadata
            }
            return content_id

    def cache_changelog(self):
        """Load the changelog into memory based on the backup file."""
        if self.db_client or not self.changelog_filename:
            return

        self.cached_changes = {}
        changelist = []
        with open(self.changelog_filename, 'r') as changelog_file:
            metadata = changelog_file.read()
            if metadata:
                changelist = loads(metadata)

        for change in changelist:
            self.cached_changes[change['timestamp']] = change

    def flush_changelog(self):
        """Flush new changelog additions to the backup file."""
        if not self.changelog_filename:
            return
        self.sort_changelog()
        with open(self.changelog_filename, 'w') as changelog_file:
            changelog_file.write(dumps(self.get_changes(0)))

    def get_changes(self, after_timestamp):
        """Get an array of all changes after the specified change ID."""
        if not self.db_client and not self.changelog_filename:
            return []

        if self.db_client:
            return list(self.changelog_collection.find({'timestamp':{'$gt':after_timestamp}}))

        changes = self.cached_changes
        return [changes[c] for c in changes if changes[c]['timestamp'] > after_timestamp]

    def get_changes_json(self, after_timestamp):
        """Get all changes after specificed timestamp, JSON-serialized ."""
        return dumps(self.get_changes(after_timestamp))

    def get_all_metadata(self):
        if not self.db_client:
            return None
        metadata = self.catalog_collection.find()
        return metadata

    def get_metadata(self, key):
        """Get the metadata for a given key."""
        if not self.db_client:
            return None
        metadata = self.catalog_collection.find_one({'_id':ObjectId(key)})
        return metadata or {}

    def get_latest_timestamp(self):
        """Get the largest/latest change timestamp stored in the database."""
        if self.db_client is None:
            return 0
        latest_change = self.changelog_collection.find_one(sort=[('timestamp', -1)])
        return 0 if latest_change is None else latest_change['timestamp']

    def get_available(self):
        """Get the newly requested content"""
        if self.db_client is None:
            return None
        results = []
        metadata = self.catalog_collection.find({'is_available':True})
        return metadata

    def get_requests(self):
        """Get the newly requested content"""
        if self.db_client is None:
            return None
        results = []
        metadata = self.catalog_collection.find({'is_requested':True})
        return metadata

    def query_data(self, title, genre, tags, type, available, requested):
        filters_title = {}
        filters_tags = {}
        if title:
            filters_title['title'] = {'$regex': title, '$options': '-i'}
        if tags:
            filters_tags['tags'] = {'$in': [tag.lower() for tag in tags]}
        if genre:
            filters_title['genre'] = {'$regex': genre, '$options': '-i'}
            filters_tags['genre'] = {'$regex': genre, '$options': '-i'}
        if type:
            filters_title['type'] = {'$in': [t.lower() for t in type]}
            filters_tags['type'] = {'$in': [t.lower() for t in type]}
        if available != None:
            filters_title['is_available'] = available
            filters_tags['is_available'] = available
        if requested != None:
            filters_title['is_requested'] = requested
            filters_tags['is_requested'] = requested
        return self.catalog_collection.find({'$or': [filters_title, filters_tags]})

    def refresh(self, id):
        return self.catalog_collection.update_one({'_id':ObjectId(id)}, {'$set': {'expiration':100}}).raw_result

    def set_request(self, id):
        status = self.catalog_collection.find_one({'_id':ObjectId(id)})['is_requested']
        return self.catalog_collection.update_one({'_id':ObjectId(id)}, {'$set': {'is_requested':not status}}).raw_result

    def set_available(self, id):
        status = self.catalog_collection.find_one({'_id':ObjectId(id)})['is_available']
        return self.catalog_collection.update_one({'_id':ObjectId(id)}, {'$set': {'is_available':not status}}).raw_result

    def sort_changelog(self):
        """Sort the in-memory changelog in chronological order."""
        sorted_dict = OrderedDict()
        keys = sorted(list(self.cached_changes.keys()))
        for key in keys:
            sorted_dict[key] = self.cached_changes[key]
        self.cached_changes = sorted_dict

    def test_delete(self, desc):
        return self.catalog_collection.delete_one({'long_desc': desc})