import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, scoped_session

DATABASE_URL = os.getenv("DATABASE_URL")

# Create an engine with connection pooling in order to improves performance
# by reusing existing connections instead of creating new ones for each request
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


# A generator function to manage database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Queries the anomalies table to check if an event exists by event_id.
def check_event_exists(event_id):
    # Obtain a new database session from connection pool
    db: Session = next(get_db())
    result = db.execute(text("SELECT * FROM anomalies WHERE event_id = :event_id"), {"event_id": event_id}).mappings().fetchone()
    if result:
        return result['anomaly_score']
    return None


# Inserts anomaly data into the anomalies table.
def insert_anomaly(event_data, anomaly_score):
    request_id = event_data['RequestID']
    event_id = event_data['EventID']
    role_id = event_data['RoleID']
    event_type = event_data['EventType']
    event_timestamp = event_data['EventTimestamp']
    affected_assets = event_data.get('AffectedAssets', '{}')
    if affected_assets is None or affected_assets == '':
        affected_assets = '{}'
    elif isinstance(affected_assets, list):
        affected_assets = '{' + ','.join(affected_assets) + '}'

    # Obtain a new database session from connection pool
    db: Session = next(get_db())
    db.execute(text("INSERT INTO anomalies (request_id, event_id, role_id, event_type, event_timestamp, affected_assets, anomaly_score) VALUES "
                        "(:request_id, :event_id, :role_id, :event_type, :event_timestamp, :affected_assets, :anomaly_score)"),
                   {"request_id": request_id, "event_id": event_id, "role_id": role_id, "event_type": event_type, "event_timestamp": event_timestamp, "affected_assets": affected_assets, "anomaly_score": anomaly_score})
    # Commits the current transaction, making all changes permanent in the database
    db.commit()

