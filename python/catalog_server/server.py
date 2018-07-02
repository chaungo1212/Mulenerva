"""The Catalog server, providing endpoints for UI and data mule."""

from bson import ObjectId
from bson.json_util import dumps, loads
from flask import abort, Flask, request, make_response
from flask_cors import CORS, cross_origin

from os import path

from .catalog import Catalog
from .cloud_store import CloudStore
from .local_store import LocalStore
from .metadata_utils import has_required_metadata, populate_optional_fields, samples


ROUTES = {
    # shared routes
    'index':                    '/',
    'get_metadata':             '/metadata/<string:object_id>',
    #'get_metadata_all':         '/metadata/all',
    'get_search_results':       '/search/',
    'post_content':             '/content/new',
    'delete_content':           '/content/<string:object_id>',
    'post_image':               '/image/new',
    'delete_image':             '/image/<string:object_id>',
    'get_image':                '/image/<string:object_id>',
    'ping':                     '/ping',

    # community-only
    'get_latest_timestamp':     '/changelog/latest_timestamp',
    'post_changes':             '/changelog/update',
    'get_metadata_community':   '/metadata/all',
    'get_metadata_available':   '/metadata/available',
    'get_metadata_requested':   '/metadata/requested',
    'post_refresh':             '/refresh/<string:object_id>',
    'post_request':             '/request', #?id=<object_id>
    'post_availability':        '/available',
    'get_content':              '/content/<string:object_id>',
    'test':                     '/test',

    # datastore-only
    'get_changes_after':        '/changelog/get_changes_after/<int:timestamp>',
    'get_metadata_datastore':   '/metadata/all',
    'post_metadata_new':        '/metadata/new',
    'post_metadata_update':     '/metadata/<string:object_id>',
    'delete_metadata':          '/metadata/<string:object_id>',
    'get_content_link':         '/content_link/<string:object_id>',
}

CATALOG = None
LOCAL_STORE = None
CLOUD_STORE = None

community = Flask('catalog_server_community')
CORS(community)

datastore = Flask('catalog_server_datastore')
CORS(datastore)

def init(connection_string, database, s3_bucket=None):
    global CATALOG
    global LOCAL_STORE
    global CLOUD_STORE
    CATALOG = Catalog(db_url=connection_string, db_name=database)
    LOCAL_STORE = LocalStore(db=CATALOG.database)
    if s3_bucket:
        CLOUD_STORE = CloudStore(s3_bucket)

# -----------------------------------------------
# Index Route
# -----------------------------------------------

@community.route(ROUTES['index'], methods=['GET'])
@datastore.route(ROUTES['index'], methods=['GET'])
def index():
    """Index returns list of possible routes."""
    results = []
    for item in ROUTES:
        results.append(ROUTES[item])
    return dumps(results)

# -----------------------------------------------
# Changelog Routes
# -----------------------------------------------

@datastore.route(ROUTES['get_changes_after'], methods=['GET'])
def get_changes_after(timestamp):
    """Get all changes after the specified timestamp."""
    return CATALOG.get_changes_json(timestamp)

@community.route(ROUTES['get_latest_timestamp'], methods=['GET'])
def get_latest_timestamp():
    return dumps(CATALOG.get_latest_timestamp())

@community.route(ROUTES['post_changes'], methods=['POST'])
def post_changes():
    """Post updates to the changelog."""
    updates = request.get_json()
    my_timestamp = CATALOG.get_latest_timestamp()
    for item in updates:
        their_timestamp = item['timestamp']
        if my_timestamp == their_timestamp:
            continue

        if item['metadata']:
            metadata = item['metadata']

            if '_id' in metadata:
                id = metadata['_id']['$oid']
                metadata['_id'] = ObjectId(id)

                #timestamp = CATALOG.get_latest_timestamp()
                CATALOG.apply_change(content_id=metadata['_id'], metadata=metadata, timestamp=their_timestamp)
        else:
            CATALOG.apply_change(content_id=item['content_id'], timestamp=their_timestamp)
    return "posted changes"
    abort(501) # TODO

# -----------------------------------------------
# Metadata Routes
# -----------------------------------------------

@datastore.route(ROUTES['delete_metadata'], methods=['DELETE'])
def delete_metadata(object_id):
    """Delete metadata from the catalog. Datastore only."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    CATALOG.apply_change(content_id=object_id)
    return 'DELETED'

@community.route(ROUTES['get_metadata'], methods=['GET'])
@datastore.route(ROUTES['get_metadata'], methods=['GET'])
def get_metadata(object_id):
    """Get the metadata associated with an ObjectId."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400

    metadata = CATALOG.get_metadata(object_id)
    return dumps(metadata)

