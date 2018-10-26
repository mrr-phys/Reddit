
"""
This module creates the Postgres database if it doesn't exist. 
"""

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

dbname = 'Reddit'
username = 'mrr-phys'

engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

if database_exists(engine.url):
	create_database(engine.url)
print(database_exists(engine.url))