import os

from flask import Flask
from flask_cors import CORS

from config import config as config_by_name
from model import db

from blueprint.hostmonitor.hostmonitor_report import hostmonitor_report
from blueprint.prtg_alerts import prtg_alerts
from blueprint.jkb_status import jkb_status
from blueprint.for_frontend.handling_axios import handling_axios
from blueprint.for_frontend.jkb_db_routes import jkb_db_routes
from blueprint.for_frontend.hostmonitor.returning_hostmonitor_info_for_frontend import returning_hostmonitor_info_for_frontend
from blueprint.for_frontend.prtg.returning_prtg_for_frontend import returning_prtg_for_frontend
from blueprint.for_frontend.jkb.returning_jkb_for_frontend import returning_jkb_for_frontend
from demo_mode import install_demo_mode

app = Flask(__name__)
app.config.from_object(config_by_name[os.environ.get('APP_CONFIG', 'production')])
db.init_app(app)
CORS(app)

for blueprint in (
    hostmonitor_report,
    prtg_alerts,
    jkb_status,
    handling_axios,
    jkb_db_routes,
    returning_hostmonitor_info_for_frontend,
    returning_prtg_for_frontend,
    returning_jkb_for_frontend,
):
    app.register_blueprint(blueprint)

install_demo_mode(app)
