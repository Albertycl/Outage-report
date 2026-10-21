from flask import jsonify, Blueprint
from sqlalchemy import func

# --- Import your database models and db instance ---
# This assumes they are in a 'model.py' file.
from model import db, jkb_alert_detail, jkb_infra_summary

# --- Create a new Blueprint for these routes ---
jkb_db_routes = Blueprint('jkb_db_routes', __name__)


@jkb_db_routes.route("/get_jkb_alert_details/<string:which_infra>")
@jkb_db_routes.route("/get_jkb_alert_details/<string:which_infra>/")
def get_jkb_alert_details(which_infra):
    """
    Returns all the detailed alert records for a specific infrastructure.
    Example: /get_jkb_alert_details/Charlie
    """
    try:
        # Filter the jkb_alert_detail table by the infra_name from the URL
        alert_details = jkb_alert_detail.query.filter(
            func.upper(jkb_alert_detail.infra_name) == func.upper(which_infra)
        ).all()

        if not alert_details:
            return jsonify({
                "status": "not_found",
                "message": f"No alert details found for infrastructure: {which_infra}"
            }), 404
            
        # Serialize the filtered results using the '.serialize' property from the model
        serialized_data = [row.serialize for row in alert_details]
        return jsonify(serialized_data)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# @jkb_db_routes.route("/get_jkb_infra_summary/infra")
# @jkb_db_routes.route("/get_jkb_infra_summary/infra/")
# def get_jkb_infra_summary():
#     """
#     Returns the latest summary of alert counts for each infrastructure.
#     It works by finding the most recent timestamp and returning all entries
#     that match it.
#     """
#     try:
#         # Step 1: Find the most recent timestamp in the summary table.
#         latest_timestamp = db.session.query(
#             func.max(jkb_infra_summary.timestamp)
#         ).scalar()

#         if not latest_timestamp:
#             return jsonify({
#                 "status": "not_found",
#                 "message": "No infrastructure summary data found."
#             }), 404

#         # Step 2: Fetch all records that match the most recent timestamp.
#         infra_summaries = jkb_infra_summary.query.filter_by(
#             timestamp=latest_timestamp
#         ).all()
        
#         serialized_data = [row.serialize for row in infra_summaries]
#         return jsonify(serialized_data)

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500



