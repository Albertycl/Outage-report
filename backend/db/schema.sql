/*M!999999\- enable the sandbox mode */ 

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;
DROP TABLE IF EXISTS `alert_for_bu_from_hm82_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alert_for_bu_from_hm82_reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `bu_which_has_alert_on_hm82` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_alert_for_bu_from_hm82_reports_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `hostmonitor_alert_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hostmonitor_alert_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `infra_name` varchar(255) DEFAULT NULL,
  `in_ltm_or_not_in_ltm` varchar(255) DEFAULT NULL,
  `alert_name` varchar(255) DEFAULT NULL,
  `hostmonitor_ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11281 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `hostmonitor_alert_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hostmonitor_alert_summary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `alert_percentage` varchar(255) DEFAULT NULL,
  `number_of_total_alerts` varchar(255) DEFAULT NULL,
  `number_of_alerts_in_ltm` varchar(255) DEFAULT NULL,
  `number_of_alerts_not_in_ltm` varchar(255) DEFAULT NULL,
  `total_sensor_for_this_infra` varchar(255) DEFAULT NULL,
  `infra_name` varchar(255) DEFAULT NULL,
  `hostmonitor_ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5777 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `hostmonitor_report_run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hostmonitor_report_run` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` varchar(36) DEFAULT NULL,
  `run_at` datetime DEFAULT NULL,
  `infra_name` varchar(255) DEFAULT NULL,
  `hostmonitor_ip` varchar(255) DEFAULT NULL,
  `report_path` varchar(512) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `triggered_by` varchar(32) DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL,
  `report_generated_at` datetime DEFAULT NULL,
  `total_tests` int(11) DEFAULT NULL,
  `alert_count` int(11) DEFAULT NULL,
  `good_count` int(11) DEFAULT NULL,
  `bad_count` int(11) DEFAULT NULL,
  `unknown_count` int(11) DEFAULT NULL,
  `error_message` varchar(1024) DEFAULT NULL,
  `ltm_test_count` int(11) DEFAULT NULL,
  `not_ltm_test_count` int(11) DEFAULT NULL,
  `ltm_alert_count` int(11) DEFAULT NULL,
  `not_ltm_alert_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_hostmonitor_report_run_run_id` (`run_id`),
  KEY `ix_hostmonitor_report_run_run_at` (`run_at`),
  KEY `ix_hostmonitor_report_run_infra_name` (`infra_name`),
  KEY `ix_hostmonitor_report_run_hostmonitor_ip` (`hostmonitor_ip`)
) ENGINE=InnoDB AUTO_INCREMENT=5779 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `hostmonitor_report_test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hostmonitor_report_test` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` varchar(36) DEFAULT NULL,
  `run_at` datetime DEFAULT NULL,
  `infra_name` varchar(255) DEFAULT NULL,
  `hostmonitor_ip` varchar(255) DEFAULT NULL,
  `folder_name` varchar(255) DEFAULT NULL,
  `test_name` varchar(512) DEFAULT NULL,
  `status_class` varchar(32) DEFAULT NULL,
  `status_text` varchar(255) DEFAULT NULL,
  `recurrences` int(11) DEFAULT NULL,
  `reply` varchar(512) DEFAULT NULL,
  `is_alert` tinyint(1) DEFAULT NULL,
  `in_ltm` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_hostmonitor_report_test_run_id` (`run_id`),
  KEY `ix_hostmonitor_report_test_run_at` (`run_at`),
  KEY `ix_hostmonitor_report_test_infra_name` (`infra_name`),
  KEY `ix_hostmonitor_report_test_folder_name` (`folder_name`),
  KEY `ix_hostmonitor_report_test_status_class` (`status_class`),
  KEY `ix_hostmonitor_report_test_in_ltm` (`in_ltm`)
) ENGINE=InnoDB AUTO_INCREMENT=534358 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `jkb_alert_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jkb_alert_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `infra_name` varchar(50) NOT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `task_name` varchar(500) DEFAULT NULL,
  `task_summary` varchar(500) DEFAULT NULL,
  `link_for_snapshot` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_jkb_alert_details_group_name` (`group_name`),
  KEY `ix_jkb_alert_details_infra_name` (`infra_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3895 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `jkb_all_sensor_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jkb_all_sensor_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `task_id` varchar(255) DEFAULT NULL,
  `task_name` varchar(255) DEFAULT NULL,
  `task_summary` varchar(500) DEFAULT NULL,
  `task_type` varchar(255) DEFAULT NULL,
  `group_id` varchar(255) DEFAULT NULL,
  `monitor_target` varchar(255) DEFAULT NULL,
  `paused_or_started` varchar(255) DEFAULT NULL,
  `two_means_hit_threshold` varchar(255) DEFAULT NULL,
  `status_led` varchar(255) DEFAULT NULL,
  `status_led_str` varchar(255) DEFAULT NULL,
  `last_resp_status` varchar(255) DEFAULT NULL,
  `last_resp_result` varchar(255) DEFAULT NULL,
  `last_resp_time` varchar(255) DEFAULT NULL,
  `last_check_time` varchar(255) DEFAULT NULL,
  `last_check_time_readable` datetime DEFAULT NULL,
  `last_monitor_count` varchar(255) DEFAULT NULL,
  `last_monitor_abnormal_count` varchar(255) DEFAULT NULL,
  `partition_flag` varchar(255) DEFAULT NULL,
  `frequency` varchar(255) DEFAULT NULL,
  `network_protocol` varchar(255) DEFAULT NULL,
  `link_for_snapshot` varchar(500) DEFAULT NULL,
  `group_name` varchar(255) DEFAULT NULL,
  `monitor_target_ip` varchar(255) DEFAULT NULL,
  `belong_to_which_infra` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_jkb_all_sensor_status_status_led` (`status_led`),
  KEY `ix_jkb_all_sensor_status_group_id` (`group_id`),
  KEY `ix_jkb_all_sensor_status_timestamp` (`timestamp`),
  KEY `ix_jkb_all_sensor_status_task_id` (`task_id`),
  KEY `ix_jkb_all_sensor_status_belong_to_which_infra` (`belong_to_which_infra`),
  KEY `ix_jkb_all_sensor_status_group_name` (`group_name`)
) ENGINE=InnoDB AUTO_INCREMENT=48160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `jkb_infra_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jkb_infra_summary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `infra_name` varchar(50) NOT NULL,
  `alert_count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_jkb_infra_summary_timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=3997 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `jkb_poll_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jkb_poll_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` varchar(36) DEFAULT NULL,
  `run_at` datetime DEFAULT NULL,
  `step` varchar(64) DEFAULT NULL,
  `step_order` int(11) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `http_status_code` int(11) DEFAULT NULL,
  `run_http_status_code` int(11) DEFAULT NULL,
  `triggered_by` varchar(32) DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL,
  `detail` varchar(512) DEFAULT NULL,
  `error_message` varchar(1024) DEFAULT NULL,
  `alert_count_by_infra` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_jkb_poll_history_run_id` (`run_id`),
  KEY `ix_jkb_poll_history_run_at` (`run_at`),
  KEY `ix_jkb_poll_history_step` (`step`)
) ENGINE=InnoDB AUTO_INCREMENT=6052 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `jkb_poll_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jkb_poll_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `infra_name` varchar(255) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `last_run_at` datetime DEFAULT NULL,
  `last_success_at` datetime DEFAULT NULL,
  `alert_count` int(11) DEFAULT NULL,
  `sensor_count` int(11) DEFAULT NULL,
  `triggered_by` varchar(32) DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL,
  `error_message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_jkb_poll_status_infra_name` (`infra_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `monitor_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monitor_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` varchar(255) DEFAULT NULL,
  `group_name` varchar(255) DEFAULT NULL,
  `convert_to_the_name_i_want_to_show_in_frontend` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_monitor_group_group_id` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11929 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `pagerduty_poll_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pagerduty_poll_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` varchar(36) DEFAULT NULL,
  `run_at` datetime DEFAULT NULL,
  `infra_name` varchar(255) DEFAULT NULL,
  `service_id` varchar(64) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `http_status_code` int(11) DEFAULT NULL,
  `alert_count` int(11) DEFAULT NULL,
  `triggered_by` varchar(32) DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL,
  `error_message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_pagerduty_poll_history_infra_name` (`infra_name`),
  KEY `ix_pagerduty_poll_history_run_at` (`run_at`),
  KEY `ix_pagerduty_poll_history_run_id` (`run_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6013 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `pagerduty_poll_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pagerduty_poll_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `infra_name` varchar(255) DEFAULT NULL,
  `service_id` varchar(64) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `last_run_at` datetime DEFAULT NULL,
  `last_success_at` datetime DEFAULT NULL,
  `alert_count` int(11) DEFAULT NULL,
  `triggered_by` varchar(32) DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL,
  `error_message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_pagerduty_poll_status_infra_name` (`infra_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `prtg_alert_current`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prtg_alert_current` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(2550) DEFAULT NULL,
  `sensor_id` varchar(255) DEFAULT NULL,
  `whicih_infra` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6507 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `prtg_current_settings_v2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prtg_current_settings_v2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `infra_name` varchar(50) NOT NULL,
  `device_id` int(11) NOT NULL,
  `sensor_id` int(11) NOT NULL,
  `sensor_name` varchar(255) DEFAULT NULL,
  `device_name` varchar(255) DEFAULT NULL,
  `sub_id` int(11) NOT NULL,
  `trigger_type` varchar(50) DEFAULT NULL,
  `current_trigger_notification_id` varchar(1024) DEFAULT NULL,
  `current_recovery_notification_id` varchar(1024) DEFAULT NULL,
  `current_channel` varchar(255) DEFAULT NULL,
  `current_condition` varchar(100) DEFAULT NULL,
  `current_threshold` varchar(100) DEFAULT NULL,
  `current_latency` varchar(50) DEFAULT NULL,
  `current_unitsize` varchar(50) DEFAULT NULL,
  `current_unittime` varchar(50) DEFAULT NULL,
  `current_period` varchar(50) DEFAULT NULL,
  `current_changetype` varchar(50) DEFAULT NULL,
  `original_trigger_json` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_prtg_current_settings_v2_device_id` (`device_id`),
  KEY `ix_prtg_current_settings_v2_infra_name` (`infra_name`),
  KEY `ix_prtg_current_settings_v2_sensor_id` (`sensor_id`),
  KEY `ix_prtg_current_settings_v2_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `prtg_summary_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prtg_summary_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `infra_name` varchar(255) DEFAULT NULL,
  `sensor_id` int(11) DEFAULT NULL,
  `lastvalue` varchar(64) DEFAULT NULL,
  `down_count` int(11) DEFAULT NULL,
  `prtg_link` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;


-- Stamp the schema at the revision the dev database is on, so a later
-- `flask db upgrade` sees an up-to-date database and is a no-op rather than
-- trying to replay the whole chain (which currently fails).
