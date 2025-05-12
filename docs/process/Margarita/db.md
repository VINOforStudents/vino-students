# Table of Contents



# Introduction

I began by testing the connection to the database:

```py
# Standard library imports
import os

# Database imports
import psycopg2


db_info = os.getenv("DB_INFO")
if not db_info:
    raise ValueError("Database not found. Please set the DB_INFO environment variable.")

conn = psycopg2.connect(db_info)
cur = conn.cursor()
#------------------------------------------------------------------------------
cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
cur.fetchone()
conn.commit()

cur.close()
conn.close()
```

As a result, I got a new table with a record in it. Later, I deleted that table since it was just for testing.