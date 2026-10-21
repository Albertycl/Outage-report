"""
PRTG alert status endpoints (read-only, demo).

Concept demo: nothing here calls PRTG or PagerDuty. The status rows are plain
tables filled from demo/seed_demo_data.sql, and these routes only read them.
"""

from flask import Blueprint, current_app, jsonify, request
import logging
from datetime import datetime, timedelta

from config import DevConfig
from model import db, pagerduty_poll_status, pagerduty_poll_history

prtg_alerts = Blueprint("prtg_alerts", __name__)

logging.basicConfig(level=logging.INFO)

ALL_INFRAS = list(DevConfig.INFRA_NAMES)

IDLE_RUN = {"running": False, "started_at": None, "triggered_by": None,
            "running_for_seconds": None}


def _gmt8_now():
    return datetime.utcnow() + timedelta(hours=8)


# **********************************************************************
@prtg_alerts.route("/health/prtg_alerts")
@prtg_alerts.route("/health/prtg_alerts/")
def prtg_alerts_health():
    """
    What the status feed last did, per infra, for the dashboard's status panel.

    Unhealthy when any configured infra has no successful poll inside
    PAGERDUTY_MAX_DATA_AGE_MINUTES: that is the case where the numbers on
    screen are stale but still look like real readings. Returns 503 then, so a
    plain uptime check catches it too.
    """
    max_age = current_app.config["PAGERDUTY_MAX_DATA_AGE_MINUTES"]
    now = _gmt8_now()

    rows = {row.infra_name: row for row in pagerduty_poll_status.query.all()}

    infras = []
    problems = []
    for infra_name in ALL_INFRAS:
        row = rows.get(infra_name)
        entry = {
            "infra_name": infra_name,
            }

        if row is None:
            entry.update({
                "status": "never_run",
                "age_minutes": None,
                "alert_count": None,
                "last_run_at": None,
                "last_success_at": None,
                "error_message": None,
            })
            problems.append(f"{infra_name}: the status feed has never run")
        else:
            age = ((now - row.last_success_at).total_seconds() / 60.0
                   if row.last_success_at else None)
            entry.update(row.serialize)
            entry["age_minutes"] = round(age, 1) if age is not None else None

            if row.status == "not_configured":
                problems.append(f"{infra_name}: no service configured")
            elif age is None:
                problems.append(f"{infra_name}: no successful poll yet")
            elif age > max_age:
                problems.append(
                    f"{infra_name}: last successful poll was {age:.1f} minutes ago, "
                    f"over the {max_age} minute limit"
                )
            elif row.status == "error":
                # stale-but-fresh-enough data with a failing status feed is a warning,
                # not an outage: say so without failing the health check
                entry["status"] = "degraded"

        infras.append(entry)

    healthy = not problems
    payload = {
        "healthy": healthy,
        "problems": problems,
        "checked_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "max_data_age_minutes": max_age,
        "poll_interval_minutes": current_app.config["PAGERDUTY_POLL_INTERVAL_MINUTES"],
        "scheduler_enabled": current_app.config["PAGERDUTY_SCHEDULER_ENABLED"],
        "infras": infras,
    }
    if not healthy:
        logging.warning(f"/health/prtg_alerts is unhealthy: {problems}")
    return jsonify(payload), (200 if healthy else 503)


# **********************************************************************
@prtg_alerts.route("/prtg_alerts_history")
@prtg_alerts.route("/prtg_alerts_history/")
def prtg_alerts_history():
    """
    Recent poll runs, newest first, for the history page behind the status
    banner: when each run happened, what it answered, how long it took and how
    many alerts it found.

    Rows are grouped into runs by run_id, so one line covers both infras rather
    than making the reader pair them up by eye. ?limit= is the number of runs,
    not rows; ?infra= narrows to one infra.
    """
    try:
        limit = min(max(int(request.args.get("limit", 100)), 1), 1000)
    except (TypeError, ValueError):
        limit = 100
    infra_filter = request.args.get("infra")

    query = pagerduty_poll_history.query
    if infra_filter:
        query = query.filter(pagerduty_poll_history.infra_name == infra_filter)

    # find the newest `limit` runs, then pull every row belonging to them, so a
    # run is never shown with one of its infras missing
    recent_run_ids = [
        row.run_id for row in
        query.with_entities(pagerduty_poll_history.run_id,
                            db.func.max(pagerduty_poll_history.run_at).label("run_at"))
        .group_by(pagerduty_poll_history.run_id)
        .order_by(db.desc("run_at"))
        .limit(limit)
        .all()
    ]

    rows = []
    if recent_run_ids:
        row_query = pagerduty_poll_history.query.filter(
            pagerduty_poll_history.run_id.in_(recent_run_ids))
        if infra_filter:
            row_query = row_query.filter(
                pagerduty_poll_history.infra_name == infra_filter)
        rows = row_query.order_by(pagerduty_poll_history.run_at.desc()).all()

    runs = {}
    for row in rows:
        run = runs.setdefault(row.run_id, {
            "run_id": row.run_id,
            "run_at": row.run_at.strftime("%Y-%m-%d %H:%M:%S") if row.run_at else None,
            "triggered_by": row.triggered_by,
            "http_status_code": row.http_status_code,
            "total_alerts": 0,
            "infras": [],
        })
        run["infras"].append(row.serialize)
        run["total_alerts"] += row.alert_count or 0

    ordered = sorted(runs.values(), key=lambda run: run["run_at"] or "", reverse=True)
    for run in ordered:
        run["infras"].sort(key=lambda each: ALL_INFRAS.index(each["infra_name"])
                           if each["infra_name"] in ALL_INFRAS else 99)
        # a run is only "ok" if every infra in it was
        run["status"] = ("ok" if all(each["status"] == "ok" for each in run["infras"])
                         else "error")

    return jsonify({
        "runs": ordered,
        "returned_runs": len(ordered),
        "limit": limit,
        "infra_filter": infra_filter,
        "retention_days": current_app.config["PAGERDUTY_HISTORY_RETENTION_DAYS"],
        "poll_interval_minutes": current_app.config["PAGERDUTY_POLL_INTERVAL_MINUTES"],
        "scheduler_enabled": current_app.config["PAGERDUTY_SCHEDULER_ENABLED"],
        "max_data_age_minutes": current_app.config["PAGERDUTY_MAX_DATA_AGE_MINUTES"],
        "current_run": dict(IDLE_RUN),
        "next_run_at": None,
    })
