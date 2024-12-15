import os
from re import M
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine,inspect
from models import db


dbURL = os.environ.get('DATABASE_URL')
# Connect to the database
dbengine = create_engine(dbURL)
db_inspect = inspect(dbengine)
db_tables = set(db_inspect.get_table_names())
orm_tables = set(db.metadata.tables.keys())
db_xtra_tables = db_tables - orm_tables
db_missing_tables = orm_tables - db_tables
for table_name in orm_tables.intersection(db_tables):
  db_cols = {col["name"] for col in db_inspect.get_columns(table_name)}
  orm_cols = set(db.metadata.tables[table_name].columns.keys()) 
  missing_cols = orm_cols - db_cols
  extra_cols = db_cols - orm_cols 
  if missing_cols:
    print(f"Table {table_name} is missing columns: {', '.join(missing_cols)}")
  if extra_cols:
    print(f"Table {table_name} has extra columns: {', '.join(extra_cols)}")
    
              
if db_xtra_tables:
  print("The following tables are present in the database but not in the ORM:")
  for table_name in db_xtra_tables:
    print(table_name)
if db_missing_tables:
  print("The following tables are present in the ORM but not in the database:")
  for table_name in db_missing_tables:
    print(table_name)
else: 
  print("no extra tables in the ORM")  