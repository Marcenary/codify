# TODO: Add whatever
# FIXME: Should be
from app import create_app
# from routes import *

if __name__ == "__main__":
    app = create_app()
    app.run(debug=1)
