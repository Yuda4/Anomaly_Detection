-- Create anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    role_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_timestamp timestamptz NOT NULL,
    affected_assets TEXT[] NOT NULL,
    anomaly_score FLOAT
    );