"""Convert sequence values from integer to float

Revision ID: 2024_12_05_convert_seq
Revises: 2024_12_05_fix_sequence
Create Date: 2024-12-05 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '2024_12_05_convert_seq'
down_revision = '2024_12_05_fix_sequence'
branch_labels = None
depends_on = None

def upgrade():
    # Convert existing integer sequences to float
    connection = op.get_bind()
    
    # Get all events with non-null sequences
    events = connection.execute(
        text("SELECT id, sequence FROM event WHERE sequence IS NOT NULL")
    ).fetchall()
    
    # Update each event's sequence to float
    for event in events:
        connection.execute(
            text("UPDATE event SET sequence = :new_sequence WHERE id = :event_id"),
            {"new_sequence": float(event.sequence), "event_id": event.id}
        )

def downgrade():
    # Convert float sequences back to integer
    connection = op.get_bind()
    
    # Get all events with non-null sequences
    events = connection.execute(
        text("SELECT id, sequence FROM event WHERE sequence IS NOT NULL")
    ).fetchall()
    
    # Update each event's sequence back to integer
    for event in events:
        connection.execute(
            text("UPDATE event SET sequence = :new_sequence WHERE id = :event_id"),
            {"new_sequence": int(float(event.sequence)), "event_id": event.id}
        )
