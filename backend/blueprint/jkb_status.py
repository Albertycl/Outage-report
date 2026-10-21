"""
JKB status endpoints (read-only, demo).

Concept demo: nothing here calls JKB. The sensor, alert and status rows are
plain tables filled from demo/seed_demo_data.sql, and these routes only read
them. /health/jkb returns 503 when the rows are missing or older than
JKB_MAX_DATA_AGE_MINUTES, which is the signal an uptime monitor would alert on.
"""

from datetime import datetime
import json
import logging

from flask import Blueprint, current_app, jsonify, request
from backports.zoneinfo import ZoneInfo

from model import (
    db,
    jkb_all_sensor_status,
    jkb_infra_summary,
    jkb_poll_status,
    jkb_poll_history,
)

jkb_status = Blueprint("jkb_status", __name__)

logging.basicConfig(level=logging.INFO)

STEP_NAMES = ["fetch_sensors", "classify", "build_alerts"]

IDLE_RUN = {"running": False, "started_at": None, "triggered_by": None,
            "running_for_seconds": None}


# **********************************************************************
def _taipei_now():
    """The clock the pipeline stamps its rows with."""
    return datetime.now(ZoneInfo("Asia/Taipei")).replace(tzinfo=None)


# **********************************************************************
@jkb_status.route("/health/jkb")
@jkb_status.route("/health/jkb/")
def health_jkb():
    """
    200  everything fresh and every infra covered
    503  never run, stale, or an infra has no classified sensors

    Point a monitor at this and alert on any non-200.

    `infras` is the per-infra detail the dashboard banner shows: the last run's
    outcome, how stale the number on the card is, and the error if there was
    one. It mirrors /health/prtg_alerts so the two banners read the same way.
    """
    max_age_minutes = current_app.config["JKB_MAX_DATA_AGE_MINUTES"]
    infra_names = current_app.config["JKB_INFRA_NAMES"]

    problems = []
    now = _taipei_now()

    # --- freshness -----------------------------------------------------
    latest = db.session.query(db.func.max(jkb_infra_summary.timestamp)).scalar()
    if latest is None:
        problems.append("the JKB alert tables have never been written")
        age_minutes = None
        last_refresh = None
    else:
        age_minutes = round((now - latest).total_seconds() / 60, 1)
        last_refresh = latest.strftime("%Y-%m-%d %H:%M:%S")
        if age_minutes > max_age_minutes:
            problems.append(
                f"last refresh was {age_minutes} minutes ago, "
                f"over the {max_age_minutes} minute limit"
            )

    # --- coverage ------------------------------------------------------
    # counted off the sensor table rather than the summary, because a summary
    # row of 0 is written even when nothing was classified into that infra
    sensors_by_infra = {
        infra_name: jkb_all_sensor_status.query.filter_by(
            belong_to_which_infra=infra_name
        ).count()
        for infra_name in infra_names
    }
    for infra_name, sensor_count in sensors_by_infra.items():
        if sensor_count == 0:
            problems.append(
                f"no sensors are classified as {infra_name}, so its alert count "
                f"is a zero that means 'unknown', not 'healthy'"
            )

    # --- the poller ----------------------------------------------------
    # jkb_poll_status is what the last run wrote. An infra whose data is still
    # inside the freshness window but whose last run failed is 'degraded': the
    # number on the card is old but not yet worth calling stale.
    status_rows = {row.infra_name: row for row in jkb_poll_status.query.all()}

    infras = []
    for infra_name in infra_names:
        row = status_rows.get(infra_name)
        entry = {"infra_name": infra_name,
                 "sensor_count": sensors_by_infra.get(infra_name, 0)}

        if row is None:
            entry.update({
                "status": "never_run",
                "age_minutes": None,
                "alert_count": None,
                "last_run_at": None,
                "last_success_at": None,
                "error_message": None,
            })
            problems.append(f"{infra_name}: the poller has never run")
        else:
            age = ((now - row.last_success_at).total_seconds() / 60.0
                   if row.last_success_at else None)
            entry.update(row.serialize)
            entry["age_minutes"] = round(age, 1) if age is not None else None

            if age is None:
                problems.append(f"{infra_name}: no successful run yet")
            elif age > max_age_minutes:
                problems.append(
                    f"{infra_name}: last successful run was {age:.1f} minutes ago, "
                    f"over the {max_age_minutes} minute limit"
                )
            elif row.status == "error":
                entry["status"] = "degraded"

        infras.append(entry)

    payload = {
        "status": "ok" if not problems else "unhealthy",
        # the PRTG banner reads `healthy`; keep both so one component shape works
        "healthy": not problems,
        "checked_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "last_refresh": last_refresh,
        "age_minutes": age_minutes,
        "max_age_minutes": max_age_minutes,
        "max_data_age_minutes": max_age_minutes,
        "poll_interval_minutes": current_app.config["JKB_POLL_INTERVAL_MINUTES"],
        "scheduler_enabled": current_app.config["JKB_SCHEDULER_ENABLED"],
        "classified_sensors_by_infra": sensors_by_infra,
        "infras": infras,
        "current_run": dict(IDLE_RUN),
        "next_run_at": None,
        "problems": problems,
    }

    if problems:
        logging.warning(f"/health/jkb is unhealthy: {problems}")
        return jsonify(payload), 503
    return jsonify(payload), 200


