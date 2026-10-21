
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.sqltypes import TIMESTAMP
db = SQLAlchemy()


def utc_8():
    return datetime.utcnow() + timedelta(hours=8)

# ***************************************************
class hostmonitor_alert_summary(db.Model):
    __tablename__ = "hostmonitor_alert_summary"
    id = db.Column(db.Integer, primary_key=True)
    timestamp=db.Column(db.DateTime)
    alert_percentage=db.Column(db.String(255))
    number_of_total_alerts=db.Column(db.String(255))
    number_of_alerts_in_ltm=db.Column(db.String(255))
    number_of_alerts_not_in_ltm=db.Column(db.String(255))
    total_sensor_for_this_infra=db.Column(db.String(255))
    infra_name=db.Column(db.String(255))
    hostmonitor_ip=db.Column(db.String(255))
    
   
    

    @property
    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "alert_percentage": self.alert_percentage,
            "number_of_total_alerts": self.number_of_total_alerts,
            "number_of_alerts_in_ltm": self.number_of_alerts_in_ltm,
            "number_of_alerts_not_in_ltm": self.number_of_alerts_not_in_ltm,
            "total_sensor_for_this_infra": self.total_sensor_for_this_infra,
            "infra_name": self.infra_name,
            "hostmonitor_ip": self.hostmonitor_ip
        }
        
        
    @property
    def serialize_for_frontend(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "number_of_alerts_in_ltm": self.number_of_alerts_in_ltm,
            "number_of_alerts_not_in_ltm": self.number_of_alerts_not_in_ltm,
            "total_sensor_for_this_infra": self.total_sensor_for_this_infra,
            "infra_name": self.infra_name,
            "hostmonitor_ip": self.hostmonitor_ip
        }        
        
        
        
class hostmonitor_alert_detail(db.Model):
    __tablename__ = "hostmonitor_alert_detail"
    id = db.Column(db.Integer, primary_key=True)
    timestamp=db.Column(db.DateTime)
    infra_name=db.Column(db.String(255))
    in_ltm_or_not_in_ltm=db.Column(db.String(255))
    alert_name=db.Column(db.String(255))
    hostmonitor_ip=db.Column(db.String(255))
   
    

    @property
    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "infra_name": self.infra_name,
            "in_ltm_or_not_in_ltm": self.in_ltm_or_not_in_ltm,
            "alert_name": self.alert_name,
            "hostmonitor_ip": self.hostmonitor_ip
        }
        
        
        
        

# *********************************************************
class alert_for_bu_from_hm82_reports(db.Model):
    """
    Stores the summary count of alerts per infrastructure for each fetch operation.
    """
    __tablename__ = "alert_for_bu_from_hm82_reports"
    
    id = db.Column(db.Integer, primary_key=True)
    # The timestamp links this summary to a specific fetch operation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    bu_which_has_alert_on_hm82 = db.Column(db.String(50), nullable=False)

    @property
    def serialize(self):
        """Return object data in a easily serializable format"""
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "bu_which_has_alert_on_hm82": self.bu_which_has_alert_on_hm82,
        }

        
        
        
        
        
# ******************************************
class prtg_summary_data(db.Model):
    __tablename__ = "prtg_summary_data"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    infra_name = db.Column(db.String(255))
    sensor_id = db.Column(db.Integer)
    lastvalue = db.Column(db.String(64))
    down_count = db.Column(db.Integer)
    prtg_link = db.Column(db.String(64))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "infra_name": self.infra_name,
            "sensor_id": self.sensor_id,
            "lastvalue": self.lastvalue,
            "down_count": self.down_count,
            "prtg_link": self.prtg_link
        }        
        
        
    @property
    def serialize_for_sending_prtg_data_to_frontend(self):
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "sensor_id": self.sensor_id,
            "infra_name": self.infra_name,
            "lastvalue": self.lastvalue,
            "down_count": self.down_count,
        }              
        
        
        
class prtg_alert_current(db.Model):
    __tablename__ = "prtg_alert_current"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    title = db.Column(db.String(2550))
    sensor_id = db.Column(db.String(255))
    whicih_infra = db.Column(db.String(255))


    @property
    def serialize(self):
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "title":self.title,
            "sensor_id":self.sensor_id,
            "whicih_infra":self.whicih_infra,

        }        
        
        
