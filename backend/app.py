from flask import Flask
from flasgger import Swagger
from backend.routes.routes import register_routes

app = Flask(__name__)
Swagger(app)

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