@community.route(ROUTES['get_metadata_community'], methods=['GET'])
def get_metadata_community():
    """Get ALL metadata stored on the server. Please use for test only."""
    metadata = CATALOG.get_all_metadata()
    results = LOCAL_STORE.find_all_related(metadata)
    return dumps(results)

@datastore.route(ROUTES['get_metadata_datastore'], methods=['GET'])
def get_metadata_datastore():
    """Get ALL metadata stored on the server. Please use for test only."""
    metadata = CATALOG.get_all_metadata()
    return dumps(metadata)

@community.route(ROUTES['get_metadata_available'], methods=['GET'])
def get_metadata_available():
    """Get the metadata available on the server. Community only."""
    metadata = CATALOG.get_available()
    results = LOCAL_STORE.find_all_related(metadata)
    return dumps(results)

@community.route(ROUTES['get_metadata_requested'], methods=['GET'])
def get_metadata_requested():
    """Get the metadata requested by students. Community only."""
    metadata = CATALOG.get_requests()
    #results = LOCAL_STORE.find_all_related(metadata)
    return dumps(metadata)

@community.route(ROUTES['get_search_results'], methods=['GET'])
@datastore.route(ROUTES['get_search_results'], methods=['GET'])
def get_search_results():
    """Search for Metadata in the Catalog."""
    args = request.args
    title = args.get('title')
    genre = args.get('genre')
    tags = args.getlist('tags')

    if tags and tags[0] == '':
        tags = None
    type = args.getlist('type')
    if type and type[0] == '':
        type = None

    available = args.get('available')
    requested = args.get('requested')

    metadata = CATALOG.query_data(title, genre, tags, type, available, requested)
    results = LOCAL_STORE.find_all_related(metadata)

    return dumps(results)

@datastore.route(ROUTES['post_metadata_new'], methods=['POST'])
@community.route(ROUTES['post_metadata_new'], methods=['POST'])
def post_metadata_new():
    """Add a new piece of metadata to the catalog."""
    data = request.get_json()
    if '_id' in data:
        data['_id'] = ObjectId(data['_id'])
    if not data:
        return 'MISSING_JSON', 400
    if not has_required_metadata(data):
        return 'INVALID_JSON', 400
    populate_optional_fields(data)
    return dumps(CATALOG.apply_change(metadata=data))

@datastore.route(ROUTES['post_metadata_update'], methods=['POST'])
def post_metadata_update(object_id):
    """Update an existing piece of metadata in the catalog."""
    data = request.get_json()
    if not data:
        return 'MISSING_JSON', 400
    if not has_required_metadata(data):
        return 'INVALID_JSON', 400
    return dumps(CATALOG.apply_change(content_id=object_id, metadata=data))

@community.route(ROUTES['post_refresh'], methods=['POST'])
def post_refresh(object_id):
    """Refresh a piece of content to prevent it from expiring. Community only."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    return dumps(CATALOG.refresh(object_id))

@community.route(ROUTES['post_request'], methods=['GET'])
def post_request():
    """Request a piece of content. Community only."""
    id = request.args['id']
    if not ObjectId.is_valid(id):
        return 'INVALID_ID', 400
    return dumps(CATALOG.set_request(id))

@community.route(ROUTES['post_availability'], methods=['GET'])
def post_availability():
    """Set availability of a piece of content. Community only."""
    id = request.args['id']
    if not ObjectId.is_valid(id):
        return 'INVALID_ID', 400
    return dumps(CATALOG.set_available(id))

# -----------------------------------------------
# Content Routes
# -----------------------------------------------

@community.route(ROUTES['delete_content'], methods=['DELETE'])
def delete_content_community(object_id):
    """Delete content from the catalog. Community version."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    LOCAL_STORE.delete(object_id)
    return 'DELETED'

@datastore.route(ROUTES['delete_content'], methods=['DELETE'])
def delete_content_datastore(object_id):
    """Delete content from the catalog. Datastore version."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    CATALOG.set_available(object_id)
    LOCAL_STORE.delete(object_id)
    return 'DELETED'

@community.route(ROUTES['delete_image'], methods=['DELETE'])
def delete_image_community(object_id):
    """Delete an image from the catalog. Community version."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    LOCAL_STORE.delete_thumbnail(object_id)
    return 'DELETED'

