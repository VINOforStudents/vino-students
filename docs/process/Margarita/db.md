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


After that, I decided to work on document processing function. The goal is to take files that are currently in ```../../kb_new/```, get their metadata and extract text and then upload them to the database that I created. 

I had to change the metadata that is passed through after processing the document and I got rid of chunking for now for simplicity:

```py
metadata = DocumentMetadata(file_name=file_name,
                            file_size=file_size,
                            file_type=file_name.split('.')[-1],
                            page_count=0,  # Placeholder for page count
                            word_count=word_count,
                            char_count=char_count,
                            keywords=[],  # Placeholder for keywords
                            source="system_upload"
                            abstract="", # Placeholder for abstract
                            ).model_dump() 
```

A lot of it is placeholders just to make prototyping faster.
Had to do some bug fixing related to names and class' attributes, but I got the desired output:

```PS D:\GitHub\vino-students> & D:/GitHub/vino-students/.venv/Scripts/python.exe d:/GitHub/vino-students/sql_upload.py
[{'file_name': 'DoT.pdf', 'file_size': 79797, 'file_type': 'pdf', 'page_count': 0, 'word_count': 1018, 'char_count': 3580, 'keywords': [], 'source': 'system_upload', 'abstract': ''}]```

Now I can try to put all this data to the database, along with uploading plain text to a dedicated table.