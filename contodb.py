"""
This module connects to the SQL database on local machine. 
"""

import psycopg2
import os

dbname = 'Reddit'
host = 'localhost'
port = '5432'
user = 'mrr-phys' # os.environ["SQL_USERNAME"]
password = '' # os.environ["SQL_PASSWORD"]

con = psycopg2.connect(
   database = dbname,
   user = user,
   password = password,
   host = host,
   port = port
)