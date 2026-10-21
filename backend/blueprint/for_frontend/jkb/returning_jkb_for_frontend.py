from flask import Flask,Blueprint,request,jsonify
import json
from model import db,hostmonitor_alert_summary,hostmonitor_alert_detail,prtg_summary_data,prtg_alert_current,jkb_infra_summary,jkb_alert_detail
import datetime
import random, string, json, re

returning_jkb_for_frontend = Blueprint("returning_jkb_for_frontend", __name__)




@returning_jkb_for_frontend.route('/sending_jkb_info_to_frontend_for_each_infra/<string:infra_name>')
def sending_jkb_info_to_frontend_for_each_infra(infra_name):
    """
    Fetches the most recent summary for the specified infra.
    
    - It returns the most recent summary if found.
    - If no data exists for that infra, it now returns a 404 Not Found error.
    """
    try:
        # Query for the most recent record matching the infra_name.
        latest_summary = db.session.query(jkb_infra_summary).filter(jkb_infra_summary.infra_name == infra_name).order_by(jkb_infra_summary.timestamp.desc()).first()
        
        # If a record is found in the database, serialize and return it.
        if latest_summary:
            return jsonify({
                "status": "success",
                "data": [latest_summary.serialize]
            })
        
        # --- THIS IS THE MODIFIED LOGIC ---
        # If no record is found (latest_summary is None), return a 404 error.
        else:
            return jsonify({
                "status": "error",
                "message": f"No summary data found for infrastructure: '{infra_name}'"
            }), 404
            
    except Exception as e:
        # It's good practice to have a general exception handler for unexpected database errors.
        logging.error(f"Error fetching infra summary for {infra_name}: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred."
        }), 500
