-- Demo data. This app never calls PRTG, PagerDuty, JKB or HostMonitor; every
-- number it shows comes from here. All values are made up; IPs are from the documentation
-- ranges. Re-run it to refresh the timestamps (the health checks go red when
-- the data is older than a few minutes). Times are Asia/Taipei, like the app.
--
-- The backend container runs schema.sql and then this file at start-up
-- (load_sql.py). To re-run by hand:
--   mariadb -u<user> -p outage_report < backend/db/seed_demo_data.sql

SET @now = DATE_ADD(UTC_TIMESTAMP(), INTERVAL 8 HOUR);

DELETE FROM prtg_summary_data;
INSERT INTO prtg_summary_data (timestamp, infra_name, sensor_id, lastvalue, down_count, prtg_link) VALUES
 (@now, 'charlie', 3138, '1842', 2, NULL),
 (@now, 'delta',  4727, '926',  0, NULL);

DELETE FROM prtg_alert_current;
INSERT INTO prtg_alert_current (timestamp, title, sensor_id, whicih_infra) VALUES
 (DATE_SUB(@now, INTERVAL 7 MINUTE), 'Ping Down: edge-gw-01 (192.0.2.11)', '2101', 'charlie'),
 (DATE_SUB(@now, INTERVAL 3 MINUTE), 'HTTP Slow: shop-front (198.51.100.20)', '2144', 'charlie');

DELETE FROM pagerduty_poll_status;
INSERT INTO pagerduty_poll_status (infra_name, service_id, status, last_run_at, last_success_at, alert_count, triggered_by, duration_seconds, error_message) VALUES
 ('charlie', 'PEK31II', 'success', @now, @now, 2, 'demo', 0.4, NULL),
 ('delta',  'PWMLHS3', 'success', @now, @now, 0, 'demo', 0.3, NULL);

DELETE FROM jkb_infra_summary;
INSERT INTO jkb_infra_summary (timestamp, infra_name, alert_count) VALUES
 (@now, 'Charlie', 3),
 (@now, 'Delta', 1);

DELETE FROM jkb_alert_details;
INSERT INTO jkb_alert_details (timestamp, infra_name, group_name, task_name, task_summary, link_for_snapshot) VALUES
 (@now, 'Charlie', 'Web', 'Charlie_https_https://198.51.100.20 (CN)', 'HTTP 502 from 3 of 5 probes', NULL),
 (@now, 'Charlie', 'Web', 'Charlie_tcp_203.0.113.40:443 (CN)', 'Connect timeout', NULL),
 (@now, 'Charlie', 'API', 'Charlie_https_https://198.51.100.31 (HK)', 'Slow response 4.2 s', NULL),
 (@now, 'Delta',  'Web', 'Delta_tcp_203.0.113.77:443 (CN)', 'Connect timeout', NULL);

DELETE FROM jkb_poll_status;
INSERT INTO jkb_poll_status (infra_name, status, last_run_at, last_success_at, alert_count, sensor_count, triggered_by, duration_seconds, error_message) VALUES
 ('Charlie', 'success', @now, @now, 3, 120, 'demo', 1.8, NULL),
 ('Delta',  'success', @now, @now, 1, 85,  'demo', 1.8, NULL);

DELETE FROM hostmonitor_alert_summary;
INSERT INTO hostmonitor_alert_summary (timestamp, alert_percentage, number_of_total_alerts, number_of_alerts_in_ltm, number_of_alerts_not_in_ltm, total_sensor_for_this_infra, infra_name, hostmonitor_ip) VALUES
 (@now, '2.5', '5', '3', '2', '200', 'charlie', '192.0.2.82'),
 (@now, '0.0', '0', '0', '0', '140', 'delta',  '192.0.2.82');

