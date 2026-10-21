from flask import Flask,Blueprint,request,jsonify
import json
from model import db,hostmonitor_alert_summary,hostmonitor_alert_detail,prtg_summary_data,prtg_alert_current,alert_for_bu_from_hm82_reports
import datetime
import random, string, json, re

returning_hostmonitor_info_for_frontend = Blueprint("returning_hostmonitor_info_for_frontend", __name__)


# =========================================================================================================================

@returning_hostmonitor_info_for_frontend.route('/sending_hostmonitor_to_frontend_for_each_infra')
@returning_hostmonitor_info_for_frontend.route('/sending_hostmonitor_to_frontend_for_each_infra/<string:infra_name>')
def sending_hostmonitor_to_frontend_for_each_infra(infra_name):
    """
    Retrieves host monitor alert summaries filtered by a specific infrastructure name.
    """
    if not infra_name:
        return jsonify({"error": "infra_name parameter is required"}), 400

    try:
        # 1. Query the database using the provided model and filter by infra_name.
        # The .all() executes the query and returns a list of results.
        summaries = hostmonitor_alert_summary.query.filter_by(infra_name=infra_name).all()

        # 2. Handle the case where no records are found for the given infra_name.
        if not summaries:
            return jsonify({
                "error": f"No data found for infra_name '{infra_name}'"
            }), 404

        # 3. Use a list comprehension to serialize each object in the list.
        # This calls the `serialize_for_frontend` property for each item.
        serialized_data = [summary.serialize_for_frontend for summary in summaries]

        # 4. Return the serialized data in a standard JSON format.
        return jsonify(data=serialized_data)

    except Exception as e:
        # 5. Handle potential database errors or other exceptions gracefully.
        # It's good practice to log the error here.
        # import logging
        # logging.error(f"Error fetching hostmonitor summary for {infra_name}: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500




@returning_hostmonitor_info_for_frontend.route('/showing_the_template_and_which_bu_is_impacted_to_frontend')
@returning_hostmonitor_info_for_frontend.route('/showing_the_template_and_which_bu_is_impacted_to_frontend/')
def showing_the_template_and_which_bu_is_impacted_to_frontend():
    """
    Queries the database for impacted BUs and returns formatted incident templates.
    """
    try:
        # 1. Query the database for all unique BU alerts
        # This gets distinct BU names to avoid duplicates like ('SBK',), ('SBK',)
        bu_alerts = db.session.query(alert_for_bu_from_hm82_reports.bu_which_has_alert_on_hm82).distinct().all()

        # 2. Format the list of BUs into a single string
        # The query returns a list of tuples, e.g., [('SBK',), ('NBG',)], so we extract the first item of each tuple.
        impacted_bu_list = [item[0] for item in bu_alerts]
        
        if impacted_bu_list:
            # Join the list into a string like "188A / SBK / NBG"
            impacted_bu_string = " / ".join(impacted_bu_list)
        else:
            # Provide a default message if no alerts are found in the table
            impacted_bu_string = "No impacted services detected at the moment."

    except Exception as e:
        # Handle potential database errors gracefully
        print(f"Database query failed: {e}")
        # Return an error that the frontend can handle
        return jsonify({"error": "A database error occurred while fetching impacted BUs."}), 500

    # 3. Create the incident report templates with the dynamic data
    # The placeholders in [] are kept as requested, for the user to fill in the frontend.
    
    # Template for the initial announcement or a general "still investigating" update
    initial_update_template = f"""Please be informed that we are currently experiencing a service issue.
Issue Type: [brief description, e.g., DDoS attack / system downtime / packet loss]
Current Status: [Under Investigation]
Start Time: [e.g., 21:50 (GMT+8)]
Impacted BU/Services: {impacted_bu_string}
Remarks: The issue is still under investigation.
Next Update: An update will be provided in 15 minutes or as soon as new information becomes available."""


    # A more specific template for when an action is being taken
    action_update_template = f"""Update on the ongoing service issue:
Issue Type: [brief description, e.g., DDoS attack / system downtime / packet loss]
Start Time: [e.g., 21:50 (GMT+8)]
Current Status: [Under Investigation]
Impacted BU/Services: {impacted_bu_string}
Latest Update: [Describe the action, e.g., YT-NET suspects the issue is related to Charlie-LTM and will perform a failover.]
Next Update: Another update will be provided in 15 minutes or as soon as new information becomes available."""

    # Template for when the issue is resolved
    resolution_template = f"""Service Issue Resolved
Issue Type: [brief description, e.g., DDoS attack / system downtime / packet loss]
Start Time: [e.g., 21:50 (GMT+8)]
End Time: [e.g., 23:30 (GMT+8)]
Impacted BU/Services: {impacted_bu_string}
Resolution: [Describe the resolution, e.g., Final confirmation pending. NET team will provide an official summary.]
Current Status: [Resolved]
Thank you for your patience and understanding."""

    # 4. Return all templates in a single JSON object
    return jsonify({
        'status': 'success',
        'templates': {
            'initial_update': initial_update_template,
            'action_update': action_update_template,
            'resolution': resolution_template
        }
    })
