# TODO: Add whatever
# FIXME: Should be
from app import create_app

if __name__ == "__main__":
    app = create_app()
    # app.run(debug=1) # without https
    # app.run(debug=True, ssl_context='adhoc')
    app.run(debug=1, exclude_patterns=['/home/marcenary/Project/codify/compile/languages/python/'], host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