@datastore.route(ROUTES['delete_image'], methods=['DELETE'])
def delete_image_datastore(object_id):
    """Delete an image from the catalog. Datastore version."""
    CLOUD_STORE.remove(object_id)
    return 'DELETED'

@community.route(ROUTES['get_content'], methods=['GET'])
def get_content(object_id):
    """Return content (file) from the catalog. Community only."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    content = LOCAL_STORE.get_content(object_id)
    metadata = LOCAL_STORE.find_content(object_id)
    filetype = metadata['filename'][-3:]
    response = make_response(content)
    if filetype == 'mp4':
        response.headers['Content-Type'] = 'video/mp4'
    elif filetype == 'pdf':
        response.headers['Content-Type'] = 'application/pdf'
    elif filetype == 'txt':
        response.headers['Content-Type'] = 'text/*'
    return response

@datastore.route(ROUTES['get_content_link'], methods=['GET'])
def get_content_link(object_id):
    """Return a link to the content stored on Amazon S3. Datastore only."""
    return CLOUD_STORE.get_temporary_link(object_id)

@community.route(ROUTES['get_image'], methods=['GET'])
def get_image_community(object_id):
    """Return an image (like a thumbnail) for display. Community version."""
    if not ObjectId.is_valid(object_id):
        return 'INVALID_ID', 400
    image = LOCAL_STORE.get_thumbnail(object_id)
    response = make_response(image)
    response.headers['Content-Type'] = 'image'
    return response

@datastore.route(ROUTES['get_image'], methods=['GET'])
def get_image_datastore(object_id):
    """Return an image (like a thumbnail) for display. Datastore version."""
    image = CLOUD_STORE.download(object_id)
    if not image:
        abort(404)
    response = make_response(image)
    response.headers['Content-Type'] = 'image'
    return response

@community.route(ROUTES['post_content'], methods=['POST'])
def post_content_community():
    """Post new content to the catalog. Community version."""
    for fileid in request.files:
        print('Beginning content upload...')

        file = request.files[fileid]
        underscore = fileid.find('_')+1
        id = fileid[underscore:]
        if(LOCAL_STORE.find_content(id)):
            print("File: "+id+" exists")
            continue

        print('content_id ' + id)
        raw = request.files[fileid].read()
        CATALOG.set_request(id)
        CATALOG.set_available(id)
        return LOCAL_STORE.insert(raw, file.filename, id)
    abort(501) # TODO

@datastore.route(ROUTES['post_content'], methods=['POST'])
def post_content_datastore():
    """Post new content to the catalog. Datastore version."""
    if not 'content' in request.files:
        return 'MISSING_CONTENT', 400
    content = request.files['content']
    return dumps(CLOUD_STORE.upload(content.filename, content.read()))

@community.route(ROUTES['post_image'], methods=['POST'])
def post_image_community():
    """Post a new image to the catalog. Community version."""
    for fileid in request.files:
        file = request.files[fileid]
        underscore = fileid.find('_')+1
        id = fileid[underscore:]
        if(LOCAL_STORE.find_thumbnail(id)):
            print("File: "+id+" exists")
            continue

        print('thumb_id: ' + id)
        raw = request.files[fileid].read()
        return LOCAL_STORE.insert_thumbnail(raw, file.filename, id)
    abort(501)

@datastore.route(ROUTES['post_image'], methods=['POST'])
def post_image_datastore():
    """Post a new image to the catalog. Datastore version."""
    if not 'image' in request.files:
        return 'MISSING_IMAGE', 400
    image = request.files['image']
    return dumps(CLOUD_STORE.upload(image.filename, image.read()))

# -----------------------------------------------
# Utility Routes
# -----------------------------------------------

@community.route('/delete_metadata')
def delete_metadata():
    CATALOG.apply_change(content_id=request.args['id'])
    LOCAL_STORE.delete_thumbnail(request.args['id'])
    return 'deleted'

@community.route('/delete_content')
def delete_content():
    LOCAL_STORE.delete(request.args['id'])
    CATALOG.set_available(request.args['id'])
    metadata = CATALOG.get_metadata(request.args['id'])
    metadata['is_available'] = False
    return 'deleted'

@community.route(ROUTES['ping'])
@datastore.route(ROUTES['ping'])
def ping():
    return "PONG"

# def check_expiration():
#     metadata = CATALOG.get_all_metadata()
#     for item in metadata:
#         expiration = item['expiration']
#         timestamp = CATALOG.get_latest_timestamp()
#         if timestamp <= item['content']['uploadDate']['$Date'] + expiration:
#             delete_content()
