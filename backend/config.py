import os

# Concept demo: no credentials, no URLs of real systems. Everything the app
# shows comes from the database, which db/seed_demo_data.sql fills with
# made-up numbers.

# The two example infrastructures the demo reports on. Names are made up.
INFRAS = {
    'charlie': {'jkb_name': 'Charlie'},
    'delta': {'jkb_name': 'Delta'},
}
INFRA_NAMES = list(INFRAS)
JKB_INFRA_NAMES = [each['jkb_name'] for each in INFRAS.values()]


def _minutes(name, default):
    return int(os.environ.get(name, default))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    INFRAS = INFRAS
    INFRA_NAMES = INFRA_NAMES
    JKB_INFRA_NAMES = JKB_INFRA_NAMES

    # The health endpoints return 503 when the data is older than this.
    # demo_mode.py re-stamps the seeded rows on every Refresh click.
    JKB_MAX_DATA_AGE_MINUTES = _minutes('JKB_MAX_DATA_AGE_MINUTES', 10)
    JKB_POLL_INTERVAL_MINUTES = _minutes('JKB_POLL_INTERVAL_MINUTES', 1)
    JKB_HISTORY_RETENTION_DAYS = _minutes('JKB_HISTORY_RETENTION_DAYS', 7)
    JKB_SCHEDULER_ENABLED = False

    PAGERDUTY_MAX_DATA_AGE_MINUTES = _minutes('PAGERDUTY_MAX_DATA_AGE_MINUTES', 10)
    PAGERDUTY_POLL_INTERVAL_MINUTES = _minutes('PAGERDUTY_POLL_INTERVAL_MINUTES', 1)
    PAGERDUTY_HISTORY_RETENTION_DAYS = _minutes('PAGERDUTY_HISTORY_RETENTION_DAYS', 7)
    PAGERDUTY_SCHEDULER_ENABLED = False

    HOSTMONITOR_REPORT_IP = '192.0.2.82'  # documentation range, not a real host
    HOSTMONITOR_REPORT_MAX_DATA_AGE_MINUTES = _minutes('HOSTMONITOR_REPORT_MAX_DATA_AGE_MINUTES', 10)
    HOSTMONITOR_REPORT_POLL_INTERVAL_MINUTES = _minutes('HOSTMONITOR_REPORT_POLL_INTERVAL_MINUTES', 1)
    HOSTMONITOR_REPORT_HISTORY_RETENTION_DAYS = _minutes('HOSTMONITOR_REPORT_HISTORY_RETENTION_DAYS', 7)


class ProdConfig(Config):
    DEBUG = False


class DevConfig(Config):
    DEBUG = True


config = {
    'development': DevConfig,
    'production': ProdConfig,
    'default': DevConfig,
}
