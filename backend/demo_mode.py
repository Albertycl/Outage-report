from flask import jsonify, request
from sqlalchemy import text

from model import db

REFRESH_PATHS = (
    '/refresh_hostmonitor_report',
    '/refresh_prtg_alerts_from_pagerduty',
    '/refresh_all_jkb',
)

TOUCH = (
    "UPDATE prtg_summary_data SET timestamp = :n",
    "UPDATE prtg_alert_current SET timestamp = :n",
    "UPDATE pagerduty_poll_status SET last_run_at = :n, last_success_at = :n",
    "UPDATE jkb_infra_summary SET timestamp = :n",
    "UPDATE jkb_alert_details SET timestamp = :n",
    "UPDATE jkb_all_sensor_status SET timestamp = :n",
    "UPDATE jkb_poll_status SET last_run_at = :n, last_success_at = :n",
    "UPDATE hostmonitor_alert_summary SET timestamp = :n",
    "UPDATE hostmonitor_alert_detail SET timestamp = :n",
    "UPDATE alert_for_bu_from_hm82_reports SET timestamp = :n",
    "UPDATE hostmonitor_report_run SET run_at = :n, report_generated_at = :n",
    "UPDATE hostmonitor_report_test SET run_at = :n",
)


def install_demo_mode(app):
    @app.before_request
    def _demo_refresh():
        if request.path not in REFRESH_PATHS:
            return None
        n = db.session.execute(text("SELECT DATE_ADD(UTC_TIMESTAMP(), INTERVAL 8 HOUR)")).scalar()
        for stmt in TOUCH:
            db.session.execute(text(stmt), {'n': n})
        db.session.commit()
        return jsonify({'status': 'ok', 'demo': True, 'message': 'Demo: no outbound call, seeded numbers re-stamped as fresh'})
