from oslo_config import cfg

CONF = cfg.CONF

application_opts = [
    cfg.StrOpt("bind_host", default="0.0.0.0", help="Address to imdb_app"),
    cfg.IntOpt("bind_port", default=8000, help="Port to bind imdb_app"),
    cfg.StrOpt("secret_key", default="your_secret_key_here", help="Application secret key"),
    cfg.StrOpt("file_path", default="/path/to/uploads", help="File save folder path")
]

database_opts = [
    cfg.StrOpt("mongo_uri", default="mongodb://localhost:27017/imdb_app", help="Database URI")
]

# Define the options for each section
CONF.register_opts(application_opts, group="application")
CONF.register_opts(database_opts, group="database")


# Function to load configurations from a file
def load_config(file_path=None):
    if file_path:
        CONF(default_config_files=[file_path])


# Load the configuration file
load_config("/tmp/config/imdb_app.conf")
