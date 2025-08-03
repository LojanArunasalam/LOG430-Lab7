-- Event Store Database Schema

-- Create database if not exists
-- This will be run automatically by the Docker PostgreSQL init

-- Events table
CREATE TABLE IF NOT EXISTS stored_events (
    id SERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    aggregate_version INTEGER NOT NULL DEFAULT 1,
    event_data JSONB NOT NULL,
    metadata JSONB,
    occurred_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    stored_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    service_name VARCHAR(50)
);

-- Snapshots table
CREATE TABLE IF NOT EXISTS event_snapshots (
    id SERIAL PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_aggregate_type_id ON stored_events (aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON stored_events (event_type);
CREATE INDEX IF NOT EXISTS idx_occurred_at ON stored_events (occurred_at);
CREATE INDEX IF NOT EXISTS idx_aggregate_version ON stored_events (aggregate_type, aggregate_id, aggregate_version);
CREATE INDEX IF NOT EXISTS idx_correlation_id ON stored_events USING GIN ((metadata->>'correlation_id'));
CREATE INDEX IF NOT EXISTS idx_service_name ON stored_events (service_name);

CREATE INDEX IF NOT EXISTS idx_snapshot_aggregate ON event_snapshots (aggregate_type, aggregate_id);

-- Insert some sample data for testing (optional)
-- This demonstrates the event store structure