# *********************************************************  
class jkb_alert_detail(db.Model):
    """
    Stores the detailed information for each individual alert fetched from the service.
    """
    __tablename__ = "jkb_alert_details"
    
    id = db.Column(db.Integer, primary_key=True)
    # Record when this alert was fetched and stored in our database
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # --- Columns from the alert data ---
    infra_name = db.Column(db.String(50), nullable=False, index=True)
    group_name = db.Column(db.String(100), index=True)
    task_name = db.Column(db.String(500))
    task_summary = db.Column(db.String(500))
    link_for_snapshot = db.Column(db.String(500))

    @property
    def serialize(self):
        """Return object data in a easily serializable format"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "belong_to_which_infra": self.infra_name,
            "group_name": self.group_name,
            "task_name": self.task_name,
            "task_summary": self.task_summary,
            "link_for_snapshot": self.link_for_snapshot
        }



# *********************************************************
class jkb_infra_summary(db.Model):
    """
    Stores the summary count of alerts per infrastructure for each fetch operation.
    """
    __tablename__ = "jkb_infra_summary"
    
    id = db.Column(db.Integer, primary_key=True)
    # The timestamp links this summary to a specific fetch operation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    infra_name = db.Column(db.String(50), nullable=False)
    alert_count = db.Column(db.Integer, nullable=False)

    @property
    def serialize(self):
        """Return object data in a easily serializable format"""
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "infra_name": self.infra_name,
            "alert_count": self.alert_count
        }




# *********************************************************
from sqlalchemy import DateTime, Integer, String, Text, Boolean
from datetime import datetime
class prtg_current_settings_v2(db.Model):
    """
    Stores the current trigger settings for PRTG sensors BEFORE making any changes.
    This serves as a backup/audit trail of the original configuration.
    All timestamps are stored in GMT+8.
    """
    __tablename__ = "prtg_current_settings_v2"
    
    id = db.Column(Integer, primary_key=True)
    # The timestamp when these settings were captured (before update) - stored in GMT+8
    timestamp = db.Column(DateTime, nullable=False, index=True)
    
    # Infrastructure and device information
    infra_name = db.Column(String(50), nullable=False, index=True)
    device_id = db.Column(Integer, nullable=False, index=True)
    
    # Sensor information
    sensor_id = db.Column(Integer, nullable=False, index=True)
    sensor_name = db.Column(String(255), nullable=True)
    device_name = db.Column(String(255), nullable=True)
    
    # Trigger information
    sub_id = db.Column(Integer, nullable=False)  # The trigger sub-ID (1, 2, 3, etc.)
    trigger_type = db.Column(String(50), nullable=True)  # speed, state, threshold, etc.
    
    # Current notification settings (BEFORE change)
    current_trigger_notification_id = db.Column(String(1024), nullable=True)  # onnotificationid
    current_recovery_notification_id = db.Column(String(1024), nullable=True)  # offnotificationid
    
    # Current trigger configuration (BEFORE change)
    current_channel = db.Column(String(255), nullable=True)
    current_condition = db.Column(String(100), nullable=True)
    current_threshold = db.Column(String(100), nullable=True)
    current_latency = db.Column(String(50), nullable=True)
    
    # Additional trigger-type specific settings
    current_unitsize = db.Column(String(50), nullable=True)  # For speed triggers
    current_unittime = db.Column(String(50), nullable=True)  # For speed triggers
    current_period = db.Column(String(50), nullable=True)    # For volume triggers
    current_changetype = db.Column(String(50), nullable=True)  # For change triggers
    
    # Store the complete original trigger data as JSON for reference
    original_trigger_json = db.Column(Text, nullable=True)

    def __init__(self, **kwargs):
        """Initialize with GMT+8 timestamp if not provided"""
        if 'timestamp' not in kwargs:
            gmt8_tz = pytz.timezone('Asia/Singapore')  # GMT+8
            kwargs['timestamp'] = datetime.now(gmt8_tz).replace(tzinfo=None)
        super().__init__(**kwargs)

    @property
    def serialize(self):
        """Return object data in easily serializable format with GMT+8 indication"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") + " GMT+8",
            "infra_name": self.infra_name,
            "device_id": self.device_id,
            "sensor_id": self.sensor_id,
            "sensor_name": self.sensor_name,
            "device_name": self.device_name,
            "sub_id": self.sub_id,
            "trigger_type": self.trigger_type,
            "current_trigger_notification_id": self.current_trigger_notification_id,
            "current_recovery_notification_id": self.current_recovery_notification_id,
            "current_channel": self.current_channel,
            "current_condition": self.current_condition,
            "current_threshold": self.current_threshold,
            "current_latency": self.current_latency,
            "current_unitsize": self.current_unitsize,
            "current_unittime": self.current_unittime,
            "current_period": self.current_period,
            "current_changetype": self.current_changetype
        }

    @property
    def timestamp_gmt8_str(self):
        """Return timestamp as GMT+8 formatted string"""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S") + " GMT+8"

