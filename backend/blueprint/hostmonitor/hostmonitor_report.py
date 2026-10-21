"""
HostMonitor report endpoints (read-only, demo).

Serves the stored test runs in hostmonitor_report_run / hostmonitor_report_test
to the frontend. This is a concept demo: nothing here reads a real HostMonitor
server. The rows come from demo/seed_demo_data.sql.
"""

from flask import Blueprint, current_app, jsonify, request
import logging
from datetime import datetime, timedelta

from config import DevConfig
from model import (
    db,
    hostmonitor_report_run,
    hostmonitor_report_test,
)

hostmonitor_report = Blueprint("hostmonitor_report", __name__)

logging.basicConfig(level=logging.INFO)


def _gmt8_now():
    """Every timestamp in this database is naive GMT+8; keep to that."""
    return datetime.utcnow() + timedelta(hours=8)


# **********************************************************************
@hostmonitor_report.route("/hostmonitor_report_latest")
@hostmonitor_report.route("/hostmonitor_report_latest/")
def hostmonitor_report_latest():
    """
    The most recent reading and the tests in it -- what the frontend shows.

    Serves the stored run rather than re-reading the files, so the page loads
    at the same speed whether or not a report is readable, and so every viewer
    is looking at the same reading. ?infra= narrows to one infra;
    ?alerts_only=true drops the healthy tests.
    """
    alerts_only = request.args.get("alerts_only", "").lower() in ("1", "true", "yes")
    infra_filter = request.args.get("infra")
    # ?in_ltm=true / false narrows to one side of the split; absent shows both
    in_ltm_arg = request.args.get("in_ltm")
    in_ltm_filter = (None if in_ltm_arg is None
                     else in_ltm_arg.lower() in ("1", "true", "yes"))

    # the newest run, by the run_id its rows share
    newest = (hostmonitor_report_run.query
              .order_by(hostmonitor_report_run.run_at.desc(),
                        hostmonitor_report_run.id.desc())
              .first())

    if newest is None:
        return jsonify({
            "run_id": None,
            "run_at": None,
            "infras": [],
            "tests": [],
            "message": "the HostMonitor reports have not been read yet",
            **_report_meta(),
        }), 200

    runs_query = hostmonitor_report_run.query.filter_by(run_id=newest.run_id)
    tests_query = hostmonitor_report_test.query.filter_by(run_id=newest.run_id)
    if infra_filter:
        runs_query = runs_query.filter(hostmonitor_report_run.infra_name == infra_filter)
        tests_query = tests_query.filter(hostmonitor_report_test.infra_name == infra_filter)
    if alerts_only:
        tests_query = tests_query.filter(hostmonitor_report_test.is_alert.is_(True))
    if in_ltm_filter is not None:
        tests_query = tests_query.filter(
            hostmonitor_report_test.in_ltm.is_(in_ltm_filter))

    runs = runs_query.all()
    runs.sort(key=lambda row: _infra_order(row.infra_name))
    tests = tests_query.order_by(hostmonitor_report_test.is_alert.desc(),
                                 hostmonitor_report_test.in_ltm.desc(),
                                 hostmonitor_report_test.folder_name.asc(),
                                 hostmonitor_report_test.test_name.asc()).all()

    # how stale the reading on screen is, which is the number that matters when
    # the reader has stopped and the tests all still say "good"
    age_minutes = round((_gmt8_now() - newest.run_at).total_seconds() / 60.0, 1) \
        if newest.run_at else None

    return jsonify({
        "run_id": newest.run_id,
        "run_at": newest.run_at.strftime("%Y-%m-%d %H:%M:%S") if newest.run_at else None,
        "triggered_by": newest.triggered_by,
        "age_minutes": age_minutes,
        "alerts_only": alerts_only,
        "infra_filter": infra_filter,
        "in_ltm_filter": in_ltm_filter,
        "infras": [row.serialize for row in runs],
        "total_tests": sum(row.total_tests or 0 for row in runs),
        "alert_count": sum(row.alert_count or 0 for row in runs),
        "ltm_test_count": sum(row.ltm_test_count or 0 for row in runs),
        "not_ltm_test_count": sum(row.not_ltm_test_count or 0 for row in runs),
        "ltm_alert_count": sum(row.ltm_alert_count or 0 for row in runs),
        "not_ltm_alert_count": sum(row.not_ltm_alert_count or 0 for row in runs),
        "tests": [test.serialize for test in tests],
        **_report_meta(),
    }), 200