# **********************************************************************
@jkb_status.route("/jkb_poll_history")
@jkb_status.route("/jkb_poll_history/")
def jkb_poll_history_route():
    """
    Recent runs, newest first, for the history page behind the JKB banner:
    when each run happened, which step it stopped at, and the HTTP status every
    step answered with.

    Rows are grouped into runs by run_id, so one line covers the whole pipeline
    rather than making the reader pair three rows up by eye. ?limit= is the
    number of runs, not rows; ?step= narrows to one step.
    """
    try:
        limit = min(max(int(request.args.get("limit", 100)), 1), 1000)
    except (TypeError, ValueError):
        limit = 100
    step_filter = request.args.get("step")

    query = jkb_poll_history.query
    if step_filter:
        query = query.filter(jkb_poll_history.step == step_filter)

    # find the newest `limit` runs, then pull every row belonging to them, so a
    # run is never shown with one of its steps missing
    recent_run_ids = [
        row.run_id for row in
        query.with_entities(jkb_poll_history.run_id,
                            db.func.max(jkb_poll_history.run_at).label("run_at"))
        .group_by(jkb_poll_history.run_id)
        .order_by(db.desc("run_at"))
        .limit(limit)
        .all()
    ]

    rows = []
    if recent_run_ids:
        row_query = jkb_poll_history.query.filter(
            jkb_poll_history.run_id.in_(recent_run_ids))
        if step_filter:
            row_query = row_query.filter(jkb_poll_history.step == step_filter)
        rows = row_query.order_by(jkb_poll_history.run_at.desc(),
                                  jkb_poll_history.step_order.asc()).all()

    runs = {}
    for row in rows:
        run = runs.setdefault(row.run_id, {
            "run_id": row.run_id,
            "run_at": row.run_at.strftime("%Y-%m-%d %H:%M:%S") if row.run_at else None,
            "triggered_by": row.triggered_by,
            "http_status_code": row.run_http_status_code,
            "alert_count_by_infra": _loads_or_empty(row.alert_count_by_infra),
            "steps": [],
        })
        run["steps"].append(row.serialize)

    ordered = sorted(runs.values(), key=lambda run: run["run_at"] or "", reverse=True)
    for run in ordered:
        run["steps"].sort(key=lambda each: each["step_order"] or 0)
        run["total_alerts"] = sum(run["alert_count_by_infra"].values())
        # a run is only "ok" if every step it ran was, and none were skipped
        run["status"] = ("ok" if all(each["status"] == "ok" for each in run["steps"])
                         else "error")
        run["duration_seconds"] = round(
            sum(each["duration_seconds"] or 0 for each in run["steps"]), 2)
        failed = [each for each in run["steps"] if each["status"] == "error"]
        run["failed_at"] = failed[0]["step"] if failed else None

    return jsonify({
        "runs": ordered,
        "returned_runs": len(ordered),
        "limit": limit,
        "step_filter": step_filter,
        "steps": STEP_NAMES,
        "retention_days": current_app.config["JKB_HISTORY_RETENTION_DAYS"],
        "poll_interval_minutes": current_app.config["JKB_POLL_INTERVAL_MINUTES"],
        "scheduler_enabled": current_app.config["JKB_SCHEDULER_ENABLED"],
        "max_data_age_minutes": current_app.config["JKB_MAX_DATA_AGE_MINUTES"],
        "current_run": dict(IDLE_RUN),
        "next_run_at": None,
    })


# **********************************************************************
def _loads_or_empty(raw):
    """The stored per-infra counts, or {} for a row written before/without them."""
    try:
        return json.loads(raw) if raw else {}
    except (TypeError, ValueError):
        return {}