# *********************************************************
class jkb_all_sensor_status(db.Model):
    """
    One row per monitoring task of the (made-up) website-probe service.
    """
    __tablename__ = "jkb_all_sensor_status"

    id = db.Column(db.Integer, primary_key=True)
    # when this row was pulled from the JKB API (GMT+8)
    timestamp = db.Column(db.DateTime, default=utc_8, nullable=False, index=True)

    # --- identity ---
    task_id = db.Column(db.String(255), index=True)
    task_name = db.Column(db.String(255))
    task_summary = db.Column(db.String(500))
    task_type = db.Column(db.String(255))
    group_id = db.Column(db.String(255), index=True)
    # task_summary with scheme, port and path stripped off
    monitor_target = db.Column(db.String(255))

    # --- status ---
    # 1 = running, 3 = paused
    paused_or_started = db.Column(db.String(255))
    # 2 = the alert threshold was hit
    two_means_hit_threshold = db.Column(db.String(255))
    # newer JKB fields: the coloured button shown in the JKB UI
    status_led = db.Column(db.String(255), index=True)
    status_led_str = db.Column(db.String(255))

    # --- last check ---
    last_resp_status = db.Column(db.String(255))
    last_resp_result = db.Column(db.String(255))
    last_resp_time = db.Column(db.String(255))
    last_check_time = db.Column(db.String(255))
    last_check_time_readable = db.Column(db.DateTime)
    last_monitor_count = db.Column(db.String(255))
    last_monitor_abnormal_count = db.Column(db.String(255))

    # --- misc ---
    partition_flag = db.Column(db.String(255))
    frequency = db.Column(db.String(255))
    network_protocol = db.Column(db.String(255))
    link_for_snapshot = db.Column(db.String(500))

    # --- classification, filled in by blueprint/jkb/a03_classify.py ---
    # the country the probe group maps to, e.g. "Thailand"
    group_name = db.Column(db.String(255), index=True)
    # monitor_target resolved to an address
    monitor_target_ip = db.Column(db.String(255))
    # which infrastructure the target belongs to, e.g. "Charlie"
    belong_to_which_infra = db.Column(db.String(255), index=True)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "task_summary": self.task_summary,
            "task_type": self.task_type,
            "group_id": self.group_id,
            "monitor_target": self.monitor_target,
            "paused_or_started": self.paused_or_started,
            "two_means_hit_threshold": self.two_means_hit_threshold,
            "status_led": self.status_led,
            "status_led_str": self.status_led_str,
            "last_resp_status": self.last_resp_status,
            "last_resp_result": self.last_resp_result,
            "last_resp_time": self.last_resp_time,
            "last_check_time": self.last_check_time,
            "last_check_time_readable": f"{self.last_check_time_readable}",
            "last_monitor_count": self.last_monitor_count,
            "last_monitor_abnormal_count": self.last_monitor_abnormal_count,
            "partition_flag": self.partition_flag,
            "frequency": self.frequency,
            "network_protocol": self.network_protocol,
            "link_for_snapshot": self.link_for_snapshot,
            "group_name": self.group_name,
            "monitor_target_ip": self.monitor_target_ip,
            "belong_to_which_infra": self.belong_to_which_infra,
        }

    @property
    def serialize_for_alert_feed(self):
        """
        The five fields the alert feed shows.
        """
        return {
            "task_name": self.task_name,
            "task_summary": self.task_summary,
            "group_name": self.group_name,
            "belong_to_which_infra": self.belong_to_which_infra,
            "link_for_snapshot": self.link_for_snapshot,
        }


