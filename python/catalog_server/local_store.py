"""Client for interacting with the local content store."""

import pymongo
import gridfs

from bson import ObjectId
from bson.json_util import dumps

class LocalStore:
    """Client for interacting with the local content store."""

    def __init__(self, db):
        """Create a Content client, either file-backed or DB-backed."""
        if db:
            self.db = db
            self.fs = gridfs.GridFS(db)
        else:
            self.db = None
            self.fs = None

    def insert(self, content, filename, id):
        kwargs = {'_id':ObjectId(id), 'filename':filename}
        #collection.update_one({'_id':ObjectId(id)}, {'$set': {'isRequested':False, 'isAvailable':True, 'expiration':123}})
        result = self.fs.put(content, **kwargs)
        print('Completed content upload for id: '+ id)
        return "Inserted"

    def find_content(self, id):
        try:
            result = self.db.fs.files.find_one({'_id':ObjectId(id)})
            return result
        except Exception as e:
            print(e)
        return None

    def find_thumbnail(self, id):
        try:
            result = self.db.fs.files.find_one({'thumb_id':ObjectId(id)})
            return result
        except Exception as e:
            print(e)
        return None

    def find_all_related(self, metadata_list):
        result = []
        for item in metadata_list:
            item['content'] = self.find_content(item['_id'])
            item['thumbnail'] = self.find_thumbnail(item['_id'])
            result.append(item)
        return result

    def delete(self, id):
        return self.fs.delete(ObjectId(id))

    def insert_thumbnail(self, content, filename, id):
        kwargs = {'thumb_id':ObjectId(id), 'filename':filename}
        result = self.fs.put(content, **kwargs)
        return "Inserted" 

    def get_content(self, id):
        video = self.fs.get(ObjectId(id))
        return video.read()

    def get_thumbnail(self, id):
        thumb_id = self.find_thumbnail(ObjectId(id))['_id']
        image = self.fs.get(thumb_id)
        return image.read()

    def delete_thumbnail(self, id):
        thumb_id = self.find_thumbnail(ObjectId(id))['_id']
        return self.fs.delete(thumb_id)
