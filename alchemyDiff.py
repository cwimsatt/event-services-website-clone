
import os
from sqlalchemy_diff import compare
from sqlalchemy import create_engine
from models import Base
from extensions import db

# Connect to the database
dburl = os.getenv('DATABASE_URL')
engine = create_engine(dburl)

# Compare the models' metadata with the database schema
diff = compare(Base.metadata, engine)

if diff:
    print("Schema differences found:")
    print(diff)
else:
    print("No schema differences found")
