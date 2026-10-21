"""Load db/schema.sql and db/seed_demo_data.sql into the database in DATABASE_URL."""
import os
import sys
import time

import pymysql
from pymysql.constants import CLIENT
from sqlalchemy.engine import make_url

url = make_url(os.environ["DATABASE_URL"])
here = os.path.dirname(os.path.abspath(__file__))

for attempt in range(60):
    try:
        conn = pymysql.connect(
            host=url.host, port=url.port or 3306, user=url.username,
            password=url.password, database=url.database,
            client_flag=CLIENT.MULTI_STATEMENTS, autocommit=True,
        )
        break
    except pymysql.err.OperationalError as error:
        print(f"waiting for the database ({error.args[0]})", file=sys.stderr)
        time.sleep(2)
else:
    sys.exit("database never became reachable")

with conn.cursor() as cur:
    for name in ("schema.sql", "seed_demo_data.sql"):
        with open(os.path.join(here, "db", name), encoding="utf-8") as handle:
            cur.execute(handle.read())
        while cur.nextset():
            pass
        print(f"loaded {name}")
conn.close()
