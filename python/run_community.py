"""Entry point for the Catalog Server."""

import sys

from catalog_server.server import community as app, init


CONNECTION_STRING = 'mongodb://localhost:27017/'
COMMUNITY_MONGO_DB = 'mulenerva-community'

init(CONNECTION_STRING, COMMUNITY_MONGO_DB)

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=5001)