# **********************************************************************
@hostmonitor_report.route("/hostmonitor_report_history")
@hostmonitor_report.route("/hostmonitor_report_history/")
def hostmonitor_report_history():
    """
    Recent readings, newest first, for the history table under the current one:
    when each ran, whether it worked, and how many tests were alerting.

    Rows are grouped into runs by run_id, so one line covers every infra rather
    than making the reader pair them up by eye. ?limit= is the number of runs,
    not rows; ?infra= narrows to one infra.
    """
    try:
        limit = min(max(int(request.args.get("limit", 100)), 1), 1000)
    except (TypeError, ValueError):
        limit = 100
    infra_filter = request.args.get("infra")

    query = hostmonitor_report_run.query
    if infra_filter:
        query = query.filter(hostmonitor_report_run.infra_name == infra_filter)

    # find the newest `limit` runs, then pull every row belonging to them, so a
    # run is never shown with one of its infras missing
    recent_run_ids = [
        row.run_id for row in
        query.with_entities(hostmonitor_report_run.run_id,
                            db.func.max(hostmonitor_report_run.run_at).label("run_at"))
        .group_by(hostmonitor_report_run.run_id)
        .order_by(db.desc("run_at"))
        .limit(limit)
        .all()
    ]

    rows = []
    if recent_run_ids:
        row_query = hostmonitor_report_run.query.filter(
            hostmonitor_report_run.run_id.in_(recent_run_ids))
        if infra_filter:
            row_query = row_query.filter(
                hostmonitor_report_run.infra_name == infra_filter)
        rows = row_query.order_by(hostmonitor_report_run.run_at.desc()).all()

    runs = {}
    for row in rows:
        run = runs.setdefault(row.run_id, {
            "run_id": row.run_id,
            "run_at": row.run_at.strftime("%Y-%m-%d %H:%M:%S") if row.run_at else None,
            "triggered_by": row.triggered_by,
            "total_tests": 0,
            "alert_count": 0,
            "ltm_alert_count": 0,
            "not_ltm_alert_count": 0,
            "infras": [],
        })
        run["infras"].append(row.serialize)
        run["total_tests"] += row.total_tests or 0
        run["alert_count"] += row.alert_count or 0
        run["ltm_alert_count"] += row.ltm_alert_count or 0
        run["not_ltm_alert_count"] += row.not_ltm_alert_count or 0

    ordered = sorted(runs.values(), key=lambda run: run["run_at"] or "", reverse=True)
    for run in ordered:
        run["infras"].sort(key=lambda each: _infra_order(each["infra_name"]))
        # a run is only "ok" if every infra in it was read; an infra with no
        # path configured is not a failure of the run
        statuses = {each["status"] for each in run["infras"]}
        if statuses <= {"not_configured"}:
            run["status"] = "not_configured"
        elif statuses <= {"ok", "not_configured"}:
            run["status"] = "ok"
        elif "ok" in statuses:
            run["status"] = "partial"
        else:
            run["status"] = "error"

    return jsonify({
        "runs": ordered,
        "returned_runs": len(ordered),
        "limit": limit,
        "infra_filter": infra_filter,
        **_report_meta(),
    }), 200


# **********************************************************************
@hostmonitor_report.route("/health/hostmonitor_report")
@hostmonitor_report.route("/health/hostmonitor_report/")
def hostmonitor_report_health():
    """
    Whether each infra's report is being read, for the banner above the table.

    Unhealthy (503) once an infra's last successful read is older than
    HOSTMONITOR_REPORT_MAX_DATA_AGE_MINUTES -- the case where the page is
    showing real-looking test results that stopped being true hours ago. An
    infra with no path configured is reported as its own state and is not a
    failure: there is nothing broken to fix.
    """
    max_age = current_app.config["HOSTMONITOR_REPORT_MAX_DATA_AGE_MINUTES"]
    now = _gmt8_now()
    infra_names = list(DevConfig.INFRA_NAMES)

    problems = []
    infras = []
    for infra_name in infra_names:
        last_run = (hostmonitor_report_run.query
                    .filter_by(infra_name=infra_name)
                    .order_by(hostmonitor_report_run.run_at.desc(),
                              hostmonitor_report_run.id.desc())
                    .first())
        last_success = (hostmonitor_report_run.query
                        .filter_by(infra_name=infra_name, status="ok")
                        .order_by(hostmonitor_report_run.run_at.desc(),
                                  hostmonitor_report_run.id.desc())
                        .first())

        age_minutes = None
        if last_success is None:
            state = "never_run" if last_run is None else "error"
            problems.append(f"{infra_name}: the report has never been read successfully")
        else:
            age_minutes = round((now - last_success.run_at).total_seconds() / 60.0, 1)
            if age_minutes > max_age:
                state = "stale"
                problems.append(
                    f"{infra_name}: the last successful read was {age_minutes} "
                    f"minutes ago, over the {max_age} minute limit")
            elif last_run is not None and last_run.status != "ok":
                # fresh enough data behind a failing read is a warning, not an
                # outage: say so without failing the health check
                state = "degraded"
            else:
                state = "ok"

        infras.append({
            "infra_name": infra_name,
            "state": state,
            "age_minutes": age_minutes,
            "last_run": last_run.serialize if last_run else None,
            "last_success_at": last_success.run_at.strftime("%Y-%m-%d %H:%M:%S")
                               if last_success else None,
        })

    payload = {
        "healthy": not problems,
        "problems": problems,
        "checked_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "infras": infras,
        **_report_meta(),
    }
    if problems:
        logging.warning(f"/health/hostmonitor_report is unhealthy: {problems}")
    return jsonify(payload), (200 if not problems else 503)


# **********************************************************************
def _infra_order(infra_name):
    names = list(DevConfig.INFRA_NAMES)
    return names.index(infra_name) if infra_name in names else len(names)


# **********************************************************************
def _report_meta():
    return {
        "hostmonitor_ip": current_app.config.get("HOSTMONITOR_REPORT_IP"),
        "infra_names": list(DevConfig.INFRA_NAMES),
        "scheduler_enabled": False,
        "poll_interval_minutes": current_app.config.get(
            "HOSTMONITOR_REPORT_POLL_INTERVAL_MINUTES"),
        "retention_days": current_app.config.get(
            "HOSTMONITOR_REPORT_HISTORY_RETENTION_DAYS"),
        "max_data_age_minutes": current_app.config.get(
            "HOSTMONITOR_REPORT_MAX_DATA_AGE_MINUTES"),
        "next_run_at": None,
    }
