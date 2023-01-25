from web._init_ import app
from gevent import pywsgi


# app.run(host = "0.0.0.0", debug=True, port=5000) #debug mode, port is 5000

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0',5000),app)
    server.serve_forever()