from flask import Flask
from gevent.pywsgi import WSGIServer
from app import app
import os
import logging

if __name__ == "__main__":
    #logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', debug=False, port=os.getenv("PORT", default=80))
    