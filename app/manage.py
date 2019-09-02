import os
from .main import create_flask_app


environment = os.getenv("FLASK_ENV")
app = create_flask_app(environment)





