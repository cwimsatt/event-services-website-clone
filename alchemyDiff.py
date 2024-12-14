from os import getenv
from sqlalchemydiff import compare
from sqlalchemy import create_engine
from models import metadata
import os
from sqlalchemy import create_engine

# Connect to the database
dburl = os.getenv('DATABASE_URL')
engine = create_engine(dburl)

# Compare the models' metadata with the database schema
diff = compare(Base.metadata, engine)
print(diff)