# *********************************************************
class monitor_group(db.Model):
    """
    Probe groups of the website-probe service.

    JKB names its groups after the probe location ("South_East_Asia_TH_Probe"),
    which is not what we want on a dashboard, so each row also carries the
    display name the frontend shows.
    """
    __tablename__ = "monitor_group"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(255), index=True)
    group_name = db.Column(db.String(255))
    convert_to_the_name_i_want_to_show_in_frontend = db.Column(db.String(255))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "convert_to_the_name_i_want_to_show_in_frontend": self.convert_to_the_name_i_want_to_show_in_frontend,
        }


# *********************************************************
class pagerduty_poll_status(db.Model):
    """
    One row per PagerDuty poll attempt outcome, so the dashboard can tell
    "no alerts" apart from "the poller is dead".

    Only the latest row per infra matters, so the table is upserted rather than
    appended to; it stays two rows wide (one per infra) no matter how long the
    poller runs. `last_success_at` is deliberately kept across a failure, which
    is what lets the frontend say how stale the data it is showing actually is.
    """
    __tablename__ = "pagerduty_poll_status"

    id = db.Column(db.Integer, primary_key=True)
    infra_name = db.Column(db.String(255), unique=True, index=True)
    service_id = db.Column(db.String(64))
    # 'ok' | 'error' | 'not_configured'
    status = db.Column(db.String(32))
    # when the poller last finished a run for this infra, success or not
    last_run_at = db.Column(db.DateTime)
    # when it last finished a run that actually wrote data
    last_success_at = db.Column(db.DateTime)
    alert_count = db.Column(db.Integer, default=0)
    # how the last run was started: 'scheduler' or 'manual'
    triggered_by = db.Column(db.String(32))
    duration_seconds = db.Column(db.Float)
    error_message = db.Column(db.String(1024))

    @property
    def serialize(self):
        return {
            "infra_name": self.infra_name,
            "service_id": self.service_id,
            "status": self.status,
            "last_run_at": self.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_run_at else None,
            "last_success_at": self.last_success_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_success_at else None,
            "alert_count": self.alert_count,
            "triggered_by": self.triggered_by,
            "duration_seconds": round(self.duration_seconds, 2) if self.duration_seconds is not None else None,
            "error_message": self.error_message,
        }


# *********************************************************
class pagerduty_poll_history(db.Model):
    """
    One row per infra per poll run, appended rather than upserted, so the
    history page can show what the poller has actually been doing over time.

    pagerduty_poll_status answers "is it healthy right now" in two rows and is
    what the banner reads; this answers "has it been healthy" and is what the
    history page reads. Rows older than PAGERDUTY_HISTORY_RETENTION_DAYS are
    pruned at the end of each run -- at a one minute interval this table grows
    by about 2,900 rows a day, so it does not get to grow forever.
    """
    __tablename__ = "pagerduty_poll_history"

    id = db.Column(db.Integer, primary_key=True)
    # groups the rows written by a single run, so the page can show one line
    # per run with both infras on it
    run_id = db.Column(db.String(36), index=True)
    run_at = db.Column(db.DateTime, index=True)
    infra_name = db.Column(db.String(255), index=True)
    service_id = db.Column(db.String(64))
    # 'ok' | 'error' | 'not_configured'
    status = db.Column(db.String(32))
    # the HTTP status the run as a whole answered with: 200 ok, 207 partial,
    # 500/503 failed. Stored per row so a row is readable on its own.
    http_status_code = db.Column(db.Integer)
    alert_count = db.Column(db.Integer)
    triggered_by = db.Column(db.String(32))
    duration_seconds = db.Column(db.Float)
    error_message = db.Column(db.String(1024))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "run_at": self.run_at.strftime("%Y-%m-%d %H:%M:%S") if self.run_at else None,
            "infra_name": self.infra_name,
            "service_id": self.service_id,
            "status": self.status,
            "http_status_code": self.http_status_code,
            "alert_count": self.alert_count,
            "triggered_by": self.triggered_by,
            "duration_seconds": round(self.duration_seconds, 2) if self.duration_seconds is not None else None,
            "error_message": self.error_message,
        }


