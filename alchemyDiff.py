
from sqlalchemy_diff import compare
from sqlalchemy import create_engine
from models import Base  # Import your SQLAlchemy models (ensure they use Base.metadata)

# Connect to the database
engine = create_engine('postgresql://user:password@localhost/dbname')

# Compare the models' metadata with the database schema
diff = compare(Base.metadata, engine)
print(diff)
