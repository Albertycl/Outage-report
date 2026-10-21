from flask import Flask,Blueprint,request,jsonify
import json
from model import db,hostmonitor_alert_summary,hostmonitor_alert_detail,prtg_summary_data,prtg_alert_current
import datetime
import random, string, json, re

returning_prtg_for_frontend = Blueprint("returning_prtg_for_frontend", __name__)

@returning_prtg_for_frontend.route('/sending_prtg_info_to_frontend_for_each_infra')
@returning_prtg_for_frontend.route('/sending_prtg_info_to_frontend_for_each_infra/<string:infra_name>')
def sending_prtg_info_to_frontend_for_each_infra(infra_name=None):
    """
    Retrieves PRTG summary data. If an infra_name is provided, it filters
    the results; otherwise, it returns all records.
    """
    try:
        # 1. Start with a base query for the prtg_summary_data table.
        query = prtg_summary_data.query

        # 2. If an infra_name was passed in the URL, add a filter to the query.
        if infra_name:
            query = query.filter_by(infra_name=infra_name)

        # 3. Execute the query to get the list of results.
        results = query.all()

        # 4. If a specific infra_name was requested but no data was found, return a 404 error.
        if infra_name and not results:
            return jsonify({
                "error": f"No PRTG data found for infra_name '{infra_name}'"
            }), 404

        # 5. Use the serializer property you provided to format each result object.
        serialized_data = [
            item.serialize_for_sending_prtg_data_to_frontend for item in results
        ]

        # 6. Return the final data as a JSON response.
        return jsonify(data=serialized_data)

    except Exception as e:
        # 7. A general error handler for database issues or other unexpected problems.
        # It's a good practice to log the error for debugging.
        # e.g., current_app.logger.error(f"Error in sending_prtg_info_to_frontend: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500