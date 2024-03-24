from flask import Flask
from imdb_app.api.auth.routes import auth_app
from imdb_app.api.movies.routes import movies_app

app = Flask("imdb_app")

app.register_blueprint(auth_app)
app.register_blueprint(movies_app)