# *********************************************************
class hostmonitor_report_run(db.Model):
    """
    One row per infra per read of the HostMonitor HTML reports: when we read
    it, what the report itself said it was generated at, and the counts it
    carried. One run covers every infra, and its rows share a run_id.

    Appended rather than upserted. The newest row is what the frontend shows as
    "now", and the rest is the history behind it -- which is the only way to
    tell "Delta is quiet" apart from "nobody has read the report since Tuesday".
    Rows past HOSTMONITOR_REPORT_HISTORY_RETENTION_DAYS are pruned at the end
    of each run, together with their hostmonitor_report_test rows.
    """
    __tablename__ = "hostmonitor_report_run"

    id = db.Column(db.Integer, primary_key=True)
    # ties this run to its hostmonitor_report_test rows
    # one run reads every infra's report, so its rows share a run_id
    run_id = db.Column(db.String(36), index=True)
    # when we read the file (GMT+8, like every other timestamp here)
    run_at = db.Column(db.DateTime, index=True)
    infra_name = db.Column(db.String(255), index=True)
    hostmonitor_ip = db.Column(db.String(255), index=True)
    # where it was read from, so a run is readable after the path is changed
    report_path = db.Column(db.String(512))
    # 'ok' | 'error' | 'not_configured'
    status = db.Column(db.String(32))
    # 'scheduler' or 'manual'
    triggered_by = db.Column(db.String(32))
    duration_seconds = db.Column(db.Float)

    # the "Generated on ..." line in the report. Distinct from run_at: the gap
    # between them is how stale HostMonitor's own file is, which is a failure
    # we cannot see from run_at alone.
    report_generated_at = db.Column(db.DateTime)
    total_tests = db.Column(db.Integer, default=0)
    # tests whose status class is a live problem (Bad/BadAck/Unknown/UnknAck)
    alert_count = db.Column(db.Integer, default=0)
    # the same split the dashboard card shows: a test named after a load
    # balancer object (Po.../VS...) is on the LTM, anything else is not
    ltm_test_count = db.Column(db.Integer, default=0)
    not_ltm_test_count = db.Column(db.Integer, default=0)
    ltm_alert_count = db.Column(db.Integer, default=0)
    not_ltm_alert_count = db.Column(db.Integer, default=0)
    # the report's own footer counts, kept as reported rather than recomputed
    good_count = db.Column(db.Integer, default=0)
    bad_count = db.Column(db.Integer, default=0)
    unknown_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.String(1024))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "run_at": self.run_at.strftime("%Y-%m-%d %H:%M:%S") if self.run_at else None,
            "infra_name": self.infra_name,
            "hostmonitor_ip": self.hostmonitor_ip,
            "report_path": self.report_path,
            "status": self.status,
            "triggered_by": self.triggered_by,
            "duration_seconds": round(self.duration_seconds, 2) if self.duration_seconds is not None else None,
            "report_generated_at": self.report_generated_at.strftime("%Y-%m-%d %H:%M:%S") if self.report_generated_at else None,
            "total_tests": self.total_tests,
            "alert_count": self.alert_count,
            "ltm_test_count": self.ltm_test_count,
            "not_ltm_test_count": self.not_ltm_test_count,
            "ltm_alert_count": self.ltm_alert_count,
            "not_ltm_alert_count": self.not_ltm_alert_count,
            "good_count": self.good_count,
            "bad_count": self.bad_count,
            "unknown_count": self.unknown_count,
            "error_message": self.error_message,
        }


# *********************************************************
class hostmonitor_report_test(db.Model):
    """
    One row per test in one read of one infra's report -- the parsed contents
    of a single <input> button, including what its onclick popup would have
    said.

    Kept per run rather than overwritten so the detail behind a past run is
    still there when someone asks what was down at 2am.
    """
    __tablename__ = "hostmonitor_report_test"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(36), index=True)
    run_at = db.Column(db.DateTime, index=True)
    infra_name = db.Column(db.String(255), index=True)
    hostmonitor_ip = db.Column(db.String(255))
    # the HostMonitor folder the test sits in, e.g. all_Delta_alert_for_albert_outage_tool
    folder_name = db.Column(db.String(255), index=True)
    test_name = db.Column(db.String(512))
    # the button's CSS class, which is how the report encodes state:
    # Good/Bad/Unknown/BadAck/UnknAck/Disabled/NotTested/...
    status_class = db.Column(db.String(32), index=True)
    # the "Status:" line from the popup, e.g. 'no answer'. Free text from
    # HostMonitor, so it is shown but never matched on.
    status_text = db.Column(db.String(255))
    # how many consecutive times the test has been in this state
    recurrences = db.Column(db.Integer)
    reply = db.Column(db.String(512))
    # True for the classes that mean something is actually wrong
    is_alert = db.Column(db.Boolean, default=False)
    # True when the test watches an LTM object -- see is_ltm_sensor()
    in_ltm = db.Column(db.Boolean, default=False, index=True)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "run_at": self.run_at.strftime("%Y-%m-%d %H:%M:%S") if self.run_at else None,
            "infra_name": self.infra_name,
            "hostmonitor_ip": self.hostmonitor_ip,
            "folder_name": self.folder_name,
            "test_name": self.test_name,
            "status_class": self.status_class,
            "status_text": self.status_text,
            "recurrences": self.recurrences,
            "reply": self.reply,
            "is_alert": bool(self.is_alert),
            "in_ltm": bool(self.in_ltm),
        }


