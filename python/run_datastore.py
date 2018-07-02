"""Entry point for the Catalog Server."""

import sys

from catalog_server.server import datastore as app, init


CONNECTION_STRING = 'mongodb://localhost:27017/'
DATASTORE_MONGO_DB = 'mulenerva-datastore'
S3_CATALOG_BUCKET = 'mulenerva-catalog'

init(CONNECTION_STRING, DATASTORE_MONGO_DB, s3_bucket=S3_CATALOG_BUCKET)

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=5002)