DELETE FROM hostmonitor_alert_detail;
INSERT INTO hostmonitor_alert_detail (timestamp, infra_name, in_ltm_or_not_in_ltm, alert_name, hostmonitor_ip) VALUES
 (@now, 'charlie', 'in_ltm',     'pool-web-01 ping', '192.0.2.82'),
 (@now, 'charlie', 'in_ltm',     'pool-web-02 ping', '192.0.2.82'),
 (@now, 'charlie', 'in_ltm',     'pool-api-01 tcp 443', '192.0.2.82'),
 (@now, 'charlie', 'not_in_ltm', 'oob-sw-03 ping', '192.0.2.82'),
 (@now, 'charlie', 'not_in_ltm', 'backup-nas-01 ping', '192.0.2.82');

DELETE FROM alert_for_bu_from_hm82_reports;
INSERT INTO alert_for_bu_from_hm82_reports (timestamp, bu_which_has_alert_on_hm82) VALUES
 (@now, 'Shop'), (@now, 'Payments');

SET @run = '00000000-0000-0000-0000-000000000001';

DELETE FROM hostmonitor_report_run;
INSERT INTO hostmonitor_report_run (run_id, run_at, infra_name, hostmonitor_ip, report_path, status, triggered_by, duration_seconds, report_generated_at, total_tests, alert_count, good_count, bad_count, unknown_count, ltm_test_count, not_ltm_test_count, ltm_alert_count, not_ltm_alert_count) VALUES
 (@run, @now, 'charlie', '192.0.2.82', 'demo', 'ok', 'demo', 0.5, @now, 200, 5, 195, 5, 0, 120, 80, 3, 2),
 (@run, @now, 'delta',  '192.0.2.82', 'demo', 'ok', 'demo', 0.5, @now, 140, 0, 140, 0, 0, 90, 50, 0, 0);

-- generic test rows, no domains or IPs; counts match the run rows above
DELETE FROM hostmonitor_report_test;
INSERT INTO hostmonitor_report_test (run_id, run_at, infra_name, hostmonitor_ip, folder_name, test_name, status_class, status_text, recurrences, reply, is_alert, in_ltm)
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 200)
SELECT @run, @now, 'charlie', '192.0.2.82',
       IF(i <= 120, 'Charlie\\Load balancer', 'Charlie\\Infrastructure'),
       CONCAT(IF(i <= 120, 'web-pool-', 'infra-node-'), LPAD(i, 3, '0'), ' ping'),
       IF(i IN (1,2,3,121,122), 'bad', 'good'),
       IF(i IN (1,2,3,121,122), 'Bad', 'Good'),
       IF(i IN (1,2,3,121,122), 4, 0),
       IF(i IN (1,2,3,121,122), 'Timeout', 'Reply 1 ms'),
       i IN (1,2,3,121,122), i <= 120
FROM n;
INSERT INTO hostmonitor_report_test (run_id, run_at, infra_name, hostmonitor_ip, folder_name, test_name, status_class, status_text, recurrences, reply, is_alert, in_ltm)
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 140)
SELECT @run, @now, 'delta', '192.0.2.82',
       IF(i <= 90, 'Delta\\Load balancer', 'Delta\\Infrastructure'),
       CONCAT(IF(i <= 90, 'web-pool-', 'infra-node-'), LPAD(i, 3, '0'), ' ping'),
       'good', 'Good', 0, 'Reply 1 ms', 0, i <= 90
FROM n;

DELETE FROM jkb_all_sensor_status;
INSERT INTO jkb_all_sensor_status (timestamp, task_id, task_name, task_type, status_led, belong_to_which_infra, group_name) VALUES
 (@now, '1001', 'Charlie_https_https://198.51.100.20 (CN)', 'https', '2', 'Charlie', 'Web'),
 (@now, '1002', 'Charlie_tcp_203.0.113.40:443 (CN)', 'tcp', '2', 'Charlie', 'Web'),
 (@now, '1003', 'Charlie_https_https://198.51.100.31 (HK)', 'https', '1', 'Charlie', 'API'),
 (@now, '2001', 'Delta_tcp_203.0.113.77:443 (CN)', 'tcp', '2', 'Delta', 'Web');