# *********************************************************
class jkb_poll_status(db.Model):
    """
    One row per infra describing what the JKB pipeline last managed to do, so
    the dashboard can tell "no alerts" apart from "the poller is dead".

    Same contract as pagerduty_poll_status: upserted rather than appended to,
    and last_success_at survives a failure, which is what lets the banner say
    how old the zero on the card actually is.
    """
    __tablename__ = "jkb_poll_status"

    id = db.Column(db.Integer, primary_key=True)
    infra_name = db.Column(db.String(255), unique=True, index=True)
    # 'ok' | 'error' | 'no_sensors'
    status = db.Column(db.String(32))
    last_run_at = db.Column(db.DateTime)
    last_success_at = db.Column(db.DateTime)
    alert_count = db.Column(db.Integer, default=0)
    # how many sensors the classifier placed in this infra. Zero means the
    # alert count is an "unknown", not a "healthy".
    sensor_count = db.Column(db.Integer, default=0)
    triggered_by = db.Column(db.String(32))
    duration_seconds = db.Column(db.Float)
    error_message = db.Column(db.String(1024))

    @property
    def serialize(self):
        return {
            "infra_name": self.infra_name,
            "status": self.status,
            "last_run_at": self.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_run_at else None,
            "last_success_at": self.last_success_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_success_at else None,
            "alert_count": self.alert_count,
            "sensor_count": self.sensor_count,
            "triggered_by": self.triggered_by,
            "duration_seconds": round(self.duration_seconds, 2) if self.duration_seconds is not None else None,
            "error_message": self.error_message,
        }


# *********************************************************
class jkb_poll_history(db.Model):
    """
    One row per pipeline step per run, appended, so the history page can show
    what each query answered rather than only whether the run as a whole worked.

    The JKB pipeline is three HTTP-ish calls that depend on each other
    (fetch_sensors -> classify -> build_alerts), and a run can succeed at the
    first and fail at the second. A single status per run would hide that, so
    the step is the row and http_status_code is per step. `run_http_status_code`
    is the code the run as a whole answered with, repeated on every row so a row
    still reads on its own.

    Rows older than JKB_HISTORY_RETENTION_DAYS are pruned at the end of a run.
    """
    __tablename__ = "jkb_poll_history"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(36), index=True)
    run_at = db.Column(db.DateTime, index=True)
    # 'fetch_sensors' | 'classify' | 'build_alerts'
    step = db.Column(db.String(64), index=True)
    # the order the steps run in, so the page never has to guess it
    step_order = db.Column(db.Integer)
    # 'ok' | 'error' | 'skipped' (an earlier step failed, so this never ran)
    status = db.Column(db.String(32))
    http_status_code = db.Column(db.Integer)
    run_http_status_code = db.Column(db.Integer)
    triggered_by = db.Column(db.String(32))
    duration_seconds = db.Column(db.Float)
    # what the step wrote, in its own terms: sensors pulled, sensors classified,
    # alerts stored. Free text because each step counts a different thing.
    detail = db.Column(db.String(512))
    error_message = db.Column(db.String(1024))
    # the run's per-infra alert counts as JSON, written on every row of the run
    alert_count_by_infra = db.Column(db.String(512))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "run_at": self.run_at.strftime("%Y-%m-%d %H:%M:%S") if self.run_at else None,
            "step": self.step,
            "step_order": self.step_order,
            "status": self.status,
            "http_status_code": self.http_status_code,
            "run_http_status_code": self.run_http_status_code,
            "triggered_by": self.triggered_by,
            "duration_seconds": round(self.duration_seconds, 2) if self.duration_seconds is not None else None,
            "detail": self.detail,
            "error_message": self.error_message,
        }
