from flask import Flask,Blueprint,request,jsonify
import json
from model import db,hostmonitor_alert_summary,hostmonitor_alert_detail,prtg_summary_data,prtg_alert_current
import datetime
import random, string, json, re

handling_axios = Blueprint("handling_axios", __name__)


# =========================================================================================================================

@handling_axios.route('/showing_hostmonitor_alert_summary')
@handling_axios.route('/showing_hostmonitor_alert_summary/')
def showing_hostmonitor_alert_summary():
    # Sort the results by hostmonitor_ip
    list_all_the_data_in_hostmonitor_alert_summary_table = (
        hostmonitor_alert_summary.query
        .order_by(hostmonitor_alert_summary.hostmonitor_ip)
        .all()
    )

    # Serialize the results
    result = [data.serialize for data in list_all_the_data_in_hostmonitor_alert_summary_table]

    return jsonify(result)


# =========================================================================================================================
@handling_axios.route('/query_hostmonitor_alert_detail/<which_infra>/<hostmonitor_ip>')
def query_hostmonitor_alert_detail(which_infra,hostmonitor_ip):
    
    list_all_the_data_in_hostmonitor_alert_detail_table=hostmonitor_alert_detail.query.filter_by(infra_name=which_infra,hostmonitor_ip=hostmonitor_ip).all()
    print(f'list_all_the_data_in_hostmonitor_alert_detail_table={list_all_the_data_in_hostmonitor_alert_detail_table}')
    list_all_the_data_in_hostmonitor_alert_detail_table = [data.serialize  for data in list_all_the_data_in_hostmonitor_alert_detail_table]
    
    return jsonify(list_all_the_data_in_hostmonitor_alert_detail_table)





# =========================================================================================================================
@handling_axios.route('/frontend_query_prtg_summary')
@handling_axios.route('/frontend_query_prtg_summary/')
def frontend_query_prtg_summary():
    
    list_all_the_data_in_prtg_summary_data_table=prtg_summary_data.query.all()
    list_all_the_data_in_prtg_summary_data_table = [data.serialize  for data in list_all_the_data_in_prtg_summary_data_table]
    return jsonify(list_all_the_data_in_prtg_summary_data_table)






# =========================================================================================================================
@handling_axios.route('/frontend_query_prtg_detail/<string:which_infra>')
def frontend_query_prtg_detail(which_infra):
    records = prtg_alert_current.query.filter_by(whicih_infra=which_infra).all()
    result = [r.serialize for r in records]
    return jsonify(result)
