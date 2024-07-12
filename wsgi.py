from flask import Flask
from api_v1 import blueprint as api_v1
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_v1)

def create_app():
    return app
if __name__ == '__main__':
    app.run(host='0.0.0.0')